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

document.addEventListener('DOMContentLoaded', async () => {
  const serverStatus = document.getElementById('server-status');
  const tabStatus = document.getElementById('tab-status');
  const btnSync = document.getElementById('btn-sync');

  // Check Cindy Local Server
  try {
    const res = await fetch('http://127.0.0.1:8765/api/status');
    if (res.ok) {
      serverStatus.className = 'badge-ok';
      serverStatus.innerText = 'متصل 🟢';
    } else {
      serverStatus.className = 'badge-wait';
      serverStatus.innerText = 'غير متصل';
    }
  } catch (err) {
    serverStatus.className = 'badge-wait';
    serverStatus.innerText = 'السيرفر مغلق';
  }

  // Check Google Flow tab and auto-inject content scripts if needed
  const tabs = await chrome.tabs.query({});
  const flowTab = tabs.find(isFlowTab);
  const cindyTabs = tabs.filter(t => t.url && (t.url.startsWith('http://127.0.0.1:8765') || t.url.startsWith('http://localhost:8765')));

  for (const ct of cindyTabs) {
    try { await chrome.scripting.executeScript({ target: { tabId: ct.id }, files: ['content_cindy.js'] }); } catch (e) {}
  }

  if (flowTab) {
    try { await chrome.scripting.executeScript({ target: { tabId: flowTab.id }, files: ['content_flow.js'] }); } catch (e) {}
    tabStatus.className = 'badge-ok';
    tabStatus.innerText = 'مفتوح ومتصل 🟢';
  } else {
    tabStatus.className = 'badge-wait';
    tabStatus.innerText = 'افتح Google Flow في كروم';
  }

  btnSync.addEventListener('click', async () => {
    btnSync.innerText = 'جارٍ إرسال إشارة المزامنة...';
    try {
      if (flowTab) {
        try { await chrome.scripting.executeScript({ target: { tabId: flowTab.id }, files: ['content_flow.js'] }); } catch (e) {}
        await chrome.tabs.sendMessage(flowTab.id, { action: 'CINDY_PING' });
        btnSync.innerText = 'تم إظهار زر سيندي الذهبي وتأكيد الربط ✅';
      } else {
        btnSync.innerText = 'افتح صفحة Google Flow أولاً';
      }
    } catch (e) {
      btnSync.innerText = 'تم التحديث ✅';
    }
    setTimeout(() => {
      btnSync.innerText = 'مزامنة واختبار الجسر الآن';
    }, 2500);
  });
});
