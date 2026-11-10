// Cindy Flow Bridge v1.3.0 — Background Service Worker

function isStudioUrl(url) {
  if (!url) return false;
  return url.startsWith('http://127.0.0.1:8765') || url.startsWith('http://localhost:8765');
}

function isFlowTab(tab) {
  if (!tab || !tab.url) return false;
  const u = tab.url.toLowerCase();
  const title = (tab.title || '').toLowerCase();
  return (
    u.includes('flow.google') ||
    u.includes('labs.google') ||
    u.includes('aitestkitchen') ||
    (u.includes('google.') && (
      title.includes('flow') ||
      title.includes('veo') ||
      u.includes('/fx') ||
      u.includes('/flow') ||
      u.includes('video-fx')
    ))
  );
}

// Auto-inject content scripts into already-open tabs whenever the extension starts or reloads
async function injectIntoExistingTabs() {
  try {
    const tabs = await chrome.tabs.query({});
    for (const tab of tabs) {
      if (!tab.id || !tab.url) continue;
      if (isStudioUrl(tab.url)) {
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content_cindy.js']
        }).catch(() => {});
      } else if (isFlowTab(tab)) {
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content_flow.js']
        }).catch(() => {});
      }
    }
  } catch (e) {
    console.warn('[Cindy Flow Bridge] injectIntoExistingTabs warning:', e);
  }
}

chrome.runtime.onInstalled.addListener(() => {
  injectIntoExistingTabs();
});

// Also run immediately when service worker wakes up
injectIntoExistingTabs();

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message) return false;

  if (message.action === 'CINDY_CHECK_DEBUGGER') {
    const hasDbg = Boolean(typeof chrome !== 'undefined' && chrome.debugger);
    sendResponse({ hasDbg });
    return false;
  }

  if (message.action === 'CINDY_RELOAD_EXT') {
    sendResponse({ reloading: true });
    setTimeout(() => { chrome.runtime.reload(); }, 100);
    return true;
  }

  if (message.action === 'CINDY_DISPATCH_TRUSTED_CLICK') {
    (async () => {
      const tabId = (sender.tab && sender.tab.id) ? sender.tab.id : null;
      if (!tabId) {
        sendResponse({ success: false, error: 'No sender tab' });
        return;
      }
      const res = await dispatchTrustedClick(tabId, message.selector || 'button[type="submit"]');
      sendResponse(res);
    })();
    return true;
  }

  if (message.action === 'CINDY_TASK_DISPATCH_V2' || message.action === 'CINDY_TASK_DISPATCH') {
    handleTaskDispatch(message.task).then(res => sendResponse(res));
    return true;
  }

  if (message.action === 'CINDY_SYNC_FLOW') {
    handleSyncFlow(message.preferType).then(res => sendResponse(res));
    return true;
  }

  if (message.action === 'CINDY_DEBUG') {
    fetch('http://127.0.0.1:8765/api/bridge/debug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message.report)
    }).catch(() => {});
    return false;
  }

  if (message.action === 'FLOW_MEDIA_READY') {
    handleMediaReady(message.media).then(res => sendResponse(res));
    return true;
  }
});

let lastDispatchedTaskId = '';
let lastDispatchPromise = null;

async function handleTaskDispatch(task) {
  if (!task) return { success: false, error: 'Task payload is empty' };
  if (task.id && task.id === lastDispatchedTaskId && lastDispatchPromise) {
    return await lastDispatchPromise;
  }
  if (task.id) lastDispatchedTaskId = task.id;
  lastDispatchPromise = _doTaskDispatch(task);
  return await lastDispatchPromise;
}

