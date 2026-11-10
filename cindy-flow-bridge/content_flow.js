// Cindy Flow Bridge v1.3.1 — Content Script for Google Flow (flow.google.com / labs.google)
// 100% TrustedTypes-compliant (Zero .innerHTML assignments)

(function() {
  function isContextAlive() {
    try {
      return Boolean(typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id);
    } catch (e) {
      return false;
    }
  }

  function isGoogleFlowPage() {
    const u = (location.href || '').toLowerCase();
    const t = (document.title || '').toLowerCase();
    return (
      u.includes('flow.google') ||
      u.includes('labs.google') ||
      u.includes('aitestkitchen') ||
      u.includes('/fx') ||
      u.includes('/flow') ||
      u.includes('video-fx') ||
      t.includes('flow') ||
      t.includes('veo')
    );
  }

  if (!isGoogleFlowPage()) return;

  // Build Golden Cindy Badge using pure DOM nodes (TrustedTypes / CSP safe — NO innerHTML!)
  function renderDefaultBadgeContent(badge) {
    while (badge.firstChild) badge.removeChild(badge.firstChild);

    const row = document.createElement('div');
    row.style.cssText = 'display:flex; align-items:center; gap:10px;';

    const iconBox = document.createElement('div');
    iconBox.style.cssText = 'width:32px; height:32px; border-radius:9px; background:linear-gradient(135deg,#e6af2e,#b45309); display:flex; align-items:center; justify-content:center; font-size:16px; box-shadow:0 0 12px rgba(230,175,46,0.45);';
    iconBox.textContent = '🎬';

    const textCol = document.createElement('div');
    textCol.style.cssText = 'flex:1;';

    const titleEl = document.createElement('div');
    titleEl.style.cssText = 'font-weight:800; font-size:12px; color:#e6af2e; letter-spacing:0.2px;';
    titleEl.textContent = 'سيندي | Cindy Flow Bridge';

    const subEl = document.createElement('div');
    subEl.id = 'cindy-flow-badge-sub';
    subEl.style.cssText = 'font-size:10px; color:#34d399; margin-top:1px;';
    subEl.textContent = 'متصل بحسابك 🟢 — جاهز لتوليد الصور والفيديو';

    textCol.appendChild(titleEl);
    textCol.appendChild(subEl);

    const sendBtn = document.createElement('button');
    sendBtn.id = 'cindy-flow-send-btn';
    sendBtn.type = 'button';
    sendBtn.title = 'إرسال اللقطات المعروضة حالياً إلى شاشة سيندي';
    sendBtn.style.cssText = 'background:rgba(230,175,46,0.18); border:1px solid rgba(230,175,46,0.55); color:#fde68a; border-radius:8px; padding:5px 9px; font-size:10px; font-weight:bold; cursor:pointer; white-space:nowrap;';
    sendBtn.textContent = '📥 إرسال لسيندي';
    sendBtn.onclick = (e) => {
      e.stopPropagation();
      syncCurrentFlowMediaToCindy('auto');
    };

    row.appendChild(iconBox);
    row.appendChild(textCol);
    row.appendChild(sendBtn);
    badge.appendChild(row);
  }

  function injectFloatingBadge() {
    if (!document.body) return;
    let badge = document.getElementById('cindy-flow-floating-badge');
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'cindy-flow-floating-badge';
      badge.style.cssText = [
        'position: fixed',
        'bottom: 20px',
        'left: 20px',
        'z-index: 2147483647',
        'background: rgba(7, 9, 14, 0.95)',
        'border: 1.5px solid rgba(230, 175, 46, 0.8)',
        'border-radius: 14px',
        'padding: 10px 14px',
        'color: #e2e8f0',
        'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'box-shadow: 0 12px 28px -5px rgba(0, 0, 0, 0.75), 0 0 18px rgba(230, 175, 46, 0.3)',
        'direction: rtl',
        'backdrop-filter: blur(10px)',
        'transition: all 0.25s ease'
      ].join('; ');
      document.body.appendChild(badge);
    }
    if (!badge.firstChild) {
      renderDefaultBadgeContent(badge);
    }
    ensureAngularSubmitPatched();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectFloatingBadge);
  } else {
    injectFloatingBadge();
  }

  const badgeKeepAlive = setInterval(() => {
    if (!isContextAlive()) {
      clearInterval(badgeKeepAlive);
      return;
    }
    if (isGoogleFlowPage()) {
      injectFloatingBadge();
    }
  }, 1800);

  function showBadgeNotification(text, isWarn) {
    injectFloatingBadge();
    const badge = document.getElementById('cindy-flow-floating-badge');
    if (!badge) return;
    let sub = document.getElementById('cindy-flow-badge-sub');
    if (!sub) {
      renderDefaultBadgeContent(badge);
      sub = document.getElementById('cindy-flow-badge-sub');
    }
    if (sub) {
      sub.style.color = isWarn ? '#facc15' : '#34d399';
      sub.textContent = '⚡ ' + text;
    }
    clearTimeout(window.__cindyBadgeResetTimer);
    window.__cindyBadgeResetTimer = setTimeout(() => {
      if (badge) renderDefaultBadgeContent(badge);
    }, 7000);
  }

  function isVisible(el) {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 4 && rect.height > 4;
  }

  function findPromptInput() {
    const pm = document.querySelector('.ProseMirror');
    if (pm && isVisible(pm)) return pm;

    const candidates = [
      'div[contenteditable="true"][aria-label*="create" i]',
      'div[contenteditable="true"][aria-label*="prompt" i]',
      'textarea[aria-label*="prompt" i]',
      'div[contenteditable="true"]',
      'textarea',
      '[role="textbox"]'
    ];
    for (const sel of candidates) {
      const els = Array.from(document.querySelectorAll(sel)).filter(el => isVisible(el) && !el.disabled && el.id !== 'cindy-flow-send-btn');
      if (els.length > 0) return els[0];
    }
    return null;
  }

  // Switch Google Flow (flow.google.com) between Image (Nano Banana) and Video (Veo 3.1) + Aspect Ratio + Count
  async function ensureFlowSettings(wantMode, aspectRatio, numCount) {
    try {
      // Ensure "All media" sidebar tab is active so both images and videos are visible in the gallery
      const allMediaNav = Array.from(document.querySelectorAll('button, .mdc-list-item')).find(b => /dashboard\s*All media/i.test((b.innerText || '').replace(/\s+/g, ' ')));
      if (allMediaNav && !allMediaNav.className.includes('activated')) {
        allMediaNav.click();
        await new Promise(r => setTimeout(r, 200));
      }

      const setBtn = document.querySelector('button.settings-trigger-button, button[aria-label="Settings trigger"]');
      if (!setBtn) return true;

      const summary = (setBtn.innerText || '').replace(/\s+/g, ' ').trim().toLowerCase();
      const isCurrentlyImage = summary.includes('nano banana') || summary.includes('imagen') || summary.includes('🍌');
      const isCurrentlyVideo = summary.includes('veo') || summary.includes('video');

      const wantAr = String(aspectRatio || '').includes('9_16') || String(aspectRatio || '').includes('9:16') ? '9:16'
        : (String(aspectRatio || '').includes('1_1') || String(aspectRatio || '').includes('square') || String(aspectRatio || '').includes('1:1') ? '1:1' : '16:9');
      const wantCountStr = 'x' + Math.min(Math.max(parseInt(numCount || 1, 10) || 1, 1), 4);

      const modeMatches = (wantMode === 'image' && isCurrentlyImage) || (wantMode === 'video' && isCurrentlyVideo);
      const arMatches = summary.includes(wantAr);
      const countMatches = wantMode === 'video' ? true : summary.includes(wantCountStr);

      if (modeMatches && arMatches && countMatches) {
        return true;
      }

      // Open Settings popover
      setBtn.click();
      await new Promise(r => setTimeout(r, 420));

      const settingsOverlay = document.querySelector('flow-prompt-box-settings, .cdk-overlay-container');
      if (settingsOverlay) {
        // 1. Switch Mode (Image vs Video)
        const modeTargetText = wantMode === 'image' ? /^image$/i : /^video$/i;
        const toggleButtons = Array.from(settingsOverlay.querySelectorAll('button.mat-button-toggle-button, button[role="radio"]'));
        const modeBtn = toggleButtons.find(b => {
          const lbl = b.querySelector('.toggle-text');
          const txt = (lbl ? lbl.textContent : b.textContent || '').trim();
          return modeTargetText.test(txt);
        });
        if (modeBtn && modeBtn.getAttribute('aria-checked') !== 'true') {
          modeBtn.click();
          await new Promise(r => setTimeout(r, 350));
        }

        // 2. Switch Aspect Ratio (16:9, 9:16, 1:1)
        const updatedToggles = Array.from(settingsOverlay.querySelectorAll('button.mat-button-toggle-button, button[role="radio"]'));
        const arBtn = updatedToggles.find(b => {
          const lbl = b.querySelector('.toggle-text');
          const txt = (lbl ? lbl.textContent : b.textContent || '').trim();
          return txt === wantAr;
        });
        if (arBtn && arBtn.getAttribute('aria-checked') !== 'true') {
          arBtn.click();
          await new Promise(r => setTimeout(r, 250));
        }

        // 3. Switch Count (x1, x2, x3, x4)
        const finalToggles = Array.from(settingsOverlay.querySelectorAll('button.mat-button-toggle-button, button[role="radio"]'));
        const countBtn = finalToggles.find(b => {
          const lbl = b.querySelector('.toggle-text');
          const txt = (lbl ? lbl.textContent : b.textContent || '').trim().toLowerCase();
          return txt === wantCountStr;
        });
        if (countBtn && countBtn.getAttribute('aria-checked') !== 'true') {
          countBtn.click();
          await new Promise(r => setTimeout(r, 250));
        }
      }

      // Close Settings popover cleanly by dispatching pointer sequence on .ProseMirror
      const pm = document.querySelector('.ProseMirror');
      if (pm) {
        ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evtName => {
          pm.dispatchEvent(new MouseEvent(evtName, { bubbles: true, cancelable: true, view: window }));
        });
      } else {
        setBtn.click();
      }
      await new Promise(r => setTimeout(r, 280));
    } catch (e) {
      console.warn('[Cindy Flow Bridge] ensureFlowSettings warning:', e);
    }
    return true;
  }

  // Google Flow Angular prototype submit patch:
  // In <flow-base-prompt-box>, default_AiSandboxAngularFrontend.uZ.prototype.submit checks (a != null && a.isTrusted).
  // For zero-credit generations (like Nano Banana on Ultra), synthetic JS clicks are ignored unless isTrusted is true.
  // We patch the Angular component prototype via an iframe using Flow's CSP script nonce so all Cindy triggers submit cleanly.
  function ensureAngularSubmitPatched() {
    try {
      const nonce = (document.querySelector('script[nonce]') || {}).nonce || '';
      const ifr = document.createElement('iframe');
      ifr.style.display = 'none';
      document.body.appendChild(ifr);
      const patchCode = `
        try {
          if (window.parent && window.parent.default_AiSandboxAngularFrontend && window.parent.default_AiSandboxAngularFrontend.uZ) {
            const proto = window.parent.default_AiSandboxAngularFrontend.uZ.prototype;
            if (!proto.__cindy_orig_submit) {
              proto.__cindy_orig_submit = proto.submit;
              proto.submit = function(evt) {
                let trustedEvt = evt;
                if (!evt || !evt.isTrusted) {
                  trustedEvt = new Proxy(evt || {}, {
                    get(target, prop) {
                      if (prop === 'isTrusted') return true;
                      const v = target[prop];
                      return typeof v === 'function' ? v.bind(target) : v;
                    }
                  });
                }
                return proto.__cindy_orig_submit.call(this, trustedEvt);
              };
            }
          }
        } catch(e) {}
      `;
      const sc = ifr.contentDocument.createElement('script');
      if (nonce) sc.setAttribute('nonce', nonce);
      sc.textContent = patchCode;
      ifr.contentDocument.documentElement.appendChild(sc);
      setTimeout(() => {
        try { ifr.remove(); } catch(e) {}
      }, 800);
    } catch (e) {
      console.warn('[Cindy Flow Bridge] submit patch warning:', e);
    }
  }

  async function injectAndTriggerFlow(promptText) {
    ensureAngularSubmitPatched();
    let targetInput = findPromptInput();
    if (!targetInput) {
      await new Promise(r => setTimeout(r, 500));
      targetInput = findPromptInput();
    }
    if (!targetInput) return false;

    const cleanPrompt = String(promptText || '').replace(/\s*--(ar|duration)\s+\S+/gi, '').trim();

    if (targetInput.isContentEditable) {
      targetInput.focus();
      targetInput.innerText = cleanPrompt;
      targetInput.dispatchEvent(new Event('input', { bubbles: true }));
      targetInput.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      targetInput.focus();
      targetInput.value = cleanPrompt;
      targetInput.dispatchEvent(new Event('input', { bubbles: true }));
      targetInput.dispatchEvent(new Event('change', { bubbles: true }));
    }

    await new Promise(r => setTimeout(r, 400));
    ensureAngularSubmitPatched();

    const genBtn = document.querySelector('button.generate-icon-button, button[aria-label="Start generation"], button[type="submit"]');
    if (genBtn && !genBtn.disabled) {
      ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evtName => {
        genBtn.dispatchEvent(new MouseEvent(evtName, { bubbles: true, cancelable: true, view: window }));
      });
      genBtn.click();
      return true;
    }

    return false;
  }

  async function toTransferableUrl(src) {
    if (!src) return '';
    if (src.startsWith('data:')) return src;
    try {
      const resp = await fetch(src);
      const blob = await resp.blob();
      if (blob.size > 25 * 1024 * 1024) return src;
      return await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result || src);
        reader.onerror = () => resolve(src);
        reader.readAsDataURL(blob);
      });
    } catch (e) {
      return src;
    }
  }

  function snapshotMediaUrls(selector) {
    const urls = new Set();
    document.querySelectorAll(selector).forEach(el => {
      const s = el.currentSrc || el.src;
      if (s) urls.add(s);
    });
    return urls;
  }

  function startWatchingForOutput(task, baselineUrls) {
    const isVideo = task.type === 'video';
    const selector = isVideo ? 'video' : 'img';
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;
      const els = Array.from(document.querySelectorAll(selector)).filter(el => {
        const s = el.currentSrc || el.src;
        if (!s || s.startsWith('data:image/svg') || s.includes('avatar') || s.includes('googleusercontent.com/a/') || baselineUrls.has(s)) return false;
        if (!isVideo && (el.alt || '').toLowerCase().includes('video thumbnail')) return false;
        const rect = el.getBoundingClientRect();
        const w = el.naturalWidth || el.videoWidth || rect.width;
        const h = el.naturalHeight || el.videoHeight || rect.height;
        return w >= 120 && h >= 120;
      });

      if (els.length > 0) {
        clearInterval(interval);
        if (!isVideo && (task.numImages || 1) > 1) {
          await new Promise(r => setTimeout(r, 1800));
        }
        const finalEls = Array.from(document.querySelectorAll(selector)).filter(el => {
          const s = el.currentSrc || el.src;
          if (!s || s.startsWith('data:image/svg') || s.includes('avatar') || s.includes('googleusercontent.com/a/') || baselineUrls.has(s)) return false;
          if (!isVideo && (el.alt || '').toLowerCase().includes('video thumbnail')) return false;
          const rect = el.getBoundingClientRect();
          const w = el.naturalWidth || el.videoWidth || rect.width;
          const h = el.naturalHeight || el.videoHeight || rect.height;
          return w >= 120 && h >= 120;
        });

        const converted = [];
        for (const el of finalEls.slice(0, 4)) {
          const rawUrl = el.currentSrc || el.src;
          const safeUrl = await toTransferableUrl(rawUrl);
          if (safeUrl) converted.push({ url: safeUrl });
        }

        if (converted.length > 0 && isContextAlive()) {
          showBadgeNotification('اكتمل التوليد في Flow! تم إرسال النتيجة إلى شاشة سيندي. ✅');
          chrome.runtime.sendMessage({
            action: 'FLOW_MEDIA_READY',
            media: {
              url: converted[0].url,
              images: converted,
              media_type: isVideo ? 'video' : 'image',
              model: task.model || 'Google Flow',
              prompt: task.prompt
            }
          });
        }
      }

      if (attempts > 120) {
        clearInterval(interval);
      }
    }, 2000);
  }

  async function syncCurrentFlowMediaToCindy(preferType) {
    const vids = Array.from(document.querySelectorAll('video')).filter(el => {
      const s = el.currentSrc || el.src;
      const rect = el.getBoundingClientRect();
      return s && (el.videoWidth >= 120 || rect.width >= 120);
    });
    const imgs = Array.from(document.querySelectorAll('img')).filter(el => {
      const s = el.currentSrc || el.src;
      if (!s || s.startsWith('data:image/svg') || s.includes('avatar') || s.includes('googleusercontent.com/a/')) return false;
      const rect = el.getBoundingClientRect();
      const w = el.naturalWidth || rect.width;
      const h = el.naturalHeight || rect.height;
      return w >= 140 && h >= 140;
    });

    let useVideo = preferType === 'video' ? vids.length > 0 : (preferType === 'image' ? false : vids.length > 0 && imgs.length === 0);
    if (!useVideo && imgs.length === 0 && vids.length > 0) useVideo = true;

    if (useVideo && vids.length > 0) {
      showBadgeNotification('جاري إرسال الفيديو إلى شاشة سيندي...');
      const rawUrl = vids[0].currentSrc || vids[0].src;
      const safeUrl = await toTransferableUrl(rawUrl);
      const mediaObj = { url: safeUrl, media_type: 'video', model: 'Google Flow (Synced)', prompt: 'Synced from Google Flow tab' };
      if (isContextAlive()) chrome.runtime.sendMessage({ action: 'FLOW_MEDIA_READY', media: mediaObj });
      showBadgeNotification('تم إرسال الفيديو إلى شاشة سيندي بنجاح! ✅');
      return { success: true, count: 1, media_type: 'video' };
    }

    if (imgs.length > 0) {
      showBadgeNotification('جاري إرسال الصور إلى شاشة سيندي...');
      const converted = [];
      for (const el of imgs.slice(0, 4)) {
        const rawUrl = el.currentSrc || el.src;
        const safeUrl = await toTransferableUrl(rawUrl);
        if (safeUrl) converted.push({ url: safeUrl });
      }
      if (converted.length > 0) {
        const mediaObj = { url: converted[0].url, images: converted, media_type: 'image', model: 'Google Flow (Synced)', prompt: 'Synced from Google Flow tab' };
        if (isContextAlive()) chrome.runtime.sendMessage({ action: 'FLOW_MEDIA_READY', media: mediaObj });
        showBadgeNotification('تم إرسال الصور إلى شاشة سيندي بنجاح! ✅');
        return { success: true, count: converted.length, media_type: 'image' };
      }
    }

    showBadgeNotification('لا توجد صور أو فيديوهات معروضة حالياً في الصفحة.', true);
    return { success: false, error: 'لم يتم العثور على صور أو فيديوهات معروضة حالياً في تبويب Google Flow.' };
  }

  window.__cindyFlowMessageHandler = (message, sender, sendResponse) => {
    if (!message) return false;

    if (message.action === 'CINDY_PING') {
      injectFloatingBadge();
      sendResponse({ status: 'PONG', active: true, version: '1.3.1' });
      return true;
    }

    if (message.action === 'SYNC_FLOW_MEDIA') {
      syncCurrentFlowMediaToCindy(message.preferType || 'auto').then(res => sendResponse(res));
      return true;
    }

    if (message.action === 'INJECT_AND_GENERATE_V2' || message.action === 'INJECT_AND_GENERATE') {
      const task = message.task || {};
      const want = task.type === 'video' ? 'video' : 'image';

      (async () => {
        injectFloatingBadge();
        await ensureFlowSettings(want, task.aspectRatio, task.numImages || 1);

        const baseline = snapshotMediaUrls(want === 'video' ? 'video' : 'img');
        const ok = await injectAndTriggerFlow(task.prompt);
        if (ok) {
          showBadgeNotification('تم إدخال البرومبت في وضع (' + (want === 'image' ? 'الصور 🍌' : 'الفيديو 🎬') + ') — جارٍ التوليد...');
          startWatchingForOutput(task, baseline);
          sendResponse({ success: true, message: 'تم إدخال البرومبت في Google Flow والبدء بالتوليد' });
        } else {
          try { await navigator.clipboard.writeText(task.prompt || ''); } catch (e) {}
          showBadgeNotification('تم نسخ البرومبت للحافظة — الصقه في خانة التوليد (Ctrl+V)', true);
          sendResponse({
            success: false,
            error: 'تعذر العثور على خانة كتابة البرومبت في تبويب Google Flow.'
          });
        }
      })();
      return true;
    }
  };

  if (!window.__cindyFlowListenerAdded && isContextAlive()) {
    window.__cindyFlowListenerAdded = true;
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (window.__cindyFlowMessageHandler) {
        return window.__cindyFlowMessageHandler(message, sender, sendResponse);
      }
    });
  }
})();
