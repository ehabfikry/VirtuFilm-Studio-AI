// Cindy Flow Bridge v1.3.0 — Content Script for Cindy Studio

(function() {
  const BRIDGE_VERSION = '1.3.0';

  function isContextAlive() {
    try {
      return Boolean(typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id);
    } catch (e) {
      return false;
    }
  }

  if (!isContextAlive()) return;

  console.log('[Cindy Flow Bridge v' + BRIDGE_VERSION + '] Initialized on Studio page.');
  window.__CINDY_BRIDGE_ACTIVE__ = true;
  window.__CINDY_BRIDGE_VERSION__ = BRIDGE_VERSION;

  function announceBridge() {
    if (!isContextAlive()) return;
    window.postMessage({ type: 'CINDY_BRIDGE_STATUS', active: true, version: BRIDGE_VERSION }, '*');
    const badge = document.getElementById('google-flow-bridge-badge');
    if (badge) {
      const isEn = (window.currentAppLang && window.currentAppLang !== 'ar');
      const flowText = isEn ? 'Flow Active 🟢' : 'جسر فلو متصل 🟢';
      badge.innerHTML = `<i class="fa-solid fa-link text-emerald-400 text-[10px]"></i> <span class="text-emerald-300 font-bold">${flowText}</span>`;
      badge.className = 'cursor-pointer px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-md text-[10px] font-bold flex items-center gap-1 shadow transition';
    }
  }

  window.addEventListener('message', async (event) => {
    if (!isContextAlive()) return;
    if (event.source !== window || !event.data) return;

    if (event.data.type === 'CINDY_EXECUTE_FLOW_V2' || event.data.type === 'CINDY_EXECUTE_FLOW') {
      const task = event.data.task;
      console.log('[Cindy Flow Bridge v1.3] Dispatching task:', task);
      try {
        const response = await chrome.runtime.sendMessage({
          action: 'CINDY_TASK_DISPATCH_V2',
          task: task
        });
        window.postMessage({
          type: 'CINDY_FLOW_DISPATCH_ACK',
          task: task,
          response: response || { success: false, error: 'لم ترد إضافة الجسر.' }
        }, '*');
      } catch (err) {
        // If context was invalidated mid-call, let the HTTP bridge fallback in index.html handle it cleanly
        console.warn('[Cindy Flow Bridge] sendMessage error:', err);
      }
    }

    if (event.data.type === 'CINDY_SYNC_FLOW_NOW') {
      try {
        const res = await chrome.runtime.sendMessage({
          action: 'CINDY_SYNC_FLOW',
          preferType: event.data.preferType || 'image'
        });
        window.postMessage({ type: 'CINDY_SYNC_FLOW_ACK', response: res }, '*');
      } catch (err) {
        window.postMessage({ type: 'CINDY_SYNC_FLOW_ACK', response: { success: false, error: err.message } }, '*');
      }
    }
  });

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!isContextAlive() || !message) return false;
    if (message.action === 'CINDY_FLOW_COMPLETED') {
      console.log('[Cindy Flow Bridge v1.3] Media completed in Google Flow:', message.media);
      window.postMessage({
        type: 'CINDY_FLOW_RESULT',
        media: message.media
      }, '*');
      sendResponse({ received: true });
    }
    return true;
  });

  const timer = setInterval(() => {
    if (!isContextAlive()) {
      clearInterval(timer);
      return;
    }
    announceBridge();
  }, 2000);
  setTimeout(announceBridge, 200);
})();