async function dispatchTrustedClick(tabId, selector) {
  try {
    const [{ result: coords }] = await chrome.scripting.executeScript({
      target: { tabId },
      func: (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        return { x: Math.round(rect.left + rect.width / 2), y: Math.round(rect.top + rect.height / 2) };
      },
      args: [selector]
    });
    if (!coords || !coords.x) return { success: false, error: 'Target element not found: ' + selector };

    if (!chrome.debugger) {
      return { success: false, noDebugger: true, error: 'chrome.debugger API not available in worker' };
    }

    await chrome.debugger.attach({ tabId }, '1.3');
    try {
      await chrome.debugger.sendCommand({ tabId }, 'Input.dispatchMouseEvent', {
        type: 'mousePressed',
        x: coords.x,
        y: coords.y,
        button: 'left',
        clickCount: 1
      });
      await new Promise(r => setTimeout(r, 60));
      await chrome.debugger.sendCommand({ tabId }, 'Input.dispatchMouseEvent', {
        type: 'mouseReleased',
        x: coords.x,
        y: coords.y,
        button: 'left',
        clickCount: 1
      });
      // Also send Enter key as backup
      await chrome.debugger.sendCommand({ tabId }, 'Input.dispatchKeyEvent', {
        type: 'rawKeyDown',
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
        key: 'Enter',
        code: 'Enter'
      });
      await new Promise(r => setTimeout(r, 60));
      await chrome.debugger.sendCommand({ tabId }, 'Input.dispatchKeyEvent', {
        type: 'keyUp',
        windowsVirtualKeyCode: 13,
        nativeVirtualKeyCode: 13,
        key: 'Enter',
        code: 'Enter'
      });
    } finally {
      await chrome.debugger.detach({ tabId }).catch(() => {});
    }
    return { success: true };
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

async function _doTaskDispatch(task) {
  const tabs = await chrome.tabs.query({});
  const flowTab = tabs.find(isFlowTab);

  if (!flowTab) {
    return {
      success: false,
      noTab: true,
      error: 'لم يتم العثور على تبويب Google Flow مفتوح في المتصفح.'
    };
  }

  if (task.diagDebugger) {
    const dbgAvail = Boolean(chrome.debugger);
    let attachErr = null;
    if (dbgAvail) {
      try {
        await chrome.debugger.attach({ tabId: flowTab.id }, '1.3');
        await chrome.debugger.detach({ tabId: flowTab.id }).catch(() => {});
      } catch (e) {
        attachErr = String(e);
      }
    }
    return { success: true, dbgAvail, attachErr, tabId: flowTab.id };
  }

  try {
    // Always ensure content_flow.js is injected in the target tab before messaging
    try {
      await chrome.scripting.executeScript({
        target: { tabId: flowTab.id },
        files: ['content_flow.js']
      });
    } catch (injectErr) {}

    const response = await chrome.tabs.sendMessage(flowTab.id, {
      action: 'INJECT_AND_GENERATE_V2',
      task: task
    });
    return response || { success: true, message: 'تم إرسال الأمر لصفحة Google Flow' };
  } catch (err) {
    return { success: false, error: 'تعذر الاتصال بصفحة Google Flow: ' + err.message };
  }
}

async function handleSyncFlow(preferType) {
  const tabs = await chrome.tabs.query({});
  const flowTab = tabs.find(isFlowTab);
  if (!flowTab) {
    return { success: false, error: 'لم يتم العثور على تبويب Google Flow مفتوح.' };
  }
  try {
    try {
      await chrome.scripting.executeScript({ target: { tabId: flowTab.id }, files: ['content_flow.js'] });
    } catch (e) {}
    const res = await chrome.tabs.sendMessage(flowTab.id, { action: 'SYNC_FLOW_MEDIA', preferType: preferType });
    return res || { success: false, error: 'لم ترد صفحة Flow.' };
  } catch (err) {
    return { success: false, error: err.message };
  }
}

async function handleMediaReady(media) {
  let savedMedia = media;
  try {
    const res = await fetch('http://127.0.0.1:8765/api/bridge/complete_task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(media)
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.media) savedMedia = data.media;
    }
  } catch (e) {}

  const tabs = await chrome.tabs.query({});
  const cindyTabs = tabs.filter(t => t.url && isStudioUrl(t.url));

  for (const cTab of cindyTabs) {
    try {
      await chrome.tabs.sendMessage(cTab.id, {
        action: 'CINDY_FLOW_COMPLETED',
        media: savedMedia
      });
    } catch (e) {}
  }

  return { success: true };
}

// Secondary HTTP Bridge Polling: picks up tasks from local Cindy Server even if content_cindy.js was not refreshed
setInterval(async () => {
  try {
    const tabs = await chrome.tabs.query({});
    const hasFlow = tabs.some(isFlowTab);
    const res = await fetch('http://127.0.0.1:8765/api/bridge/poll?flow_open=' + (hasFlow ? '1' : '0'));
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.task) {
      const dispatchRes = await handleTaskDispatch(data.task);
      await fetch('http://127.0.0.1:8765/api/bridge/ack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: data.task.id, result: dispatchRes })
      }).catch(() => {});
    }
  } catch (e) {}
}, 1500);
