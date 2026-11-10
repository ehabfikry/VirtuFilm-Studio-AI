# -*- coding: utf-8 -*-

import json, os, sys



sys.stdout.reconfigure(encoding='utf-8')



sys.path.append(r"C:\Users\DELL\Desktop\Cindy-AI-Director")

from cindy_server import get_intelligence_report, get_full_models_catalog

intelligence_report = get_intelligence_report()

intelligence_report_json = json.dumps(intelligence_report, ensure_ascii=False)

models_catalog = get_full_models_catalog()

models_catalog_json = json.dumps(models_catalog, ensure_ascii=False)



memory_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_memory.json'

with open(memory_file, 'r', encoding='utf-8') as f:

    memory_data = json.load(f)

memory_json_str = json.dumps(memory_data, ensure_ascii=False)



prompts_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\master_prompts_db.json'

with open(prompts_file, 'r', encoding='utf-8') as f:

    prompts_data = json.load(f)

prompts_json_str = json.dumps(prompts_data, ensure_ascii=False)



html_content = f'''<!DOCTYPE html>

<html lang="ar" dir="rtl" class="dark" style="scrollbar-gutter: stable; overflow-y: scroll;">

<head>

  <meta charset="UTF-8">

  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>CINDY AI | سيندي - استوديو التوليد السينمائي الاحترافي المتكامل</title>

  <script src="https://cdn.tailwindcss.com"></script>


  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Cinzel:wght@600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

  <script>

    tailwind.config = {{

      darkMode: 'class',

      theme: {{

        extend: {{

          fontFamily: {{

            cairo: ['Cairo', 'sans-serif'],

            cinzel: ['Cinzel', 'serif'],

            mono: ['JetBrains Mono', 'monospace'],

          }},

          colors: {{

            cinema: {{

              900: '#07090e',

              800: '#0d111a',

              700: '#141a27',

              600: '#1e2638',

              gold: '#e6af2e',

              neon: '#00f0ff',

              purple: '#9d4edd',

              red: '#ff0055',

              google: '#4285f4'

            }}

          }}

        }}

      }}

    }}

  

  </script>

  <style>

    html {{

      scrollbar-gutter: stable;

      overflow-y: scroll;

    }}

    body {{

      font-family: 'Cairo', sans-serif;

      background-color: #07090e;

      color: #e2e8f0;

      overflow-x: hidden;

    }}

    #comfy-preview-box {{

      min-height: 520px !important;

      max-height: 520px !important;

      height: 520px !important;

    }}

    input, textarea, select, button {{

      font-family: 'Cairo', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

    }}

    input[dir="auto"], textarea[dir="auto"] {{

      unicode-bidi: plaintext;

      text-align: start;

    }}

    /* HIGH CONTRAST & LEGIBILITY OVERRIDES */

    input, textarea, select {{

      color: #ffffff !important;

      background-color: #0b0f19 !important;

      border: 1px solid #3b4861 !important;

      font-size: 13px !important;

      font-weight: 500 !important;

    }}

    input:focus, textarea:focus, select:focus {{

      border-color: #e6af2e !important;

      box-shadow: 0 0 0 2px rgba(230, 175, 46, 0.25) !important;

    }}

    input::placeholder, textarea::placeholder {{

      color: #94a3b8 !important;

      opacity: 1 !important;

      font-weight: 400 !important;

    }}

    label {{

      color: #f1f5f9 !important;

      font-weight: 700 !important;

      font-size: 12px !important;

    }}

    .text-slate-400, .text-slate-500 {{

      color: #cbd5e1 !important;

    }}

    #screen-active-prompt {{

      color: #fef08a !important;

      background-color: #090d16 !important;

      padding: 6px 10px !important;

      border-radius: 8px !important;

      border: 1px solid #1e293b !important;

      font-size: 12px !important;

    }}

    #edit-media-prompt {{

      color: #ffffff !important;

      background-color: #050811 !important;

      font-size: 13px !important;

    }}

    .glass-panel {{

      background: rgba(13, 17, 26, 0.94);

      backdrop-filter: blur(16px);

      -webkit-backdrop-filter: blur(16px);

    }}

    @keyframes pulse-ring {{

      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0.7); }}

      70% {{ transform: scale(1.1); box-shadow: 0 0 0 15px rgba(66, 133, 244, 0); }}

      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(66, 133, 244, 0); }}

    }}

    .recording-pulse {{

      animation: pulse-ring 1.5s infinite cubic-bezier(0.45, 0, 0.55, 1);

      background: #4285f4 !important;

      color: white !important;

    }}

    .wave-bar {{ animation: wave 1.2s ease-in-out infinite alternate; }}

    @keyframes wave {{ 0% {{ height: 4px; }} 100% {{ height: 28px; }} }}

    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}

    ::-webkit-scrollbar-track {{ background: #07090e; }}

    ::-webkit-scrollbar-thumb {{ background: #1e2638; border-radius: 4px; }}

    ::-webkit-scrollbar-thumb:hover {{ background: #e6af2e; }}

    .toast-item {{ pointer-events: auto; cursor: pointer; animation: toast-in .25s ease-out; }}

    @keyframes toast-in {{ from {{ opacity: 0; transform: translateY(-8px); }} to {{ opacity: 1; transform: none; }} }}

    :focus-visible {{ outline: 2px solid #e6af2e; outline-offset: 2px; }}

    select option, select optgroup {{ background: #0d111a; color: #e2e8f0; }}

    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}

  </style>

</head>

<body class="min-h-screen flex flex-col bg-cinema-900 text-slate-100">



  <!-- TOP HEADER -->

  <header class="glass-panel border-b border-cinema-700/60 sticky top-0 z-50 px-4 py-2.5">

    <div class="max-w-7xl mx-auto flex items-center justify-between gap-4 flex-nowrap overflow-x-auto no-scrollbar">

      

      <!-- Brand & Status -->

      <div class="flex items-center gap-3">

        <div class="relative">

          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-cinema-purple to-cinema-gold flex items-center justify-center text-white shadow-lg shadow-blue-500/30">

            <i class="fa-solid fa-clapperboard text-lg"></i>

          </div>

          <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-cinema-900 rounded-full animate-pulse"></span>

        </div>

        <div>

          <div class="flex items-center gap-2">

            <h1 class="text-lg font-black font-cinzel tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cinema-gold via-amber-200 to-yellow-500">CINDY AI</h1>

            <span class="text-[10px] px-2 py-0.5 rounded-full bg-cinema-purple/30 text-purple-300 font-bold border border-cinema-purple/50">سيندي</span>

            <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-bold border border-blue-500/40">

              Google Flow & SOTA Multi-Cloud

            </span>

          </div>

          <p class="text-[11px] text-slate-400 font-semibold flex items-center gap-2">

            <span>تحكم سينمائي كامل: قوائم منفصلة للفيديو والصور + مدد اللقطات وعدد الإطارات</span>

          </p>

        </div>

      </div>



      <!-- Navigation Tabs (DIRECT ACCESS TO ALL CORE STUDIOS) -->
      <div class="hidden lg:flex items-center bg-cinema-800/80 p-1 rounded-xl border border-cinema-700 shadow-inner gap-1">
        <button onclick="switchTab('chat')" id="nav-main-chat" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-cinema-gold text-cinema-900 shadow">
          <i class="fa-solid fa-clapperboard"></i><span>الإخراج والدردشة</span>
        </button>

        <button onclick="switchTab('comfy')" id="nav-main-comfy" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-300 hover:text-white transition flex items-center gap-1.5 border border-emerald-500/40 bg-emerald-500/10 shadow">
          <i class="fa-solid fa-bolt text-emerald-400"></i>
          <span>استوديو ComfyUI السينمائي (Wan 2.1 / Wan 2.2)</span>
          <span id="comfy-status-dot" class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </button>

        <button onclick="switchTab('screening')" id="nav-main-screening" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition flex items-center gap-1.5">
          <i class="fa-solid fa-film text-amber-400"></i><span>الاستوديو والعرض</span>
        </button>

        <button onclick="switchTab('lora')" id="nav-main-lora" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-purple-300 transition flex items-center gap-1.5">
          <i class="fa-solid fa-dna text-purple-400"></i><span>الممثلين (LoRA)</span>
        </button>

        <button onclick="switchTab('flow')" id="nav-main-flow" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-blue-300 transition flex items-center gap-1.5">
          <i class="fa-brands fa-google text-blue-400"></i><span>Google Flow</span>
        </button>

        <button onclick="switchTab('vault')" id="nav-main-vault" class="px-3 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-amber-300 transition flex items-center gap-1.5">
          <i class="fa-solid fa-lock text-amber-400"></i><span>الخزنة</span>
        </button>
      </div>



      <!-- Controls -->

      <div class="flex items-center gap-2">

        <!-- Google Flow Bridge Status Pill -->

        <div id="google-flow-bridge-badge" onclick="openBridgeGuide()" class="cursor-pointer px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold flex items-center gap-1.5 transition shadow">

          <i class="fa-solid fa-puzzle-piece text-amber-400"></i>

          <span>جسر فلو: اضغط للتثبيت</span>

        </div>



        <!-- Live Wallet Balance Bar -->

        <div id="cindy-wallet-bar" class="hidden md:flex items-center gap-2 bg-cinema-900/90 border border-cinema-700/80 rounded-xl px-2.5 py-1 shadow-inner text-[11px] shrink-0">

          <div class="flex items-center gap-1.5 text-slate-300 font-semibold cursor-pointer" onclick="refreshWalletStatus(true)" title="رصيد سيرفرات RunPod السحابية">

            <i class="fa-solid fa-server text-purple-400 text-xs"></i>

            <span class="text-slate-400">RunPod:</span>

            <span id="wallet-runpod-badge" class="text-emerald-400 font-bold font-mono">$13.25</span>

          </div>

          <button type="button" onclick="emergencyStopAllRunpod(true)" id="topbar-emergency-stop-btn" class="px-2.5 py-1 rounded-lg bg-cinema-800 hover:bg-rose-900/80 text-rose-300 hover:text-white border border-rose-500/40 font-bold text-[10px] flex items-center gap-1 transition shadow cursor-pointer" title="إيقاف وحذف كروت RunPod فوراً لوقف استهلاك الرصيد">
            <i class="fa-solid fa-power-off text-[9px] text-rose-400"></i>
            <span id="topbar-emergency-stop-text">🛑 إيقاف RunPod</span>
          </button>

          <span class="text-cinema-700">|</span>

          <div class="flex items-center gap-1.5 text-slate-300 font-semibold" title="حالة محركات Fal.ai">

            <i class="fa-solid fa-bolt text-amber-400 text-xs"></i>

            <span class="text-slate-400">Fal:</span>

            <span id="wallet-fal-badge" class="text-amber-300 font-bold">متصل</span>

          </div>

          <button type="button" onclick="refreshWalletStatus(true)" title="تحديث الرصيد الآن" class="text-slate-400 hover:text-cinema-gold p-1 transition">

            <i class="fa-solid fa-arrows-rotate text-[11px]" id="wallet-refresh-icon"></i>

          </button>

          <span class="text-cinema-700">|</span>

          <button type="button" onclick="openDailyPricingModal()" id="topbar-pricing-btn" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cinema-800 hover:bg-amber-950/60 text-amber-300 hover:text-amber-200 border border-amber-500/40 font-bold text-[10px] transition shadow cursor-pointer" title="عرض مؤشر أسعار الأدوات والموديلات اليومي">
            <i class="fa-solid fa-tags text-[10px] text-amber-400"></i>
            <span>مؤشر الأسعار</span>
            <span id="topbar-pricing-date-pill" class="text-[9px] bg-amber-500/20 text-amber-300 px-1.5 py-0.2 rounded font-mono">اليوم</span>
          </button>

        </div>



        <button onclick="toggleVoiceOutput()" id="tts-toggle-btn" class="px-3 py-1.5 rounded-lg bg-cinema-800 border border-cinema-700 text-xs font-bold text-slate-300 hover:text-cinema-gold transition flex items-center gap-1.5">

          <i class="fa-solid fa-volume-high text-cinema-gold" id="tts-icon"></i>

          <span class="hidden sm:inline" id="tts-text">الصوت: مفعل</span>

        </button>

      </div>



    </div>



    <!-- Mobile Nav -->
    <div class="flex lg:hidden items-center justify-around mt-2 pt-2 border-t border-cinema-800 text-[11px] overflow-x-auto gap-2">
      <button onclick="switchTab('chat')" class="text-cinema-gold font-bold whitespace-nowrap"><i class="fa-solid fa-comments"></i> إخراج</button>
      <button onclick="switchTab('comfy')" class="text-emerald-400 font-bold whitespace-nowrap"><i class="fa-solid fa-bolt"></i> ComfyUI (Wan)</button>
      <button onclick="switchTab('screening')" class="text-slate-400 font-bold whitespace-nowrap"><i class="fa-solid fa-film"></i> العرض</button>
      <button onclick="switchTab('lora')" class="text-purple-400 font-bold whitespace-nowrap"><i class="fa-solid fa-dna"></i> LoRA</button>
      <button onclick="switchTab('flow')" class="text-blue-400 font-bold whitespace-nowrap"><i class="fa-brands fa-google"></i> فلو</button>
      <button onclick="switchTab('vault')" class="text-slate-400 font-bold whitespace-nowrap"><i class="fa-solid fa-lock"></i> الخزنة</button>
    </div>

  </header>



  <!-- MAIN VIEWPORT -->

  <main class="flex-1 max-w-7xl w-full mx-auto p-4 flex flex-col gap-4">



    <!-- ======================================================== -->

    <!-- TAB 1: CHAT & ADVANCED PARAMETERS CONTROL -->

    <!-- ======================================================== -->

    <section id="tab-chat" class="flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl overflow-hidden shadow-2xl">

      

      <!-- DIRECTORIAL CONTROL BAR (MODE, MODEL, DURATION, IMAGES COUNT, RATIO) -->

      <div class="px-5 py-3 border-b border-cinema-700/80 bg-cinema-800/90 flex flex-wrap items-center justify-between gap-3 text-xs">

        

        <!-- 1. Mode Switcher (Video vs Image) -->

        <div class="flex items-center bg-cinema-900 p-1 rounded-xl border border-cinema-700 shadow-inner">

          <button onclick="setGenerationMode('video')" id="mode-btn-video" class="px-3.5 py-1.5 rounded-lg text-xs font-black transition flex items-center gap-1.5 bg-cinema-gold text-cinema-900 shadow">

            <i class="fa-solid fa-video text-xs"></i>

            <span>أدوات الفيديو (Video)</span>

          </button>

          <button onclick="setGenerationMode('image')" id="mode-btn-image" class="px-3.5 py-1.5 rounded-lg text-xs font-black text-slate-400 hover:text-white transition flex items-center gap-1.5">

            <i class="fa-solid fa-image text-xs"></i>

            <span>أدوات الصور (Images)</span>

          </button>

        </div>



        <!-- 2. VIDEO CONTROLS BLOCK -->

        <div id="video-controls-group" class="flex flex-wrap items-center gap-2 flex-1 max-w-4xl">

          <!-- Video Model Dropdown -->
          <div class="flex-1 min-w-[220px]">
            <select id="active-video-model" onchange="syncSelectedModel()" class="w-full bg-cinema-900 border border-cinema-gold/60 rounded-xl px-2.5 py-1.5 text-slate-100 font-bold focus:outline-none focus:border-cinema-gold text-xs shadow-inner">
              <optgroup label="📝 1. موديلات نص فقط (Text-to-Video) - لا تحتاج صورة">
                <option value="MiniMax H3 Lite" selected>⚡ MiniMax Hailuo H3 Lite (~$0.04 - الأرخص للتجارب)</option>
                <option value="Wan 2.1 (Alibaba 14B)">💎 Alibaba Wan 2.1 (سينمائي مفتوح المصدر 720p)</option>
                <option value="CogVideoX-5B (THUDM)">🎥 THUDM CogVideoX-5B (مفتوح المصدر - سريع)</option>
                <option value="Tencent HunyuanVideo">🎬 Tencent HunyuanVideo (ثبات فيزيائي 13B)</option>
                <option value="Kling AI Standard">⚡ Kling Standard (حركة بشرية واقعية)</option>
                <option value="Kling 4 / 3.0 Pro">👑 Kling Pro 1080p (أعلى دقة وثبات)</option>
                <option value="Luma Ray 2 &amp; Dream Machine">🌊 Luma Ray 2 (حركة كاميرا ثلاثية الأبعاد)</option>
                <option value="Google Veo 3.1 Fast">⚡ Google Veo 3.1 Fast</option>
                <option value="Google Veo 3.1 Cinematic">🎬 Google Veo 3.1 Cinematic (لقطة إخراجية)</option>
              </optgroup>
              <optgroup label="🖼️ 2. موديلات صورة إلى فيديو (Image-to-Video) - تحريك كادر مرجعي">
                <option value="Wan 2.2 Image-to-Video">💎 Alibaba Wan 2.2 Image-to-Video (تحريك سينمائي فائق الحركية)</option>
                 <option value="Wan 2.1 Image-to-Video">💎 Alibaba Wan 2.1 Image-to-Video (تحريك كادر سينمائي)</option>
                <option value="CogVideoX-5B Image-to-Video">🎥 CogVideoX-5B Image-to-Video (تحريك كادر مفتوح)</option>
                <option value="Stability SVD-XT">⚡ Stability AI SVD-XT (25 كادر سينمائي مستقر)</option>
                <option value="Flux 3 Max Image-to-Video">🌟 Flux 3 Max I2V (أعلى دقة تفاصيل فوتوغرافية)</option>
                <option value="MiniMax H3 Max Turbo">🎯 MiniMax H3 Max Turbo (قفل ملامح الشخصية المرجعية)</option>
                <option value="Kling 1.6 Pro Image-to-Video">👑 Kling 1.6 Pro I2V (يدعم كادر بداية + كادر نهاية اختياري)</option>
                <option value="Luma Ray 2 Image-to-Video">🌊 Luma Ray 2 I2V (يدعم كادر بداية + كادر نهاية اختياري)</option>
                <option value="Mischief-1 Image-to-Video">🔥 Mischief-1 (أكشن وديناميكا)</option>
              </optgroup>
              <optgroup label="🎬 3. نقل حركة كامل للجسم وتعديل فيديو (Motion & Video Control)">
                <option value="Kling Motion Control (1080p)">👑 Kling Motion Control (1080p) - نقل حركة كامل للممثل</option>
                <option value="Kling O1 Video-to-Video Edit">🎞️ Kling O1 Edit (تعديل وتطبيق ستايل على فيديو)</option>
                <option value="Luma Ray 2 Modify">🌊 Luma Ray 2 Modify (تعديل إضاءة وستايل الفيديو)</option>
              </optgroup>
            </select>
          </div>

          <!-- Video Duration Dropdown -->
          <div class="flex items-center gap-1 bg-cinema-900 border border-cinema-700 rounded-xl px-2 py-1">
            <span class="text-slate-400 font-bold text-[10px]"><i class="fa-solid fa-clock text-cinema-gold"></i> مدة اللقطة:</span>
            <select id="video-duration-select" class="bg-transparent text-amber-300 font-bold focus:outline-none text-xs">
              <option value="5" selected>5 ثوانٍ</option>
              <option value="10">10 ثوانٍ</option>
              <option value="15">15 ثانية (Commercial)</option>
            </select>
          </div>

          <!-- Aspect Ratio Dropdown -->
          <div class="flex items-center gap-1 bg-cinema-900 border border-cinema-700 rounded-xl px-2 py-1">
            <span class="text-slate-400 font-bold text-[10px]"><i class="fa-solid fa-crop text-cinema-neon"></i> الأبعاد:</span>
            <select id="video-aspect-select" class="bg-transparent text-slate-200 font-bold focus:outline-none text-xs">
              <option value="landscape_16_9" selected>16:9 (عريض)</option>
              <option value="portrait_9_16">9:16 (عمودي / Reels)</option>
              <option value="square_hd">1:1 (مربع)</option>
              <option value="landscape_21_9">21:9 (سينما سكوب)</option>
            </select>
          </div>

          <!-- DYNAMIC SMART REFERENCE HUB (المرجعيات التفاعلية) -->
          <div id="smart-ref-hub" class="flex items-center gap-2">
            
            <!-- 1. State: Text-Only (لا يتطلب أي صورة أو فيديو) -->
            <div id="ref-mode-text-badge" class="flex items-center gap-1.5 bg-cinema-950/80 border border-slate-700/80 rounded-xl px-2.5 py-1 text-[11px] text-slate-400 shadow-inner">
              <i class="fa-solid fa-align-right text-slate-400"></i>
              <span class="font-bold">نص فقط</span>
              <span class="text-[9px] text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">لا يتطلب مرجعيات بصرية</span>
            </div>

            <!-- 2. State: Image-to-Video (Start Frame + Optional End Frame) -->
            <div id="ref-mode-i2v-panel" class="hidden flex items-center gap-2 bg-cinema-900 border border-amber-500/40 rounded-xl px-2.5 py-1 shadow-inner">
              <input type="file" id="i2v-start-file-input" accept="image/*" class="hidden" onchange="handleI2VStartSelected(event)">
              <input type="file" id="i2v-end-file-input" accept="image/*" class="hidden" onchange="handleI2VEndSelected(event)">

              <!-- Start Frame Slot -->
              <div class="flex items-center gap-1.5">
                <span class="text-amber-400 font-bold text-[10px] flex items-center gap-1">
                  <i class="fa-solid fa-image"></i> كادر البداية:
                </span>
                <div id="i2v-start-empty" class="flex items-center gap-1">
                  <button type="button" onclick="document.getElementById('i2v-start-file-input').click()" class="px-2 py-0.5 rounded-lg bg-amber-600/90 hover:bg-amber-500 text-white font-bold text-[10px] flex items-center gap-1 shadow" title="رفع صورة كادر البداية">
                    <i class="fa-solid fa-cloud-arrow-up"></i> <span>رفع صورة</span>
                  </button>
                  <button type="button" onclick="useLastRenderedAsI2VStart()" class="px-2 py-0.5 rounded-lg bg-cinema-800 hover:bg-cinema-700 text-slate-300 font-bold text-[10px] flex items-center gap-1 border border-cinema-700" title="استخدام آخر كادر">
                    <i class="fa-solid fa-bolt text-amber-400"></i> <span>آخر كادر</span>
                  </button>
                </div>
                <div id="i2v-start-active" class="hidden flex items-center gap-1.5">
                  <img id="i2v-start-thumb" src="" alt="Start" class="w-6 h-6 rounded border border-amber-400 object-cover shadow">
                  <span class="text-emerald-400 font-bold text-[10px]">✓ كادر أول</span>
                  <button type="button" onclick="clearI2VStart()" class="text-rose-400 hover:text-rose-300 text-xs px-0.5" title="إلغاء">✕</button>
                </div>
              </div>

              <!-- End Frame Slot (Shown only when supported, e.g. Kling Pro / Luma Ray 2) -->
              <div id="i2v-end-wrapper" class="hidden flex items-center gap-1.5 border-r border-slate-700 pr-2 mr-1">
                <span class="text-cyan-300 font-bold text-[10px] flex items-center gap-1">
                  <i class="fa-solid fa-forward-step"></i> كادر النهاية (اختياري):
                </span>
                <div id="i2v-end-empty" class="flex items-center gap-1">
                  <button type="button" onclick="document.getElementById('i2v-end-file-input').click()" class="px-2 py-0.5 rounded-lg bg-cyan-900/80 hover:bg-cyan-800 text-cyan-200 border border-cyan-700 font-bold text-[10px] flex items-center gap-1" title="رفع إطار نهائي لانتقال سينمائي">
                    + كادر نهاية
                  </button>
                </div>
                <div id="i2v-end-active" class="hidden flex items-center gap-1.5">
                  <img id="i2v-end-thumb" src="" alt="End" class="w-6 h-6 rounded border border-cyan-400 object-cover shadow">
                  <span class="text-cyan-300 font-bold text-[10px]">✓ كادر نهاية</span>
                  <button type="button" onclick="clearI2VEnd()" class="text-rose-400 hover:text-rose-300 text-xs px-0.5" title="إلغاء">✕</button>
                </div>
              </div>
            </div>

            <!-- 3. State: Motion Control (Character Image + Driving Video) -->
            <div id="ref-mode-motion-panel" class="hidden flex items-center gap-2 bg-purple-950/30 border border-purple-500/40 rounded-xl px-2.5 py-1 shadow-inner">
              <input type="file" id="motion-char-file-input" accept="image/*" class="hidden" onchange="handleMotionCharSelected(event)">
              <input type="file" id="motion-video-file-input" accept="video/*" class="hidden" onchange="handleMotionVideoSelected(event)">

              <!-- Character slot -->
              <div class="flex items-center gap-1.5">
                <span class="text-purple-300 font-bold text-[10px] flex items-center gap-1">
                  <i class="fa-solid fa-user-tie"></i> الممثل:
                </span>
                <div id="motion-char-empty" class="flex items-center gap-1">
                  <button type="button" onclick="document.getElementById('motion-char-file-input').click()" class="px-2 py-0.5 rounded-lg bg-purple-700 hover:bg-purple-600 text-white font-bold text-[10px] flex items-center gap-1 shadow">
                    رفع صورة
                  </button>
                  <button type="button" onclick="useLastRenderedAsMotionChar()" class="px-1.5 py-0.5 rounded bg-cinema-800 text-purple-300 text-[10px] border border-cinema-700">
                    آخر كادر
                  </button>
                </div>
                <div id="motion-char-active" class="hidden flex items-center gap-1.5">
                  <img id="motion-char-thumb" src="" alt="Actor" class="w-6 h-6 rounded border border-purple-400 object-cover shadow">
                  <button type="button" onclick="clearMotionChar()" class="text-rose-400 text-xs px-0.5">✕</button>
                </div>
              </div>

              <!-- Driving video slot -->
              <div class="flex items-center gap-1.5 border-r border-purple-800/40 pr-2 mr-1">
                <span class="text-emerald-400 font-bold text-[10px] flex items-center gap-1">
                  <i class="fa-solid fa-person-running"></i> فيديو الحركة:
                </span>
                <div id="motion-video-empty" class="flex items-center gap-1">
                  <button type="button" onclick="document.getElementById('motion-video-file-input').click()" class="px-2 py-0.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-[10px] flex items-center gap-1 shadow">
                    رفع فيديو MP4
                  </button>
                </div>
                <div id="motion-video-active" class="hidden flex items-center gap-1.5">
                  <span id="motion-video-badge" class="text-[10px] font-bold text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/30">✓ فيديو الحركة محدد</span>
                  <button type="button" onclick="clearMotionVideo()" class="text-rose-400 text-xs px-0.5">✕</button>
                </div>
              </div>
            </div>

            <!-- 4. State: Video-to-Video Edit (Original Video to Restyle) -->
            <div id="ref-mode-v2v-panel" class="hidden flex items-center gap-2 bg-blue-950/30 border border-blue-500/40 rounded-xl px-2.5 py-1 shadow-inner">
              <input type="file" id="v2v-source-file-input" accept="video/*" class="hidden" onchange="handleV2VSourceSelected(event)">
              <span class="text-blue-300 font-bold text-[10px] flex items-center gap-1">
                <i class="fa-solid fa-film"></i> الفيديو الأصلي للتعديل:
              </span>
              <div id="v2v-source-empty" class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('v2v-source-file-input').click()" class="px-2 py-0.5 rounded-lg bg-blue-700 hover:bg-blue-600 text-white font-bold text-[10px] flex items-center gap-1 shadow">
                  رفع فيديو MP4
                </button>
              </div>
              <div id="v2v-source-active" class="hidden flex items-center gap-1.5">
                <span id="v2v-source-badge" class="text-[10px] font-bold text-blue-300 bg-blue-500/20 px-2 py-0.5 rounded border border-blue-500/30">✓ الفيديو محدد</span>
                <button type="button" onclick="clearV2VSource()" class="text-rose-400 text-xs px-0.5">✕</button>
              </div>
            </div>

            <!-- Active Model Cost Estimate Badge -->
            <div id="model-cost-estimate-badge" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cinema-950/90 border border-amber-500/30 text-[10px] text-slate-300 font-semibold cursor-pointer shrink-0 shadow" onclick="openDailyPricingModal()" title="عرض مؤشر أسعار الأدوات والخدمات السحابية">
              <i class="fa-solid fa-coins text-amber-400 text-xs"></i>
              <span class="text-slate-400">التكلفة:</span>
              <span id="active-model-cost-val" class="text-amber-300 font-mono font-bold">~$0.63 / 5s</span>
            </div>

          </div>

        </div>

        <!-- 3. IMAGE CONTROLS BLOCK -->

        <div id="image-controls-group" class="hidden flex flex-wrap items-center gap-2 flex-1 max-w-2xl">

          <!-- Image Model Dropdown -->

          <div class="flex-1 min-w-[200px]">

            <select id="active-image-model" onchange="syncSelectedModel()" class="w-full bg-cinema-900 border border-cinema-neon/60 rounded-xl px-2.5 py-1.5 text-slate-100 font-bold focus:outline-none focus:border-cinema-neon text-xs shadow-inner">

              <optgroup label="🌟 نماذج حساب Google Flow (توليد داخل تبويب Flow المفتوح)">

                <option value="Google Nano Banana">🍌 Google Nano Banana (توليد مباشر داخل حسابك في Google Flow)</option>

                <option value="Google Nano Banana Pro">🍌 Google Nano Banana Pro (توليد داخل حسابك في Google Flow)</option>

                

              </optgroup>

              <optgroup label="⚡ نماذج Nano Banana السحابية (توليد داخل سيندي فقط)">

                <option value="fal-ai/nano-banana">🍌 Nano Banana Cloud (داخل شاشة سيندي فقط - بدون Flow)</option>

                <option value="fal-ai/nano-banana-pro">🍌 Nano Banana Pro Cloud (داخل شاشة سيندي فقط)</option>

              </optgroup>

              <optgroup label="📸 أحدث نماذج الصور والإطارات المفتاحية">

                <option value="fal-ai/flux/schnell" selected>⚡ FLUX.1 Schnell (أسرع إطار مفتاحي في ثانيتين)</option>

                <option value="fal-ai/flux/dev">💎 FLUX.1 Dev (أعلى دقة تفاصيل سينمائية 1080p)</option>

                <option value="fal-ai/flux-pro/v1.1-ultra">📸 FLUX 1.1 Pro Ultra (جودة 2K RAW فوتوغرافية)</option>

                <option value="fal-ai/recraft-v3">🎨 Recraft v3 (تصميم واقعي متفوق)</option>

                <option value="fal-ai/ideogram/v2">🔤 Ideogram v2 (كتابة نصوص وخطوط خارقة)</option>

                <option value="fal-ai/stable-diffusion-v35-large">SD 3.5 Large</option>

              </optgroup>

            </select>

          </div>



          <!-- Number of Images Dropdown (NEW!) -->

          <div class="flex items-center gap-1 bg-cinema-900 border border-cinema-700 rounded-xl px-2 py-1">

            <span class="text-slate-400 font-bold text-[10px]"><i class="fa-solid fa-clone text-cinema-neon"></i> عدد الصور:</span>

            <select id="image-count-select" class="bg-transparent text-cyan-300 font-bold focus:outline-none text-xs">

              <option value="1" selected>1 صورة</option>

              <option value="2">2 صورتين (A/B)</option>

              <option value="4">4 صور (Grid)</option>

            </select>

          </div>



          <!-- Image Aspect Ratio Dropdown -->

          <div class="flex items-center gap-1 bg-cinema-900 border border-cinema-700 rounded-xl px-2 py-1">

            <span class="text-slate-400 font-bold text-[10px]"><i class="fa-solid fa-crop text-cinema-neon"></i> الأبعاد:</span>

            <select id="image-aspect-select" class="bg-transparent text-slate-200 font-bold focus:outline-none text-xs">

              <option value="landscape_16_9" selected>16:9 (عريض)</option>

              <option value="portrait_9_16">9:16 (عمودي / Story)</option>

              <option value="square_hd">1:1 (مربع)</option>

            </select>

          </div>

        </div>



      </div>

      <!-- Live Waveform -->

      <div id="voice-activity-bar" class="hidden px-5 py-2.5 bg-gradient-to-r from-blue-900/40 via-cinema-purple/30 to-cinema-gold/30 border-b border-cinema-gold/40 flex items-center justify-between shadow-md">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1 h-6">
            <span class="w-1.5 bg-blue-400 rounded-full wave-bar" style="animation-delay: 0.1s;"></span>
            <span class="w-1.5 bg-cinema-gold rounded-full wave-bar" style="animation-delay: 0.3s;"></span>
            <span class="w-1.5 bg-cinema-purple rounded-full wave-bar" style="animation-delay: 0.2s;"></span>
            <span class="w-1.5 bg-cinema-red rounded-full wave-bar" style="animation-delay: 0.4s;"></span>
            <span class="w-1.5 bg-emerald-400 rounded-full wave-bar" style="animation-delay: 0.15s;"></span>
          </div>
          <span class="text-xs font-bold text-slate-100" id="voice-activity-text">سيندي تستمع إليك باهتمام... تحدث براحتك ولا تقلق، لن يتم الإرسال إلا بأمرك</span>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" onclick="submitVoiceDirected()" class="text-xs px-3.5 py-1.5 bg-gradient-to-r from-cinema-gold to-amber-500 hover:from-amber-400 hover:to-yellow-500 text-cinema-900 font-black rounded-xl shadow-lg flex items-center gap-1.5 transition">
            <i class="fa-solid fa-paper-plane text-[11px]"></i>
            <span>إرسال التوجيه لسيندي</span>
          </button>
          <button type="button" onclick="stopVoiceRecognition()" class="text-xs px-3 py-1.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded-xl hover:bg-rose-500/40 font-bold flex items-center gap-1 transition">
            <i class="fa-solid fa-stop text-[11px]"></i>
            <span>إيقاف</span>
          </button>
        </div>
      </div>

      <!-- Messages Stream -->

      <div id="chat-messages-container" class="flex-1 p-5 overflow-y-auto space-y-4 max-h-[520px]">

        

        <!-- Welcome Cindy Message -->

        <div class="flex items-start gap-3">

          <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-cinema-gold flex items-center justify-center font-bold text-cinema-900 flex-shrink-0 shadow">

            <i class="fa-solid fa-clapperboard text-xs"></i>

          </div>

          <div class="flex-1 bg-cinema-800/90 border border-cinema-700/80 rounded-2xl rounded-tr-none p-4 shadow-lg">

            <div class="flex items-center justify-between mb-2">

              <span class="text-xs font-black text-cinema-gold">المساعدة الإخراجية سيندي | Cindy (Assistant Director)</span>

              <span class="text-[10px] text-blue-400 font-bold"><i class="fa-solid fa-sliders"></i> لوحة التحكم الدقيقة نشطة</span>

            </div>

            <div class="text-sm text-slate-200 leading-relaxed space-y-2">

              <p class="text-xs text-slate-200">جاهزة لأمرك يا أستاذ إيهاب. استوديو الإخراج السينمائي ومحركات نقل الحركة والانفعال (Kling Motion & LatentSync) تحت تصرفك بالكامل.</p>

            </div>

          </div>

        </div>



      </div>



      <!-- Chat Input Controls (WITH IMAGE & VIDEO UPLOAD FOR DISCUSSION & EDITING) -->

      <div class="p-3 bg-cinema-800/80 border-t border-cinema-700 space-y-2">

        <input type="file" id="media-upload-input" accept="image/*,video/*" class="hidden" onchange="handleMediaFileSelected(event)">



        <!-- Attachment Preview Chip -->

        <div id="chat-attachment-preview" class="hidden bg-cinema-900/95 border border-cinema-gold/50 rounded-xl p-2.5 flex items-center justify-between gap-3 shadow-lg">

          <div class="flex items-center gap-3 min-w-0">

            <div id="chat-attach-thumb-box" class="w-14 h-10 rounded-lg overflow-hidden bg-cinema-950 border border-cinema-700 flex items-center justify-center shrink-0"></div>

            <div class="min-w-0">

              <div class="flex items-center gap-1.5">

                <span id="chat-attach-badge" class="text-[10px] px-2 py-0.5 rounded bg-cinema-gold/20 text-cinema-gold font-bold">صورة مرفوعة</span>

                <span id="chat-attach-name" class="text-xs font-bold text-slate-200 truncate">file.jpg</span>

              </div>

              <p class="text-[11px] text-slate-400 mt-0.5">اكتب سؤالك أو التعديل المطلوب بالأسفل ثم اضغط «إرسال» للمناقشة والتعديل مع سيندي</p>

            </div>

          </div>

          <div class="flex items-center gap-1.5 shrink-0">

            <button type="button" onclick="openAttachedInScreening()" class="px-2.5 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-[11px] font-bold">

              <i class="fa-solid fa-wand-magic-sparkles"></i> فتح في استوديو التعديل

            </button>

            <button type="button" onclick="clearMediaAttachment()" class="w-7 h-7 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 flex items-center justify-center text-xs" title="إزالة المرفق">

              <i class="fa-solid fa-xmark"></i>

            </button>

          </div>

        </div>



        <!-- Prompt Target & Mode Guidance Bar -->
        <div class="flex flex-wrap items-center justify-between px-2 py-1 bg-cinema-900/60 border border-cinema-700/60 rounded-xl text-[11px] gap-2 mb-1">
          <div class="flex items-center gap-2">
            <span class="text-slate-400 font-bold flex items-center gap-1"><i class="fa-solid fa-crosshairs text-cinema-gold"></i> أداة التوليد المختارة:</span>
            <span id="active-prompt-target-badge" class="font-extrabold text-amber-300 bg-amber-500/10 px-2.5 py-0.5 rounded-lg border border-amber-500/30">MiniMax Hailuo H3 Lite</span>
            <span id="active-prompt-ref-badge" class="hidden font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-lg border border-emerald-500/30 flex items-center gap-1"><i class="fa-solid fa-lock text-[9px]"></i> بمرجع صورة</span>
          </div>
          <div class="text-[10px] text-slate-400 font-medium">
            اكتب المشهد المطلوب هنا في مربع البرومبت بالأسفل ⬇️ واضغط إرسال
          </div>
        </div>

        <form onsubmit="handleChatSubmit(event)" class="flex items-center gap-2">

          <button type="button" id="voice-record-btn" onclick="toggleVoiceRecording()" aria-label="تسجيل صوتي" class="w-12 h-12 rounded-xl bg-cinema-700 hover:bg-cinema-600 border border-cinema-600 text-cinema-gold flex items-center justify-center transition shadow-lg group relative" title="تحدث بالصوت">

            <i class="fa-solid fa-microphone text-lg group-hover:scale-110 transition"></i>

            <span class="absolute -top-8 px-2 py-0.5 bg-cinema-900 border border-cinema-700 text-[10px] text-slate-300 rounded whitespace-nowrap hidden group-hover:block">تحدث بالصوت</span>

          </button>



          <button type="button" onclick="triggerMediaUpload('chat')" aria-label="رفع صورة أو فيديو" class="px-3.5 h-12 rounded-xl bg-cinema-700 hover:bg-cinema-600 border border-cinema-neon/50 text-cinema-neon flex items-center justify-center gap-1.5 transition shadow-lg text-xs font-bold shrink-0" title="رفع صورة أو فيديو للمناقشة والتعديل">

            <i class="fa-solid fa-cloud-arrow-up text-sm"></i>

            <span class="hidden sm:inline">رفع صورة / فيديو</span>

          </button>



          <div class="flex-1 relative flex items-center">

            <textarea id="chat-input" rows="1" dir="auto" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="اكتب توجيهك الإخراجي، أو ارفع صورة/فيديو لمناقشته وتعديله مع سيندي... (Enter للإرسال، Shift+Enter لسطر جديد)" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cinema-gold pr-10 resize-none max-h-32 leading-relaxed transition-all"></textarea>

            <button type="button" onclick="clearChatInput()" aria-label="مسح النص" class="absolute left-3 top-3.5 text-slate-400 hover:text-slate-300 text-xs">

              <i class="fa-solid fa-xmark"></i>

            </button>

          </div>



          <button type="submit" id="send-btn" class="px-5 py-3 rounded-xl bg-gradient-to-r from-cinema-gold to-amber-500 hover:from-amber-400 hover:to-yellow-500 text-cinema-900 font-bold text-sm flex items-center gap-2 shadow-lg shadow-amber-500/20 transition">

            <span>إرسال</span>

            <i class="fa-solid fa-paper-plane text-xs"></i>

          </button>

        </form>

      </div>



    </section>



    <!-- ======================================================== -->

    <!-- TAB 2: GOOGLE FLOW DEDICATED SUITE -->

    <!-- ======================================================== -->

    <section id="tab-flow" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">

      

      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-3">

        <div>

          <h2 class="text-lg font-black text-white flex items-center gap-2">

            <i class="fa-brands fa-google text-blue-500"></i>

            <span>جناح نماذج Google Flow المعتمدة رسميـاً (Google Flow Suite)</span>

          </h2>

          <p class="text-xs text-slate-400">نماذج Google Flow الأربعة المتخصصة مع إمكانية التفعيل المباشر بنقرة واحدة.</p>

        </div>

      </div>



      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        

        <!-- Veo 3.1 Cinematic -->

        <div class="bg-cinema-800/90 border border-blue-500/40 rounded-xl p-4 space-y-2.5 shadow-lg">

          <div class="flex items-center justify-between">

            <h3 class="text-sm font-black text-white flex items-center gap-2">

              <i class="fa-solid fa-film text-cinema-gold"></i>

              <span>1. Google Veo 3.1 Cinematic</span>

            </h3>

            <span class="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30">4K + Native Audio</span>

          </div>

          <p class="text-xs text-slate-300 leading-relaxed">

            النموذج السينمائي الرائد لتوليد لقطات فائقة الدقة حتى 4K، مع ميزة التوليد الصوتي المتزامن الدائم (Always-on Synchronized Audio & Dialogue).

          </p>

          <button onclick="activateFromCard('video', 'Google Veo 3.1 Cinematic')" class="w-full py-1.5 bg-blue-600/30 hover:bg-blue-600/50 text-blue-200 border border-blue-500/40 rounded-lg text-xs font-bold transition">

            <i class="fa-solid fa-check"></i> تفعيل في قائمة الفيديو

          </button>

        </div>



        <!-- Veo 3.1 Fast -->

        <div class="bg-cinema-800/90 border border-blue-500/40 rounded-xl p-4 space-y-2.5 shadow-lg">

          <div class="flex items-center justify-between">

            <h3 class="text-sm font-black text-white flex items-center gap-2">

              <i class="fa-solid fa-bolt text-yellow-400"></i>

              <span>2. Google Veo 3.1 Fast</span>

            </h3>

            <span class="text-[10px] px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-300 font-bold border border-yellow-500/30">High-Speed Motion</span>

          </div>

          <p class="text-xs text-slate-300 leading-relaxed">

            نسخة فائقة السرعة للمطاردات والأكشن والرياضة مع زمن استجابة سريع وثبات فيزيائي قوي تحت حركات الكاميرا العنيفة.

          </p>

          <button onclick="activateFromCard('video', 'Google Veo 3.1 Fast')" class="w-full py-1.5 bg-yellow-600/30 hover:bg-yellow-600/50 text-yellow-200 border border-yellow-500/40 rounded-lg text-xs font-bold transition">

            <i class="fa-solid fa-check"></i> تفعيل في قائمة الفيديو

          </button>

        </div>



        <!-- Veo 3.1 Lite -->

        <div class="bg-cinema-800/90 border border-blue-500/40 rounded-xl p-4 space-y-2.5 shadow-lg">

          <div class="flex items-center justify-between">

            <h3 class="text-sm font-black text-white flex items-center gap-2">

              <i class="fa-solid fa-leaf text-emerald-400"></i>

              <span>3. Google Veo 3.1 Lite</span>

            </h3>

            <span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">Draft & Credit Saver</span>

          </div>

          <p class="text-xs text-slate-300 leading-relaxed">

            النموذج الاقتصادي الأنسب لتجربة الأفكار ومسارات الكاميرا بدقة درافت (360p / 720p) لتوفير رصيدك من الكريديتس قبل الانتقال للرندرة النهائية بدقة 4K.

          </p>

          <button onclick="activateFromCard('video', 'Google Veo 3.1 Lite')" class="w-full py-1.5 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-200 border border-emerald-500/40 rounded-lg text-xs font-bold transition">

            <i class="fa-solid fa-check"></i> تفعيل في قائمة الفيديو

          </button>

        </div>



        <!-- Gemini Omni Flash 1.1 -->

        <div class="bg-cinema-800/90 border border-purple-500/40 rounded-xl p-4 space-y-2.5 shadow-lg">

          <div class="flex items-center justify-between">

            <h3 class="text-sm font-black text-white flex items-center gap-2">

              <i class="fa-solid fa-brain text-cinema-purple"></i>

              <span>4. Gemini Omni Flash 1.1 (المعدل الحواري)</span>

            </h3>

            <span class="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">Conversational Video</span>

          </div>

          <p class="text-xs text-slate-300 leading-relaxed">

            النموذج الأقوى في التعديل الحواري عبر الأدوار المتتابعة (Multi-Turn). يمكنك تعديل المشهد بعبارات محادثة دون إعادة التوليد من الصفر مع ذاكرة 10 ثوانٍ ودعم 5 صور مرجعية.

          </p>

          <button onclick="activateFromCard('video', 'Gemini Omni Flash 1.1')" class="w-full py-1.5 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 rounded-lg text-xs font-bold transition">

            <i class="fa-solid fa-check"></i> تفعيل في قائمة الفيديو

          </button>

        </div>



      </div>



    </section>



    <!-- ======================================================== -->

    <!-- TAB 3: SCREENING, UPLOAD, EDIT & DOWNLOAD STUDIO -->

    <!-- ======================================================== -->

    <section id="tab-screening" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">

      

      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-3">

        <div>

          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">

            <i class="fa-solid fa-film"></i>

            <span>شاشة العرض واستوديو التعديل والتحريك والنقد الإخراجي</span>

          </h2>

          <p class="text-xs text-slate-400">اعرض لقطاتك، أو ارفع أي صورة/فيديو من جهازك لمناقشته مع سيندي وتعديله أو تحريكه وتنزيله بجودة كاملة.</p>

        </div>



        <div class="flex flex-wrap items-center gap-2">

          <button type="button" onclick="triggerMediaUpload('screening')" class="px-3.5 py-2 rounded-xl bg-cinema-neon/20 hover:bg-cinema-neon/30 text-cyan-300 border border-cinema-neon/50 text-xs font-bold flex items-center gap-1.5 transition shadow">

            <i class="fa-solid fa-cloud-arrow-up"></i>

            <span>رفع صورة / فيديو للتعديل والمناقشة</span>

          </button>



          <button type="button" onclick="syncFromFlowTab()" class="px-3 py-2 rounded-xl bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/40 text-xs font-bold flex items-center gap-1.5 transition shadow" title="سحب الصور أو الفيديوهات المعروضة حالياً داخل تبويب Google Flow المفتوح">

            <i class="fa-solid fa-arrows-rotate"></i>

            <span>جلب من تبويب Flow</span>

          </button>



          <button type="button" onclick="saveCurrentMedia()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-cinema-950 text-xs font-black flex items-center gap-1.5 transition shadow-lg shadow-emerald-500/20">

            <i class="fa-solid fa-download"></i>

            <span>تنزيل اللقطة (Download HD)</span>

          </button>

        </div>

      </div>



      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        

        <div class="lg:col-span-7 flex flex-col gap-3">

          <div class="relative w-full aspect-video bg-cinema-950 border border-cinema-700 rounded-2xl overflow-hidden flex items-center justify-center shadow-2xl" id="screening-viewport">

            <!-- Single Image Display -->

            <img id="screen-img-display" src="https://v3b.fal.media/files/b/0ab07bdc/gUeYYpdkOc7G2XYeuaCEK.jpg" alt="Screening Preview" class="w-full h-full object-cover">

            

            <!-- Video Display -->

            <video id="screen-video-display" src="" controls class="hidden w-full h-full object-cover"></video>



            <!-- Multi-Image Grid Display -->

            <div id="screen-grid-display" class="hidden w-full h-full p-2 grid grid-cols-2 gap-2 overflow-y-auto bg-cinema-950"></div>



            <!-- Loader -->

            <div id="screen-loader" class="hidden absolute inset-0 bg-cinema-950/85 backdrop-blur-md flex flex-col items-center justify-center gap-3 z-20">

              <i class="fa-solid fa-spinner fa-spin text-3xl text-cinema-gold"></i>

              <p class="text-xs font-bold text-slate-200" id="screen-loader-text">سيندي تقوم بالتوليد الفعلي الآن...</p>

            </div>

          </div>



          <div class="bg-cinema-800/80 border border-cinema-700 rounded-xl p-3 text-xs space-y-1.5">

            <div class="flex flex-wrap items-center justify-between gap-2 text-slate-400">

              <span class="font-bold text-cinema-gold"><i class="fa-solid fa-tag"></i> اللقطة النشطة: <span id="screen-model-tag" class="text-cinema-neon font-mono">صورة افتراضية</span></span>

              <div class="flex items-center gap-2">

                <button type="button" onclick="analyzeCurrentScreeningMedia()" class="px-2.5 py-1 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-[11px] font-bold">

                  <i class="fa-solid fa-eye"></i> فحص ونقد اللقطة بالرؤية الذكية

                </button>

                <button type="button" onclick="saveCurrentMedia()" aria-label="تنزيل اللقطة" class="px-3 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-[11px] font-bold">

                  <i class="fa-solid fa-download"></i> تنزيل للجهاز

                </button>

              </div>

            </div>

            <p id="screen-active-prompt" class="font-mono text-amber-200 text-[11px] select-all">cinematic shot of a master falcon with golden eyes perched in desert at twilight, 35mm anamorphic</p>

          </div>



          <!-- AI MEDIA EDITING & IMAGE-TO-VIDEO STUDIO -->

          <div id="media-edit-studio" class="bg-gradient-to-br from-cinema-800/95 to-cinema-900 border border-cinema-gold/50 rounded-2xl p-4 space-y-3 shadow-xl">

            <div class="flex flex-wrap items-center justify-between gap-2 border-b border-cinema-700/70 pb-2">

              <div class="flex items-center gap-2">

                <i class="fa-solid fa-wand-magic-sparkles text-cinema-gold"></i>

                <h3 class="text-xs font-black text-white">استوديو تعديل اللقطة المعروضة أو تحريكها لفيديو (Edit & Image-to-Video)</h3>

              </div>

              <span class="text-[10px] px-2 py-0.5 rounded bg-cinema-gold/20 text-cinema-gold font-bold">يعمل على الصور والفيديوهات المرفوعة والمولدة</span>

            </div>



            <div class="grid grid-cols-1 md:grid-cols-12 gap-2.5">

              <div class="md:col-span-5">

                <label class="block text-[10px] text-slate-400 font-bold mb-1">اختر نوع العملية والمحرك:</label>

                <select id="edit-action-select" class="w-full bg-cinema-950 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs font-bold text-slate-100 focus:outline-none focus:border-cinema-gold">

                  <optgroup label="🎨 تعديل الصورة الحالية مع الحفاظ على التكوين">

                    <option value="edit_image|fal-ai/nano-banana/edit" selected>🍌 تعديل الصورة: Google Nano Banana Edit</option>

                    <option value="edit_image|fal-ai/nano-banana-pro/edit">🍌 تعديل احترافي: Google Nano Banana Pro Edit</option>

                    <option value="edit_image|fal-ai/flux/dev/image-to-image">📸 إعادة رسم سينمائي: FLUX.1 Dev (Image-to-Image)</option>

                  </optgroup>

                  <optgroup label="🎬 تحريك الصورة الحالية إلى فيديو سينمائي (Image-to-Video)">

                    <option value="image_to_video|fal-ai/minimax/video-01/image-to-video">⚡ تحريك اقتصادي فائق السرعة: MiniMax H3 Lite / Hailuo</option>

                    <option value="image_to_video|fal-ai/wan/v2.1/image-to-video">💎 تحريك سينمائي مفتوح المصدر: Wan 2.1 (Alibaba 14B)</option>

                    <option value="image_to_video|fal-ai/cogvideox-5b/image-to-video">🎥 تحريك سينمائي: CogVideoX-5B</option>

                    <option value="image_to_video|fal-ai/hunyuan-video/image-to-video">🎬 تحريك عالي الثبات: Tencent HunyuanVideo</option>

                    <option value="image_to_video|tbc/mischief-1/image-to-video">🔥 تحريك أكشن وديناميكا: Mischief-1 Image-to-Video</option>

                    <option value="image_to_video|blackforestlabs/flux-3-max/image-to-video">🌟 أعلى دقة تفاصيل فوتوغرافية: Flux 3 Max Image-to-Video</option>

                    <option value="image_to_video|minimax/h3-max-turbo/reference-to-video">🎯 قفل ملامح الشخصية المرجعية: MiniMax H3 Max Turbo</option>

                    <option value="image_to_video|fal-ai/kling-video/v1.6/pro/image-to-video">👑 تحريك هوليوودي: Kling 1.6 Pro (I2V)</option>

                    <option value="image_to_video|fal-ai/veo3.1/image-to-video">🌟 تحريك الصورة لفيديو بصوت: Google Veo 3.1 (I2V)</option>

                    <option value="image_to_video|fal-ai/luma-dream-machine/ray-2/image-to-video">🌊 تحريك انسيابي للصورة: Luma Ray 2 (I2V)</option>

                  </optgroup>

                  <optgroup label="🎞️ تعديل الفيديو الحالي أو إضافة صوت وموسيقى">

                    <option value="edit_video|fal-ai/kling-video/o1/video-to-video/edit">🎞️ تعديل الفيديو بالذكاء الاصطناعي: Kling O1 Edit</option>

                    <option value="edit_video|fal-ai/luma-dream-machine/ray-2/modify">🌊 تعديل ستايل الفيديو: Luma Ray 2 Modify</option>

                    <option value="add_audio|fal-ai/mmaudio-v2">🔊 توليد مؤثرات صوتية وموسيقى للفيديو: MMAudio v2</option>

                  </optgroup>

                </select>

              </div>



              <div class="md:col-span-7">

                <label class="block text-[10px] text-slate-400 font-bold mb-1">اكتب التعديل أو حركة الكاميرا المطلوبة (بالعربية أو الإنجليزية):</label>

                <div class="flex gap-2">

                  <input type="text" id="edit-media-prompt" dir="auto" autocomplete="off" autocorrect="off" spellcheck="false" placeholder="مثال: اجعل الإضاءة ليلية ماطرة نيون، أو حرّك الكاميرا للأمام ببطء... (اضغط Enter للتنفيذ)" class="flex-1 bg-cinema-950 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cinema-gold">

                  <button type="button" onclick="executeMediaEdit()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-cinema-gold to-amber-500 hover:from-amber-400 hover:to-yellow-500 text-cinema-950 font-black text-xs flex items-center gap-1.5 shrink-0 shadow-lg">

                    <i class="fa-solid fa-bolt"></i>

                    <span>تنفيذ التعديل</span>

                  </button>

                </div>

              </div>

            </div>

          </div>

        </div>



        <div class="lg:col-span-5 flex flex-col gap-3 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-4 shadow-xl">

          <div class="flex items-center justify-between border-b border-cinema-700/60 pb-2">

            <span class="text-xs font-black text-cinema-gold flex items-center gap-1.5">

              <i class="fa-solid fa-comments-dollar"></i> ملاحظات سيندي الإخراجية:

            </span>

            <span id="critique-badge" class="text-[10px] px-2 py-0.5 rounded bg-cinema-700/60 text-slate-300 font-bold border border-cinema-600/50">جاهز للفحص البصري</span>

          </div>



          <div class="grid grid-cols-3 gap-2 text-center text-xs">

            <div class="bg-cinema-900/80 p-2 rounded-xl border border-cinema-700">

              <span class="text-slate-400 text-[10px] block">حركة الكاميرا</span>

              <span class="text-cinema-neon font-black font-mono" id="critique-score-camera">—</span>

            </div>

            <div class="bg-cinema-900/80 p-2 rounded-xl border border-cinema-700">

              <span class="text-slate-400 text-[10px] block">ثبات العناصر والفيزياء</span>

              <span class="text-emerald-400 font-black font-mono" id="critique-score-physics">—</span>

            </div>

            <div class="bg-cinema-900/80 p-2 rounded-xl border border-cinema-700">

              <span class="text-slate-400 text-[10px] block">الإضاءة والعمق</span>

              <span class="text-amber-400 font-black font-mono" id="critique-score-lighting">—</span>

            </div>

          </div>



          <div class="text-xs text-slate-200 leading-relaxed bg-cinema-900/50 p-3 rounded-xl border border-cinema-700/50" id="critique-analysis-text">

            ستظهر هنا ملاحظات سيندي بعد أول توليد، أو اضغط «فحص ونقد اللقطة بالرؤية الذكية» بالأسفل لتشغيل فحص حقيقي بكسل-بكسل عبر محرك Google Gemini Vision.

          </div>



          <div class="space-y-2">

            <span class="text-[11px] font-bold text-slate-300 flex items-center gap-1">

              <i class="fa-solid fa-question-circle text-cinema-purple"></i> مقترحات سيندي للمناقشة وتطوير المشهد:

            </span>

            <div class="space-y-1.5" id="critique-questions-box">

              <button onclick="handleDiscussionChoice('slow_motion')" class="w-full text-right p-2 rounded-lg bg-cinema-700/50 hover:bg-cinema-700 border border-cinema-600/60 text-xs text-slate-200 transition">

                🎬 هل تفضل إبطاء الحركة بنسبة 20% لتكون Slow Motion؟

              </button>

              <button onclick="handleDiscussionChoice('next_shot')" class="w-full text-right p-2 rounded-lg bg-cinema-700/50 hover:bg-cinema-700 border border-cinema-600/60 text-xs text-slate-200 transition">

                ➡️ هل نعتمد هذه النتيجة وننتقل فوراً لتوليد اللقطة التالية في التايم لاين؟

              </button>

            </div>

          </div>

        </div>



      </div>



    </section>



    <!-- ======================================================== -->

    <!-- TAB 4: SECURE VAULT -->

    <!-- ======================================================== -->
    <!-- TAB 4: ZERO-LEAK LOCAL VAULT -->
    <!-- ======================================================== -->
    <section id="tab-vault" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">

      <!-- Vault Header -->
      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-yellow-600 flex items-center justify-center text-cinema-950 font-black text-2xl shadow-xl">
            <i class="fa-solid fa-vault"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-black text-cinema-gold">
                الخزنة السحابية المؤمنة (Zero-Leak Local Vault)
              </h2>
              <span class="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1">
                <i class="fa-solid fa-shield-halved text-emerald-400"></i> تشفير محلي 100%
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">
              مفاتيح الربط والـ APIs مخزنة محلياً ومشفرة في جهازك (127.0.0.1) ولا تخرج لأي خادم وسيط.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button type="button" onclick="loadVaultStatus()" class="px-3.5 py-1.5 rounded-xl bg-cinema-800 hover:bg-cinema-700 border border-cinema-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 transition cursor-pointer shadow">
            <i class="fa-solid fa-arrows-rotate text-[11px]" id="vault-refresh-icon"></i>
            <span>تحديث حالة الخزنة</span>
          </button>
        </div>
      </div>

      <!-- Quick Search / Filter Bar -->
      <div class="flex items-center justify-between gap-4 bg-cinema-950/80 p-3 rounded-xl border border-cinema-800">
        <div class="flex-1 max-w-md relative">
          <input type="text" id="vault-search-input" oninput="filterVault()" placeholder="ابحث في مفاتيح الخدمات (Fal, RunPod, Gemini, HuggingFace)..." class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cinema-gold pl-9">
          <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
        </div>
        <div class="text-xs text-slate-400 hidden sm:flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span>الحفظ يطبق فوراً في ملف <code class="bg-cinema-900 px-1.5 py-0.5 rounded text-amber-300 font-mono">cindy_secrets.json</code></span>
        </div>
      </div>

      <!-- Vault Services Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="vault-services-grid">
        <!-- Dynamically populated by renderVaultCards() -->
      </div>

    </section>





    <!-- ======================================================== -->

    <!-- TAB 5: LORA TRAINING & INFERENCE STUDIO -->

    <!-- ======================================================== -->

    <section id="tab-lora" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">

      <!-- LoRA Header -->

      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-4">

        <div>

          <div class="flex items-center gap-2.5">

            <h2 class="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-300 to-cinema-gold font-cinzel">

              استوديو تدريب ونماذج LoRA السينمائية

            </h2>

            <span class="text-[10px] px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-bold border border-purple-500/40">

              FLUX.1 [dev] Fine-Tuning

            </span>

          </div>

          <p class="text-xs text-slate-400 mt-1">

            درّب شخصياتك وممثليك أو ستايلك البصري المخصص بدقة 100%، ونفّذ التوليد بهم فوراً، ونزّل ملف الأوزان (.safetensors) بجودة كاملة.

          </p>

        </div>



        <!-- LoRA Subtab Switcher -->

        <div class="flex items-center bg-cinema-900/90 p-1 rounded-xl border border-cinema-700/80 text-xs font-bold">

          <button type="button" onclick="switchLoraSubtab('train')" id="lora-tabbtn-train" class="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow transition flex items-center gap-1.5">

            <i class="fa-solid fa-graduation-cap"></i> تدريب LoRA جديد

          </button>

          <button type="button" onclick="switchLoraSubtab('library')" id="lora-tabbtn-library" class="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center gap-1.5">

            <i class="fa-solid fa-layer-group text-purple-400"></i> مكتبة النماذج والتنزيل

          </button>

          <button type="button" onclick="switchLoraSubtab('generate')" id="lora-tabbtn-generate" class="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-white transition flex items-center gap-1.5">

            <i class="fa-solid fa-bolt text-yellow-400"></i> توليد وتجربة LoRA

          </button>

        </div>

      </div>



      <!-- VIEW 1: TRAIN NEW LORA -->

      <div id="lora-view-train" class="space-y-6">

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          

          <!-- Training Parameters Form -->

          <div class="lg:col-span-5 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg">

            <h3 class="text-sm font-bold text-cinema-gold flex items-center gap-2 border-b border-cinema-700/60 pb-2">

              <i class="fa-solid fa-sliders"></i> إعدادات الموديل والتدريب

            </h3>



            <!-- Training Backend Engine Selector -->

            <div class="space-y-1.5 bg-cinema-900/90 p-3 rounded-xl border border-cinema-700">

              <label class="text-xs font-bold text-cinema-gold flex items-center gap-1.5">

                <i class="fa-solid fa-microchip"></i> بيئة التدريب السحابية (Training Engine):

              </label>

              <div class="space-y-2">

                <label class="flex items-start gap-2.5 p-2 rounded-lg bg-cinema-950/80 border border-purple-500/50 cursor-pointer hover:border-purple-400 transition">

                  <input type="radio" name="lora-train-backend" value="runpod" checked onchange="toggleTrainEngine('runpod')" class="mt-0.5 accent-purple-500">

                  <div class="flex-1 text-xs">

                    <div class="flex items-center justify-between">

                      <span class="font-bold text-white flex items-center gap-1.5">

                        <i class="fa-solid fa-server text-purple-400"></i> RunPod Cloud Computer (الموصى به - توفير 95%)

                      </span>

                      <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono font-bold">~ $0.04 للموديل</span>

                    </div>

                    <p class="text-[11px] text-slate-300 mt-1">يُشغل كارت RTX 4090 لحسابك الشخصي، يدرب الموديل، <strong>ويُغلق وينهي السيرفر فوراً</strong> بمجرد الانتهاء لتوفير كل سنت!</p>

                  </div>

                </label>



                <label class="flex items-start gap-2.5 p-2 rounded-lg bg-cinema-950/40 border border-cinema-800 cursor-pointer hover:border-cinema-700 transition">

                  <input type="radio" name="lora-train-backend" value="fal" onchange="toggleTrainEngine('fal')" class="mt-0.5 accent-amber-500">

                  <div class="flex-1 text-xs">

                    <div class="flex items-center justify-between">

                      <span class="font-bold text-slate-300 flex items-center gap-1.5">

                        <i class="fa-solid fa-bolt text-amber-400"></i> Fal.ai Fast API (مدفوع)

                      </span>

                      <span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded font-mono font-bold">$2.00 - $4.00</span>

                    </div>

                    <p class="text-[11px] text-slate-400 mt-0.5">سيرفرات جاهزة لكنها تستهلك من رصيد Fal.ai المسجل في خزنتك.</p>

                  </div>

                </label>

              </div>



              <!-- RunPod Specific Controls -->

              <div id="runpod-train-config" class="space-y-2 pt-2 border-t border-cinema-800">

                <div class="flex items-center justify-between text-[11px]">

                  <span class="text-slate-200 font-bold">نوع كارت الشاشة (RunPod GPU):</span>

                  <span class="text-purple-300 font-mono text-[10px]">إيقاف وحذف تلقائي فوري 100%</span>

                </div>

                <select id="runpod-gpu-select" class="w-full bg-cinema-950 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-white focus:outline-none focus:border-purple-400">

                  <option value="NVIDIA GeForce RTX 4090" selected>⚡ NVIDIA RTX 4090 (24GB VRAM) - $0.34/hr (~4 سنت فقط! سرعة فائقة)</option>

                  <option value="NVIDIA A40">👑 NVIDIA A40 (48GB VRAM) - $0.35/hr (~5 سنت لأوزان كاملة)</option>

                  <option value="NVIDIA A100 80GB PCIe">🚀 NVIDIA A100 (80GB VRAM) - $1.19/hr (الأسرع عالمياً)</option>

                </select>



                <div class="flex items-center justify-between pt-1">

                  <button type="button" onclick="terminateAllRunpodPods()" class="px-2.5 py-1 bg-rose-900/40 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300 rounded text-[10px] font-bold">

                    <i class="fa-solid fa-power-off"></i> إيقاف وحذف أي أجهزة RunPod معلقة فوراً

                  </button>

                  <button type="button" onclick="switchTab('vault')" class="text-[10px] text-cinema-gold hover:underline">

                    <i class="fa-solid fa-key"></i> ضبط مفتاح RunPod في الخزنة

                  </button>

                </div>

              </div>

            </div>



            <!-- Model Name -->

            <div class="space-y-1">

              <label class="text-xs font-bold text-slate-300">اسم الموديل / الشخصية:</label>

              <input type="text" id="lora-train-name" dir="auto" autocomplete="off" autocorrect="off" placeholder="مثال: البطل أحمد - كاجوال" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-400">

            </div>



            <!-- Trigger Word -->

            <div class="space-y-1">

              <div class="flex items-center justify-between">

                <label class="text-xs font-bold text-slate-300">كلمة التفعيل (Trigger Word):</label>

                <span class="text-[10px] text-purple-300">تُكتب في البرومبت لاستدعاء الموديل</span>

              </div>

              <input type="text" id="lora-train-trigger" dir="ltr" spellcheck="false" autocomplete="off" autocorrect="off" placeholder="مثال: sks_ahmed أو cindy_actor" class="w-full font-mono bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-amber-200 focus:outline-none focus:border-purple-400">

            </div>



            <!-- LoRA Type -->

            <div class="space-y-1">

              <label class="text-xs font-bold text-slate-300">نوع النموذج (LoRA Type):</label>

              <select id="lora-train-type" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-400">

                <option value="character" selected>👤 شخصية / ممثل / كائن محدد (Subject / Character)</option>

                <option value="style">🎨 أسلوب وستايل بصري / إخراجي (Artistic Style)</option>

              </select>

            </div>



            <!-- Training Steps -->

            <div class="space-y-1">

              <label class="text-xs font-bold text-slate-300">خطوات التدريب (Training Steps):</label>

              <select id="lora-train-steps" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-400">

                <option value="500">500 خطوة (سريع واقتصادي / معاينة درافت)</option>

                <option value="1000" selected>1000 خطوة (موصى به: دقة متوازنة وثبات ملامح عالي)</option>

                <option value="1500">1500 خطوة (فائق الدقة للأزياء والأقمشة الدقيقة)</option>

              </select>

            </div>



            <!-- Auto-captioning toggle -->

            <div class="flex items-center gap-2 bg-cinema-900/80 p-3 rounded-xl border border-cinema-700/60">

              <input type="checkbox" id="lora-train-autocaption" checked class="w-4 h-4 accent-purple-500 rounded cursor-pointer">

              <label for="lora-train-autocaption" class="text-xs text-slate-200 cursor-pointer font-semibold">

                ✨ وصف وتصنيف ذكي للصور تلقائياً عبر Cindy Gemini Vision (Auto-Captioning)

              </label>

            </div>



            <!-- Action Button -->

            <button type="button" onclick="startLoraTraining()" id="lora-start-train-btn" class="w-full py-3 bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 hover:opacity-95 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-500/25 transition">

              <i class="fa-solid fa-rocket"></i>

              <span>بدء التدريب السحابي الآن (FLUX.1 [dev] Fast LoRA)</span>

            </button>

          </div>



          <!-- Dataset Images Upload & Gallery -->

          <div class="lg:col-span-7 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg flex flex-col">

            <div class="flex items-center justify-between border-b border-cinema-700/60 pb-2">

              <h3 class="text-sm font-bold text-cinema-gold flex items-center gap-2">

                <i class="fa-solid fa-images"></i> حزمة صور التدريب (Dataset)

              </h3>

              <span id="lora-images-count-badge" class="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">0 صور مختارة</span>

            </div>



            <!-- Drop Zone -->

            <div onclick="document.getElementById('lora-files-input').click()" class="border-2 border-dashed border-purple-500/40 hover:border-purple-400 bg-cinema-900/60 rounded-xl p-6 text-center cursor-pointer transition group">

              <input type="file" id="lora-files-input" multiple accept="image/*,.zip" class="hidden" onchange="handleLoraFilesSelected(event)">

              <div class="w-12 h-12 mx-auto rounded-full bg-purple-500/10 group-hover:bg-purple-500/20 text-purple-400 flex items-center justify-center mb-2 transition">

                <i class="fa-solid fa-cloud-arrow-up text-xl"></i>

              </div>

              <p class="text-xs font-bold text-slate-200">اسحب وأفلت صور الشخصية/الستايل هنا، أو انقر للاختيار من جهازك</p>

              <p class="text-[11px] text-slate-400 mt-1">يُوصى بـ 4 إلى 15 صورة واضحة بزوايا وإضاءات متنوعة، أو ملف .zip مباشرة</p>

            </div>



            <!-- Thumbnails Preview Grid -->

            <div id="lora-thumbs-container" class="flex-1 min-h-[160px] max-h-[280px] overflow-y-auto p-2 bg-cinema-950/60 border border-cinema-800 rounded-xl grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2.5">

              <div class="col-span-full h-full flex flex-col items-center justify-center text-slate-500 text-xs py-8">

                <i class="fa-solid fa-image text-2xl mb-1 text-slate-600"></i>

                <span>لم يتم اختيار صور تدريب بعد</span>

              </div>

            </div>



            <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">

              <span>💡 نصيحة سيندي: الصور ذات الإضاءات والخلفيات المتنوعة تعطي ثباتاً هوليوودياً فائقاً للوجه.</span>

              <button type="button" onclick="clearLoraDataset()" class="text-rose-400 hover:underline">مسح الكل</button>

            </div>

          </div>



        </div>



        <!-- Training Active Monitor Card -->

        <div id="lora-training-monitor" class="hidden bg-cinema-800/90 border-2 border-purple-500/60 rounded-2xl p-5 shadow-2xl space-y-4 animate-fade-in">

          <div class="flex items-center justify-between border-b border-cinema-700/80 pb-3">

            <div class="flex items-center gap-3">

              <div class="w-9 h-9 rounded-xl bg-purple-600/30 text-purple-300 flex items-center justify-center animate-spin">

                <i class="fa-solid fa-gear text-lg"></i>

              </div>

              <div>

                <h4 id="lora-monitor-title" class="text-sm font-bold text-white">جاري تدريب النموذج: ...</h4>

                <p id="lora-monitor-sub" class="text-xs text-purple-300 font-mono">ID: ... | Trigger: ...</p>

              </div>

            </div>

            <div class="flex items-center gap-2">

              <span id="lora-monitor-timer" class="font-mono text-xs text-cinema-gold bg-black/40 px-2.5 py-1 rounded-lg border border-cinema-700">00:00</span>

              <span id="lora-monitor-status-badge" class="text-xs px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-bold border border-purple-500/40">في الطابور السحابي ⏳</span>

            </div>

          </div>



          <!-- Progress Bar -->

          <div class="w-full bg-cinema-950 rounded-full h-2.5 overflow-hidden border border-cinema-700">

            <div id="lora-monitor-progress-bar" class="bg-gradient-to-r from-purple-500 via-pink-500 to-cinema-gold h-full w-5 transition-all duration-500"></div>

          </div>



          <!-- Live Logs Terminal -->

          <div class="bg-cinema-950 p-3 rounded-xl border border-cinema-800 font-mono text-[11px] text-slate-300 space-y-1 max-h-36 overflow-y-auto" id="lora-monitor-logs">

            <div class="text-purple-400">[Cindy LoRA Engine] تم حزم البيانات وإرسالها إلى كروت التدريب السحابية...</div>

          </div>



          <!-- Completion Actions (Hidden until finished) -->

          <div id="lora-monitor-completed-actions" class="hidden pt-2 flex flex-wrap gap-3 items-center justify-between bg-emerald-500/10 border border-emerald-500/30 p-3.5 rounded-xl">

            <div class="flex items-center gap-2 text-emerald-300 text-xs font-bold">

              <i class="fa-solid fa-circle-check text-base text-emerald-400"></i>

              <span>اكتمل تدريب الـ LoRA بنجاح! الأوزان جاهزة للاستخدام والتنزيل.</span>

            </div>

            <div class="flex items-center gap-2">

              <button type="button" id="lora-completed-download-btn" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow">

                <i class="fa-solid fa-download"></i> تنزيل ملف الأوزان (.safetensors)

              </button>

              <button type="button" id="lora-completed-generate-btn" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-95 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow">

                <i class="fa-solid fa-bolt"></i> توليد فوري بهذا الموديل

              </button>

            </div>

          </div>

        </div>

      </div>



      <!-- VIEW 2: LORA LIBRARY & DOWNLOADS -->

      <div id="lora-view-library" class="hidden space-y-4">

        <div class="flex flex-wrap items-center justify-between gap-3 bg-cinema-800/60 p-3.5 rounded-xl border border-cinema-700">

          <div class="text-xs text-slate-300 font-bold flex items-center gap-2">

            <i class="fa-solid fa-box-archive text-purple-400"></i>

            <span>نماذج LoRA الخاصة بك المحفوظة في سيندي:</span>

          </div>

          <div class="flex items-center gap-2">

            <button type="button" onclick="refreshLoraLibrary()" class="px-3 py-1.5 rounded-lg bg-cinema-700 hover:bg-cinema-600 text-xs font-bold text-slate-200 flex items-center gap-1">

              <i class="fa-solid fa-arrows-rotate"></i> تحديث

            </button>

            <button type="button" onclick="toggleImportLoraModal()" class="px-3 py-1.5 rounded-lg bg-purple-600/30 hover:bg-purple-600/40 border border-purple-500/50 text-xs font-bold text-purple-200 flex items-center gap-1">

              <i class="fa-solid fa-plus"></i> استيراد LoRA خارجي (Civitai / URL)

            </button>

          </div>

        </div>



        <!-- Import Modal / Inline Card -->

        <div id="lora-import-card" class="hidden bg-cinema-900 border border-purple-500/50 rounded-xl p-4 space-y-3">

          <h4 class="text-xs font-bold text-purple-300">استيراد نموذج LoRA خارجي (ملف .safetensors مباشر):</h4>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">

            <input type="text" id="lora-import-name" placeholder="اسم الموديل" class="bg-cinema-950 border border-cinema-700 rounded-lg px-3 py-1.5 text-xs text-slate-100">

            <input type="text" id="lora-import-trigger" placeholder="كلمة التفعيل (Trigger Word)" class="bg-cinema-950 border border-cinema-700 rounded-lg px-3 py-1.5 text-xs text-amber-200 font-mono" dir="ltr">

            <input type="url" id="lora-import-url" placeholder="رابط مباشر https://.../model.safetensors" class="bg-cinema-950 border border-cinema-700 rounded-lg px-3 py-1.5 text-xs text-slate-100" dir="ltr">

          </div>

          <div class="flex justify-end gap-2">

            <button type="button" onclick="toggleImportLoraModal()" class="px-3 py-1 bg-cinema-800 text-slate-400 rounded text-xs">إلغاء</button>

            <button type="button" onclick="submitImportLora()" class="px-4 py-1 bg-purple-600 text-white rounded text-xs font-bold">إضافة للمكتبة</button>

          </div>

        </div>



        <!-- LoRA Cards Grid -->

        <div id="lora-library-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

          <!-- Populated by JS -->

        </div>

      </div>



      <!-- VIEW 3: LORA GENERATE & TEST -->

      <div id="lora-view-generate" class="hidden space-y-6">

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          

          <!-- Generator Controls -->

          <div class="lg:col-span-5 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg">

            <h3 class="text-sm font-bold text-cinema-gold flex items-center gap-2 border-b border-cinema-700/60 pb-2">

              <i class="fa-solid fa-wand-magic-sparkles"></i> توليد مشهد بنموذج LoRA (صورة أو فيديو)

            </h3>



            <!-- Mode Switcher: Image vs Video -->

            <div class="space-y-1">

              <label class="text-xs font-bold text-slate-300">نوع المخرج السينمائي (Output Media):</label>

              <div class="grid grid-cols-2 gap-2 bg-cinema-950 p-1.5 rounded-xl border border-cinema-700">

                <button type="button" id="lora-mode-btn-image" onclick="setLoraGenMode('image')" class="py-2 px-3 rounded-lg font-bold text-xs flex items-center justify-center gap-2 transition bg-purple-600 text-white shadow-md">

                  <i class="fa-solid fa-camera"></i>

                  <span>صورة مفتاحية (Image)</span>

                </button>

                <button type="button" id="lora-mode-btn-video" onclick="setLoraGenMode('video')" class="py-2 px-3 rounded-lg font-bold text-xs flex items-center justify-center gap-2 transition text-slate-400 hover:text-white hover:bg-cinema-800">

                  <i class="fa-solid fa-clapperboard text-amber-400"></i>

                  <span>فيديو سينمائي متحرك (Video)</span>

                </button>

              </div>

            </div>



            <!-- Select LoRA -->

            <div class="space-y-1">

              <label class="text-xs font-bold text-slate-300">اختر نموذج LoRA المطبق:</label>

              <select id="lora-gen-select" onchange="onLoraSelectChanged()" class="w-full bg-cinema-900 border border-purple-500/50 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-400">

                <option value="">-- اختر LoRA من مكتبتك --</option>

              </select>

            </div>



            <!-- Custom URL fallback -->

            <div class="space-y-1">

              <label class="text-[11px] text-slate-400">أو أدخل رابط أوزان (.safetensors) مباشرة:</label>

              <input type="text" id="lora-gen-custom-url" placeholder="https://.../model.safetensors" class="w-full font-mono bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-1.5 text-xs text-slate-200" dir="ltr" spellcheck="false">

            </div>



            <!-- Video Controls (Visible when mode is video) -->

            <div id="lora-video-controls" class="hidden space-y-3 bg-cinema-900/90 border border-purple-500/40 rounded-xl p-3.5 shadow-inner">

              <div class="flex items-center justify-between border-b border-cinema-700/60 pb-1.5">

                <span class="text-xs font-bold text-cinema-gold flex items-center gap-1.5">

                  <i class="fa-solid fa-video"></i> إعدادات تحريك فيديو LoRA

                </span>

                <span class="text-[10px] text-purple-300 bg-purple-950/80 px-2 py-0.5 rounded border border-purple-500/30">Two-Stage SOTA</span>

              </div>



              <div class="space-y-1">

                <label class="text-[11px] font-bold text-slate-300">محرك تحريك الفيديو (Video Engine):</label>

                <select id="lora-video-engine-select" class="w-full bg-cinema-950 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-cinema-gold">

                  <option value="kling-1.6-pro" selected>👑 Kling 1.6 / 3.0 Pro (الأعلى دقة وثبات لملامح الوجه السينمائي)</option>

                  <option value="minimax-h3">⚡ MiniMax Hailuo 01 (حركة ناعمة وانفعالات ديناميكية حية)</option>

                  <option value="luma-ray2">🌊 Luma Ray 2 Dream Machine (حركة كاميرا ثلاثية الأبعاد سلسة)</option>

                </select>

              </div>



              <div class="space-y-1">

                <label class="text-[11px] font-bold text-slate-300">مدة الفيديو (Duration):</label>

                <select id="lora-video-duration-select" class="w-full bg-cinema-950 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">

                  <option value="5" selected>5 ثوانٍ (سريع / لقطة تأسيسية)</option>

                  <option value="10">10 ثوانٍ (مشهد كامل ممتد)</option>

                </select>

              </div>



              <div class="space-y-1">

                <label class="text-[11px] font-bold text-slate-300">توجيه حركة الكاميرا والتمثيل (اختياري):</label>

                <input type="text" id="lora-video-motion-prompt" dir="auto" placeholder="مثال: Slow push-in cinematic camera movement, realistic subtle head turn and natural eye blinking" class="w-full bg-cinema-950 border border-cinema-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-400">

              </div>

            </div>



            <!-- Scale Slider -->

            <div class="space-y-1.5 bg-cinema-900/80 p-3 rounded-xl border border-cinema-700">

              <div class="flex items-center justify-between text-xs font-bold">

                <span class="text-slate-300">قوة تأثير الـ LoRA (Scale):</span>

                <span id="lora-scale-val" class="font-mono text-purple-300">1.0</span>

              </div>

              <input type="range" id="lora-gen-scale" min="0.1" max="1.5" step="0.05" value="1.0" oninput="document.getElementById('lora-scale-val').innerText = this.value" class="w-full accent-purple-500">

            </div>



            <!-- Prompt -->

            <div class="space-y-1">

              <div class="flex items-center justify-between">

                <label class="text-xs font-bold text-slate-300">البرومبت السينمائي للمشهد:</label>

                <button type="button" onclick="insertLoraTriggerToPrompt()" class="text-[10px] text-purple-300 hover:underline">

                  <i class="fa-solid fa-plus"></i> إدراج كلمة التفعيل

                </button>

              </div>

              <textarea id="lora-gen-prompt" rows="3" dir="auto" spellcheck="false" placeholder="اكتب وصف اللقطة بالعربية أو الإنجليزية، وسيتم تطبيق ملامح الموديل عليها فوراً... (اضغط Ctrl+Enter للتوليد الفوري)" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-purple-400 leading-relaxed"></textarea>

            </div>



            <!-- Aspect and Count -->

            <div class="grid grid-cols-2 gap-3">

              <div class="space-y-1">

                <label class="text-xs font-bold text-slate-300">الأبعاد:</label>

                <select id="lora-gen-aspect" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">

                  <option value="landscape_16_9" selected>16:9 (عريض)</option>

                  <option value="portrait_9_16">9:16 (عمودي / Reels)</option>

                  <option value="square_hd">1:1 (مربع)</option>

                  <option value="landscape_21_9">21:9 (سينما سكوب)</option>

                </select>

              </div>

              <div id="lora-image-count-container" class="space-y-1">

                <label class="text-xs font-bold text-slate-300">عدد الصور:</label>

                <select id="lora-gen-count" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">

                  <option value="1" selected>1 صورة</option>

                  <option value="2">2 صورتين</option>

                  <option value="4">4 صور (Grid)</option>

                </select>

              </div>

            </div>



            <button type="button" onclick="executeLoraGeneration()" id="lora-exec-btn" class="w-full py-3 bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 hover:opacity-95 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-500/25 transition">

              <i class="fa-solid fa-bolt" id="lora-exec-btn-icon"></i>

              <span id="lora-exec-btn-text">توليد اللقطة بنموذج LoRA المخصص</span>

            </button>

          </div>



          <!-- Generated Results Gallery -->

          <div class="lg:col-span-7 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg flex flex-col">

            <div class="flex items-center justify-between border-b border-cinema-700/60 pb-2">

              <h3 class="text-sm font-bold text-cinema-gold flex items-center gap-2">

                <i class="fa-solid fa-photo-film"></i> نتائج توليد LoRA

              </h3>

              <span id="lora-results-tag" class="text-[10px] text-slate-400">جاهز للتوليد</span>

            </div>



            <div id="lora-gen-output-box" class="flex-1 min-h-[300px] bg-cinema-950/80 border border-cinema-800 rounded-xl flex items-center justify-center p-4 relative overflow-hidden">

              <div id="lora-gen-placeholder" class="text-center text-slate-500 space-y-2">

                <i class="fa-solid fa-wand-magic text-3xl text-purple-500/40"></i>

                <p class="text-xs">اختر نموذج LoRA، واكتب المشهد واضغط توليد لعرض النتيجة الفورية هنا</p>

              </div>

              <div id="lora-gen-spinner" class="hidden text-center space-y-2">

                <i class="fa-solid fa-circle-notch fa-spin text-3xl text-purple-400"></i>

                <p id="lora-spinner-text" class="text-xs font-bold text-purple-300">سيندي تولد اللقطة وتطبق ملامح الـ LoRA في السحابة...</p>

              </div>

              <div id="lora-gen-results-grid" class="hidden w-full h-full grid grid-cols-1 sm:grid-cols-2 gap-3"></div>

              <div id="lora-gen-results-video" class="hidden w-full space-y-3"></div>

            </div>

          </div>



        </div>

      </div>

    </section>



  

    <!-- Tab: ComfyUI Studio (Zero Nodes, Pure Cinema) -->

    <section id="tab-comfy" class="hidden flex flex-col space-y-4 pb-12">

      <!-- Status & Cloud Controls Banner -->

      <div class="bg-cinema-800/80 border border-cinema-700 rounded-2xl p-4 shadow-lg flex flex-wrap items-center justify-between gap-3">

        <div class="flex items-center gap-3">

          <div class="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center text-lg">

            <i class="fa-solid fa-bolt"></i>

          </div>

          <div>

            <div class="flex items-center gap-2">

              <h2 class="text-sm font-bold text-slate-100">استوديو ComfyUI السينمائي (تحكم كامل بدون أسلاك)</h2>

              <span id="comfy-status-badge" class="text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 flex items-center gap-1">

                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>

                <span id="comfy-status-text">متصل (NVIDIA RTX PRO 4000 Blackwell)</span>

              </span>

            </div>

            <p id="comfy-status-sub" class="text-[11px] text-slate-400 mt-0.5 font-mono">

              24.9 GB VRAM متاحة | سرعة ريندر فائقة (2 إلى 4 ثوانٍ فقط) | صفر تكلفة API

            </p>

          </div>

        </div>



        <div class="flex flex-wrap items-center gap-2.5">

          <!-- Cloud Pod Controls (Always Visible & Accessible) -->
          <div class="flex items-center gap-2 flex-wrap">
            <select id="comfy-gpu-select" class="bg-cinema-900 border border-cinema-700 text-slate-200 text-xs rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-emerald-400">
              <option value="NVIDIA GeForce RTX 4090" selected>⚡ RTX 4090 (24GB VRAM) - ~$0.34/ساعة</option>
              <option value="NVIDIA RTX PRO 4500 Blackwell Server Edition">🚀 Blackwell PRO 4500 (32GB VRAM) - ~$0.50/ساعة</option>
            </select>

            <button type="button" onclick="launchComfyStudioPod()" id="comfy-launch-btn" class="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 hover:opacity-95 text-white text-xs font-extrabold shadow-lg shadow-emerald-500/20 transition flex items-center gap-1.5">
              <i class="fa-solid fa-rocket"></i>
              <span id="comfy-launch-btn-text">تشغيل الاستوديو السحابي</span>
            </button>

            <button type="button" onclick="emergencyStopAllRunpod(true)" id="comfy-always-stop-btn" class="px-4 py-2 rounded-xl bg-gradient-to-r from-rose-800 via-rose-700 to-red-600 hover:from-rose-700 hover:to-red-500 text-white text-xs font-black shadow-lg shadow-rose-950/40 border border-rose-500/40 transition flex items-center gap-1.5 cursor-pointer">
              <i class="fa-solid fa-power-off"></i>
              <span>🛑 إيقاف وحذف سيرفر RunPod فوراً (حماية الرصيد)</span>
            </button>

            <button type="button" onclick="checkComfyStatus(true)" class="px-3 py-2 rounded-xl bg-cinema-900 hover:bg-cinema-700 text-slate-300 border border-cinema-700 text-xs font-bold transition flex items-center gap-1">
              <i class="fa-solid fa-arrows-rotate"></i>
              <span>تحديث الحالة</span>
            </button>
          </div>

          <!-- When in Dedicated Mode (Kling Motion Control / LatentSync) -->

          <div id="comfy-serverless-controls" class="hidden flex items-center gap-2">

            <span class="px-3.5 py-1.5 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs font-bold flex items-center gap-2 shadow">

              <i class="fa-solid fa-bolt text-purple-400"></i>

              <span>محرك سيرفرلس مباشر (Fal AI) - جاهز فوراً بدون حجز كروت وبدون أي انتظار</span>

            </span>

          </div>



          <!-- When Online: Stop & Refresh Controls -->

          <div id="comfy-online-controls" class="hidden flex items-center gap-2">

            <button type="button" onclick="checkComfyStatus(true)" class="px-3 py-1.5 rounded-xl bg-cinema-900 hover:bg-cinema-700 text-slate-300 border border-cinema-700 text-xs font-bold transition flex items-center gap-1.5">

              <i class="fa-solid fa-arrows-rotate"></i>

              <span>تحديث الحالة</span>

            </button>

            <button type="button" onclick="stopComfyStudioPod()" class="px-3 py-1.5 rounded-xl bg-rose-900/50 hover:bg-rose-900/80 text-rose-200 border border-rose-500/40 text-xs font-extrabold transition flex items-center gap-1.5 shadow-md shadow-rose-900/20">

              <i class="fa-solid fa-power-off"></i>

              <span>إيقاف السيرفر السحابي فوراً (لحماية الرصيد)</span>

            </button>

          </div>

        </div>

      </div>



      <!-- Main Studio Form & Controls -->

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1">

        <!-- Director Controls (Left 5 cols) -->

        <div class="lg:col-span-5 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg flex flex-col">

          <div class="space-y-3.5">

            <div class="flex items-center justify-between border-b border-cinema-700 pb-2">

              <!-- Open-Source Direct Model Selection Hub (حرية كاملة لاختيار كل نموذج مفتوح المصدر بشكل مستقل) -->
              <div class="space-y-3 p-3.5 bg-black/50 border border-cinema-800 rounded-xl mb-3 shadow-inner">
                <div class="flex items-center justify-between border-b border-cinema-800/80 pb-2">
                  <div class="flex items-center gap-2">
                    <i class="fa-solid fa-cubes text-amber-400 text-sm"></i>
                    <span class="text-xs font-bold text-white">اختر المحرك والنموذج مفتوح المصدر المستقل مباشرة:</span>
                  </div>
                  <span class="text-[10px] text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 font-bold">كل نموذج مستقل بإعداداته</span>
                </div>

                <!-- 1. محركات الفيديو مفتوحة المصدر -->
                <div class="space-y-1.5">
                  <div class="text-[10px] text-amber-300 font-bold flex items-center gap-1.5">
                    <i class="fa-solid fa-film text-amber-400"></i>
                    <span>🎬 محركات الفيديو السينمائي مفتوحة المصدر (Video Diffusion Engines):</span>
                  </div>
                  <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
                    <!-- Wan 2.2 -->
                    <button type="button" onclick="selectDirectComfyModel('wan22')" id="btn-engine-wan22" class="p-2 rounded-lg bg-amber-500/20 border-2 border-amber-400 text-right transition flex flex-col justify-between shadow">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-amber-200">Alibaba Wan 2.2</span>
                        <span class="text-[9px] px-1 py-0.2 bg-amber-500/30 text-amber-200 rounded font-mono font-bold">14B</span>
                      </div>
                      <div class="text-[10px] text-slate-300 font-sans">فائق الحركية والفيزياء 720p</div>
                    </button>

                    <!-- Wan 2.1 -->
                    <button type="button" onclick="selectDirectComfyModel('wan21')" id="btn-engine-wan21" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-amber-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-amber-300">Alibaba Wan 2.1</span>
                        <span class="text-[9px] px-1 py-0.2 bg-blue-500/20 text-blue-300 rounded font-mono">14B</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">ثبات سينمائي عالي 720p</div>
                    </button>

                    <!-- HunyuanVideo -->
                    <button type="button" onclick="selectDirectComfyModel('hunyuan')" id="btn-engine-hunyuan" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-purple-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-purple-300">Tencent Hunyuan</span>
                        <span class="text-[9px] px-1 py-0.2 bg-purple-500/20 text-purple-300 rounded font-mono">13B</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">عملاق هوليوودي 24fps</div>
                    </button>

                    <!-- CogVideoX -->
                    <button type="button" onclick="selectDirectComfyModel('cogvideox')" id="btn-engine-cogvideo" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-emerald-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-emerald-300">THUDM CogVideoX</span>
                        <span class="text-[9px] px-1 py-0.2 bg-emerald-500/20 text-emerald-300 rounded font-mono">5B</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">ثبات ودقة سينمائية</div>
                    </button>

                    <!-- SVD-XT -->
                    <button type="button" onclick="selectDirectComfyModel('svd')" id="btn-engine-svd" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-sky-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-sky-300">Stability SVD-XT</span>
                        <span class="text-[9px] px-1 py-0.2 bg-sky-500/20 text-sky-300 rounded font-mono">خفيف</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">حركة سريعة مدمجة 576p</div>
                    </button>
                  </div>
                </div>

                <!-- 2. محركات التصوير الفوتوغرافي مفتوحة المصدر -->
                <div class="space-y-1.5 pt-1">
                  <div class="text-[10px] text-emerald-300 font-bold flex items-center gap-1.5">
                    <i class="fa-solid fa-camera-retro text-emerald-400"></i>
                    <span>📸 محركات التصوير الفوتوغرافي المستقلة (Image Generation Engines):</span>
                  </div>
                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    <!-- FLUX.1 Dev -->
                    <button type="button" onclick="selectDirectComfyModel('flux_dev')" id="btn-engine-flux" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-emerald-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-emerald-300">FLUX.1 Dev</span>
                        <span class="text-[9px] px-1 py-0.2 bg-emerald-500/20 text-emerald-300 rounded font-mono">SOTA</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">أعلى تفاصيل فوتوغرافية RAW</div>
                    </button>

                    <!-- SD 3.5 Large -->
                    <button type="button" onclick="selectDirectComfyModel('sd35')" id="btn-engine-sd35" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-indigo-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-indigo-300">Stability SD 3.5</span>
                        <span class="text-[9px] px-1 py-0.2 bg-indigo-500/20 text-indigo-300 rounded font-mono">Large</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">معمارية DiT متطورة</div>
                    </button>

                    <!-- SDXL Base -->
                    <button type="button" onclick="selectDirectComfyModel('sdxl')" id="btn-engine-sdxl" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-amber-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-amber-300">Stability SDXL Base</span>
                        <span class="text-[9px] px-1 py-0.2 bg-amber-500/20 text-amber-300 rounded font-mono">LoRA OK</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">دعم كامل للورات الممثلين</div>
                    </button>
                  </div>
                </div>

                <!-- 3. أدوات الأداء والمزامنة -->
                <div class="space-y-1.5 pt-1">
                  <div class="text-[10px] text-cyan-300 font-bold flex items-center gap-1.5">
                    <i class="fa-solid fa-wand-magic-sparkles text-cyan-400"></i>
                    <span>🎭 محركات الأداء والمزامنة الصوتية (Performance & Voice Dubbing):</span>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <!-- LatentSync -->
                    <button type="button" onclick="selectDirectComfyModel('latentsync')" id="btn-engine-ls" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-cyan-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-cyan-300">LatentSync (Open Source)</span>
                        <span class="text-[9px] px-1 py-0.2 bg-cyan-500/20 text-cyan-300 rounded font-mono">مزامنة فم</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">دبلجة ومزامنة الشفاه مع الصوت</div>
                    </button>

                    <!-- Kling Motion Control -->
                    <button type="button" onclick="selectDirectComfyModel('kling')" id="btn-engine-kling" class="p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-yellow-400 text-right transition flex flex-col justify-between">
                      <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-white hover:text-yellow-300">Kling Motion Control</span>
                        <span class="text-[9px] px-1 py-0.2 bg-yellow-500/20 text-yellow-300 rounded font-mono">1080p</span>
                      </div>
                      <div class="text-[10px] text-slate-400 font-sans">توجيه حركة الوجه والجسم بدقة</div>
                    </button>
                  </div>
                </div>
              </div>
              <span class="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">المصادر المفتوحة جاهزة</span>

            </div>



            <!-- Image Mode Fields (SDXL, SD 3.5, Flux) -->
            <div id="comfy-image-fields" class="space-y-3.5">
              <!-- Model (Checkpoint) Selection -->
              <div class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl space-y-2">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-bold text-emerald-300 flex items-center gap-1.5">
                    <i class="fa-solid fa-camera-retro"></i>
                    <span>موديل التصوير الفوتوغرافي (Image Checkpoint):</span>
                  </label>
                  <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-mono font-bold">ComfyUI Image</span>
                </div>
                <select id="comfy-checkpoint-select" class="w-full bg-cinema-900 border border-emerald-500/50 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-400 font-bold">
                  <option value="SDXL/sd_xl_base_1.0_0.9vae.safetensors" selected>🎬 Stability SDXL Base 1.0 (مفتوح المصدر - سينمائي عالي الدقة)</option>
                  <option value="Stability/sd3.5_large.safetensors">💎 Stability SD 3.5 Large (مفتوح المصدر - أحدث معمارية)</option>
                  <option value="Flux/flux1-dev.safetensors">📸 FLUX.1 Dev (أعلى تفاصيل فوتوغرافية RAW 1080p)</option>
                  <option value="SDXL-TURBO/sd_xl_turbo_1.0_fp16.safetensors">⚡ SDXL Turbo (صاروخي مفتوح المصدر - ثانية واحدة)</option>
                </select>
              </div>

              <!-- Actor / LoRA Selection -->
              <div class="space-y-1">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-bold text-slate-200">الممثل / الشخصية (LoRA المخصص):</label>
                  <span class="text-[10px] text-purple-300">من مكتبة الممثلين التي دربتها</span>
                </div>
                <select id="comfy-lora-select" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-amber-200 focus:outline-none focus:border-emerald-400">
                  <option value="" selected>👤 بدون ممثل مخصص (مشهد عام)</option>
                </select>
              </div>

              <!-- Aspect Ratio & Resolution -->
              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="text-xs font-bold text-slate-200">أبعاد الكادر (Aspect Ratio):</label>
                  <select id="comfy-aspect-select" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">
                    <option value="1216x832" selected>🎬 16:9 سينمائي عريض</option>
                    <option value="832x1216">📱 9:16 عمودي / ستوري</option>
                    <option value="1024x1024">🔲 1:1 مربع نقي</option>
                    <option value="1344x576">🎥 2.39:1 شاشة سينما بانوراما</option>
                  </select>
                </div>
                <div class="space-y-1">
                  <label class="text-xs font-bold text-slate-200">نمط الريندر (Quality & Steps):</label>
                  <select id="comfy-preset-select" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">
                    <option value="cinematic" selected>🎬 سينمائي متوازن (20 خطوة)</option>
                    <option value="ultra">💎 فائق الدقة (30 خطوة)</option>
                    <option value="turbo">⚡ درافت صاروخي (4 خطوات)</option>
                  </select>
                </div>
              </div>

              <div class="space-y-1">
                <label class="text-xs font-bold text-slate-200">وصف الكادر السينمائي (Prompt):</label>
                <textarea id="comfy-prompt" rows="4" dir="auto" spellcheck="false" placeholder="اكتب وصف اللقطة بالعربية أو الإنجليزية، وحدد الإضاءة، زاوية الكاميرا، والأجواء..." class="w-full min-h-[100px] max-h-[200px] resize-y bg-cinema-900 border border-cinema-700 rounded-xl p-3 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-400 leading-relaxed font-sans"></textarea>
              </div>
            </div>

            
            <!-- ComfyUI Open Source Nodes & Models Manager -->
            <div class="bg-gradient-to-r from-amber-500/10 via-slate-900 to-slate-900 border border-amber-500/30 rounded-xl p-4 shadow-lg mb-4">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <i class="fa-solid fa-cubes-stacked text-amber-400 text-base"></i>
                  <h4 class="text-xs font-bold text-amber-200">مدير الـ Nodes والموديلات مفتوحة المصدر (Wan 2.1, Wan 2.2, Hunyuan, CogVideoX)</h4>
                </div>
                <div class="flex items-center gap-2">
                  <button type="button" onclick="checkComfyNodeStatus()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-bold border border-slate-700 transition flex items-center gap-1">
                    <i class="fa-solid fa-rotate text-amber-400"></i> فحص الـ Nodes
                  </button>
                  <button type="button" onclick="installComfyNodesNow()" id="btn-install-comfy-nodes" class="px-3 py-1 bg-gradient-to-r from-amber-600 to-yellow-600 hover:brightness-110 text-white rounded text-[11px] font-bold shadow transition flex items-center gap-1.5">
                    <i class="fa-solid fa-download"></i> تثبيت حزمة الـ Nodes الآن
                  </button>
                </div>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2" id="comfy-nodes-status-grid">
                <div class="bg-black/40 border border-slate-800 rounded-lg p-2 flex items-center justify-between">
                  <div>
                    <div class="text-[11px] font-bold text-white">Wan 2.1 & 2.2</div>
                    <div class="text-[9px] text-slate-400">WanVideoWrapper</div>
                  </div>
                  <span id="badge-node-wan" class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">جاهز</span>
                </div>
                <div class="bg-black/40 border border-slate-800 rounded-lg p-2 flex items-center justify-between">
                  <div>
                    <div class="text-[11px] font-bold text-white">HunyuanVideo</div>
                    <div class="text-[9px] text-slate-400">HunyuanWrapper</div>
                  </div>
                  <span id="badge-node-hunyuan" class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">جاهز</span>
                </div>
                <div class="bg-black/40 border border-slate-800 rounded-lg p-2 flex items-center justify-between">
                  <div>
                    <div class="text-[11px] font-bold text-white">CogVideoX</div>
                    <div class="text-[9px] text-slate-400">CogVideoWrapper</div>
                  </div>
                  <span id="badge-node-cogvideo" class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">جاهز</span>
                </div>
                <div class="bg-black/40 border border-slate-800 rounded-lg p-2 flex items-center justify-between">
                  <div>
                    <div class="text-[11px] font-bold text-white">Video Helper Suite</div>
                    <div class="text-[9px] text-slate-400">VHS Combine</div>
                  </div>
                  <span id="badge-node-vhs" class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">جاهز</span>
                </div>
              </div>
              <div id="node-install-status-msg" class="hidden mt-2 text-[11px] text-amber-300 bg-amber-500/10 border border-amber-500/20 rounded p-2"></div>
            </div>

            <!-- Video Mode Fields (Wan 2.1, CogVideoX, Hunyuan, SVD-XT) -->
            <div id="comfy-video-fields" class="hidden space-y-3.5">
              <!-- Video Checkpoint Selector (PROMINENT AT TOP) -->
              <div class="p-3 bg-gradient-to-r from-amber-500/15 via-yellow-500/10 to-amber-500/15 border border-amber-500/50 rounded-xl space-y-2 shadow-md">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-black text-amber-200 flex items-center gap-1.5">
                    <i class="fa-solid fa-film text-cinema-gold animate-pulse"></i>
                    <span>🎥 موديل الفيديو السينمائي المختار (Open Source Video Model):</span>
                  </label>
                  <span class="text-[10px] bg-amber-500/25 text-amber-300 px-2.5 py-0.5 rounded font-mono font-bold border border-amber-500/30">ComfyUI Video</span>
                </div>
                <select id="comfy-video-checkpoint" onchange="onComfyVideoModelChange()" class="w-full bg-cinema-900 border border-amber-500/60 rounded-xl px-3 py-2 text-xs text-amber-300 font-extrabold focus:outline-none focus:border-amber-400">
                  <option value="Wan2.2/wan2.2_i2v_720p_14B_fp8_e4m3fn.safetensors" selected>💎 Alibaba Wan 2.2 Video (14B فائق الحركية والفيزياء - مفتوح المصدر 720p)</option>
                   <option value="Wan2.1/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors">💎 Alibaba Wan 2.1 Video (14B سينمائي مفتوح المصدر 720p)</option>
                  <option value="CogVideoX/cogvideox_5b_i2v.safetensors">🎥 THUDM CogVideoX-5B (مفتوح المصدر - سريع ومستقر)</option>
                  <option value="HunyuanVideo/hunyuan_video_720p_fp8_e4m3fn.safetensors">🎬 Tencent HunyuanVideo (13B مفتوح المصدر 720p - أعلى ثبات وتكوين)</option>
                  <option value="SVD/svd_xt.safetensors">⚡ Stability AI SVD-XT (25 كادر سينمائي مستقر)</option>
                </select>
                <p id="comfy-video-model-hint" class="text-[11px] text-amber-200/90 font-sans leading-normal">
                  ⚡ محرك Alibaba Wan 2.1 يوفر أعلى ثبات فيزيائي وكاميرا سينمائية ثلاثية الأبعاد بدون تشوه.
                </p>
              </div>

              <!-- Reference Image Selection -->
              <div class="space-y-1.5 p-3 bg-cinema-900/50 border border-cinema-700 rounded-xl">
                <label class="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <i class="fa-solid fa-image text-cinema-gold"></i>
                  <span>كادر الصورة المراد تحريكها (Reference Frame):</span>
                </label>
                <div class="flex items-center gap-2">
                  <input type="text" id="comfy-video-img-source" placeholder="مسار الكادر المرجعي أو الرابط..." value="" class="flex-1 bg-cinema-950 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono">
                  <input type="file" id="comfy-video-file-input" accept="image/*" class="hidden" onchange="handleComfyVideoFileSelected(event)">
                  <button type="button" onclick="document.getElementById('comfy-video-file-input').click()" class="px-3 py-2 bg-gradient-to-r from-amber-600 to-yellow-600 hover:opacity-90 text-[11px] text-cinema-950 font-black rounded-xl whitespace-nowrap shadow flex items-center gap-1">
                    <i class="fa-solid fa-cloud-arrow-up"></i> رفع كادر
                  </button>
                  <button type="button" onclick="useLastRenderedImageForVideo()" class="px-2.5 py-2 bg-cinema-700 hover:bg-cinema-600 text-[11px] text-white font-bold rounded-xl whitespace-nowrap">
                    ⚡ آخر كادر
                  </button>
                </div>
                <!-- Mini Thumbnail Preview when frame is set -->
                <div id="comfy-video-ref-preview-box" class="hidden flex items-center gap-2 pt-1 border-t border-cinema-800">
                  <img id="comfy-video-ref-preview-thumb" src="" alt="Frame preview" class="w-12 h-12 object-cover rounded-lg border border-amber-500/40">
                  <div class="text-[11px] text-slate-300">
                    <span class="text-emerald-400 font-bold">✓ الكادر المرجعي جاهز للتحريك</span>
                    <button type="button" onclick="clearComfyVideoRef()" class="text-rose-400 hover:underline mr-2 text-[10px]">إزالة</button>
                  </div>
                </div>
              </div>

              <!-- Video Prompt -->
              <div class="space-y-1">
                <div class="flex items-center justify-between">
                  <label class="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                    <i class="fa-solid fa-pen-nib text-cinema-gold"></i>
                    <span>✍️ وصف حركة المشهد والكاميرا (Video Prompt):</span>
                  </label>
                  <span class="text-[10px] text-amber-400 font-mono">يدعم Wan 2.1 و CogVideoX و Hunyuan</span>
                </div>
                <textarea id="comfy-video-prompt" rows="3" dir="auto" spellcheck="false" placeholder="اكتب وصف حركة الكاميرا والأجواء (مثال: cinematic slow push-in, intense eye contact, atmospheric cinema lighting, 8k)... أو اتركه فارغاً للتحريك التلقائي" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-400 leading-relaxed font-sans"></textarea>
              </div>

              <!-- Motion & FPS -->
              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="text-xs font-bold text-slate-200">شدة حركة الكاميرا (Motion):</label>
                  <input type="range" id="comfy-video-motion" min="20" max="255" value="127" class="w-full accent-amber-500 cursor-pointer" oninput="document.getElementById('comfy-video-motion-val').innerText = this.value">
                  <div class="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>هادئ (20)</span>
                    <span id="comfy-video-motion-val" class="text-amber-400 font-bold">127</span>
                    <span>سريع (255)</span>
                  </div>
                </div>

                <div class="space-y-1">
                  <label class="text-xs font-bold text-slate-200">معدل الإطارات (FPS):</label>
                  <select id="comfy-video-fps" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-2.5 py-2 text-xs text-slate-100">
                    <option value="6" selected>6 fps (حركة ناعمة)</option>
                    <option value="12">12 fps (حركة سينمائية)</option>
                    <option value="24">24 fps (قياسي كامل)</option>
                  </select>
                </div>
              </div>
            </div>

              <!-- Dedicated Kling Motion Control Panel -->
            <div id="comfy-kling-fields" class="hidden space-y-4 bg-amber-950/20 p-4 rounded-2xl border border-amber-800/40">
              <div class="flex items-center justify-between border-b border-amber-800/30 pb-2">
                <span class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-crown text-amber-400"></i>
                  <span>👑 Kling Motion Control v3 (Cinema Grade 1080p)</span>
                </span>
                <span class="text-[10px] font-bold text-amber-300 bg-amber-500/20 px-2.5 py-0.5 rounded-full border border-amber-500/30">سيرفرلس 1080p</span>
              </div>
              <p class="text-xs text-slate-300">يستخدم نفس مدخلات الصورة والفيديو لنقل الحركات الواقعية بدقة سينمائية هوليوودية 1080p.</p>
            </div>

<!-- LatentSync Mode Fields (Clean Spacious Layout) -->

            <div id="comfy-latentsync-fields" class="hidden space-y-4 bg-cyan-950/20 p-4 rounded-2xl border border-cyan-800/40">

              <div class="flex items-center justify-between border-b border-cyan-800/30 pb-2">

                <span class="text-xs font-bold text-cyan-300 flex items-center gap-1.5">

                  <i class="fa-solid fa-lips text-cyan-400"></i>

                  <span>إعدادات مزامنة ونطق الشفاه (LatentSync - فوري وسريع)</span>

                </span>

                <span class="text-[10px] font-bold text-cyan-300 bg-cyan-500/20 px-2.5 py-0.5 rounded-full border border-cyan-500/30">سيرفرلس فوري</span>

              </div>



              <!-- LatentSync Target Media Card -->

              <div class="bg-cinema-900/80 p-3.5 rounded-xl border border-cyan-500/30 space-y-2">

                <div class="flex items-center justify-between">

                  <label class="text-xs font-bold text-slate-200 flex items-center gap-1.5">

                    <i class="fa-solid fa-clapperboard text-cyan-400"></i>

                    <span>1. كادر أو مشهد الفيديو المراد نطق حواره:</span>

                  </label>

                  <span id="comfy-ls-target-badge" class="hidden text-[10px] text-cyan-300 font-bold bg-cyan-500/20 px-2 py-0.5 rounded-full border border-cyan-500/40">✓ تم التحميل</span>

                </div>

                <div class="flex items-center gap-3">

                  <div id="comfy-ls-target-box" class="w-16 h-16 rounded-xl border-2 border-dashed border-cyan-500/60 bg-cinema-950 flex items-center justify-center shrink-0 overflow-hidden cursor-pointer shadow group hover:border-cyan-400 transition" onclick="document.getElementById('comfy-ls-target-input').click()">

                    <img id="comfy-ls-target-preview" src="" class="hidden w-full h-full object-cover">

                    <i id="comfy-ls-target-placeholder" class="fa-solid fa-image text-cyan-400 text-xl group-hover:scale-110 transition"></i>

                  </div>

                  <div class="flex-1 space-y-2">

                    <input type="file" id="comfy-ls-target-input" accept="video/mp4,video/webm,image/*" class="hidden" onchange="uploadLatentSyncTarget(this)">

                    <div class="flex items-center gap-2">

                      <button type="button" onclick="document.getElementById('comfy-ls-target-input').click()" class="flex-1 py-2 px-3 bg-gradient-to-r from-cyan-700 to-teal-600 hover:from-cyan-600 hover:to-teal-500 text-xs text-white font-bold rounded-xl shadow flex items-center justify-center gap-2 cursor-pointer transition">

                        <i class="fa-solid fa-cloud-arrow-up"></i>

                        <span>رفع كادر/فيديو الشخصية</span>

                      </button>

                      <button type="button" onclick="useLastRenderedMediaForLatentSync()" class="py-2 px-3 bg-cinema-800 hover:bg-cinema-700 text-[11px] text-slate-300 hover:text-white font-bold rounded-xl whitespace-nowrap border border-cinema-700 transition">

                        <i class="fa-solid fa-clock-rotate-left text-cyan-400"></i> آخر ميديا

                      </button>

                    </div>

                    <input type="text" id="comfy-ls-video-source" placeholder="مسار الكادر أو الفيديو..." value="" class="w-full bg-cinema-950 border border-cinema-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-400 font-mono">

                  </div>

                </div>

              </div>



              <!-- LatentSync Audio Card -->

              <div class="bg-cinema-900/80 p-3.5 rounded-xl border border-cyan-500/30 space-y-2">

                <div class="flex items-center justify-between">

                  <label class="text-xs font-bold text-slate-200 flex items-center gap-1.5">

                    <i class="fa-solid fa-microphone text-cyan-400"></i>

                    <span>2. ملف الصوت أو الحوار المسجل (Audio Track):</span>

                  </label>

                  <span id="comfy-ls-audio-badge" class="hidden text-[10px] text-emerald-400 font-bold bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/40">✓ تم التحميل</span>

                </div>

                <div class="space-y-2">

                  <input type="file" id="comfy-ls-audio-input" accept="audio/*" class="hidden" onchange="uploadLatentSyncAudio(this)">

                  <button type="button" onclick="document.getElementById('comfy-ls-audio-input').click()" class="w-full py-2 px-3 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-xs text-white font-bold rounded-xl shadow flex items-center justify-center gap-2 cursor-pointer transition">

                    <i class="fa-solid fa-cloud-arrow-up"></i>

                    <span>رفع ملف صوت الحوار (WAV/MP3) من جهازك</span>

                  </button>

                  <input type="text" id="comfy-ls-audio-source" placeholder="مسار ملف الصوت المرفوع..." value="" class="w-full bg-cinema-950 border border-cinema-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-400 font-mono">

                </div>

                <p class="text-[10px] text-slate-400">ارفع أي ملف صوتي مسجل ليقوم الذكاء الاصطناعي بمطابقة حركة الشفاه بدقة 100%.</p>

              </div>

            </div>



            <!-- Negative Prompt Accordion -->

            <div class="space-y-1">

              <details class="text-[11px] text-slate-400 cursor-pointer">

                <summary class="font-bold text-slate-300 hover:text-white">إعدادات متقدمة (السلبيات)</summary>

                <div class="pt-2 space-y-2">

                  <input type="text" id="comfy-negative" placeholder="العناصر غير المرغوبة..." value="blurry, bad anatomy, bad hands, low quality, artifacts, watermark" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-1.5 text-xs text-slate-200">

                </div>

              </details>

            </div>



            <!-- Auto-Stop Pod Safety Toggle -->

            <div class="flex items-center gap-2 bg-cinema-900/80 p-2.5 rounded-xl border border-cinema-700">

              <input type="checkbox" id="comfy-autostop" checked class="w-4 h-4 accent-rose-500 rounded cursor-pointer">

              <label for="comfy-autostop" class="text-[11px] text-rose-300 font-bold cursor-pointer">

                🛡️ إيقاف وحذف الكارت السحابي تلقائياً فور اكتمال الريندر (حماية قصوى للرصيد)

              </label>

            </div>

          </div>



          <!-- THE ONLY EXECUTION BUTTON -->

          <div class="pt-2">

            <button type="button" onclick="handleComfyDispatch()" id="comfy-render-btn" class="w-full py-3.5 bg-gradient-to-r from-emerald-600 via-teal-600 to-amber-500 hover:opacity-95 text-white font-extrabold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/25 transition">

              <i class="fa-solid fa-clapperboard" id="comfy-render-btn-icon"></i>

              <span id="comfy-render-btn-text">▶ ريندر الكادر السينمائي الآن (ComfyUI Cloud)</span>

            </button>

            <p class="text-[10px] text-center text-slate-400 mt-2 font-mono">لن يتم أي توليد إلا بالضغط الصريح على هذا الزر بأمرك يا أستاذنا.</p>

          </div>

        </div>



        <!-- Screening & Live Preview Panel (Right 7 cols) -->

        <div class="lg:col-span-7 space-y-4 bg-cinema-800/60 border border-cinema-700 rounded-2xl p-5 shadow-lg flex flex-col">

          <div class="flex items-center justify-between border-b border-cinema-700 pb-2">

            <h3 class="text-sm font-bold text-cinema-gold flex items-center gap-2">

              <i class="fa-solid fa-tv"></i> شاشة المعاينة الفورية (Live Studio Preview)

            </h3>

            <span id="comfy-render-timer" class="text-[11px] font-mono text-emerald-400 font-bold">جاهز للريندر</span>

          </div>



          <div id="comfy-preview-box" class="flex-1 min-h-[420px] bg-cinema-950/90 border border-cinema-800 rounded-xl flex items-center justify-center p-4 relative overflow-hidden group">

            <div id="comfy-placeholder" class="text-center text-slate-500 space-y-3">

              <div class="w-16 h-16 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 text-2xl">

                <i class="fa-solid fa-camera-retro"></i>

              </div>

              <p class="text-xs font-bold text-slate-300">حدد مواصفات الكادر واضغط زر الريندر بأمرك</p>

              <p class="text-[11px] text-slate-400">ستظهر الصورة هنا فوراً في 4 ثوانٍ مع زر التنزيل المباشر</p>

            </div>



            <div id="comfy-spinner" class="hidden text-center space-y-3">

              <i class="fa-solid fa-circle-notch fa-spin text-4xl text-emerald-400"></i>

              <p id="comfy-spinnerText" class="text-xs font-bold text-emerald-300">كارت الشاشة السحابي يريندر الكادر السينمائي الآن...</p>

              <div class="w-48 mx-auto h-1.5 bg-cinema-800 rounded-full overflow-hidden">

                <div id="comfy-progressbar" class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300" style="width: 30%"></div>

              </div>

            </div>



            <div id="comfy-result-container" class="hidden w-full h-full flex flex-col items-center justify-center relative">

              <img id="comfy-result-img" src="" alt="Comfy Render" class="max-h-[360px] max-w-full rounded-lg shadow-2xl object-contain border border-cinema-700">
              <video id="comfy-result-video" controls autoplay loop class="hidden max-h-[360px] max-w-full rounded-lg shadow-2xl object-contain border border-cinema-700"></video>

              <div class="mt-4 flex flex-wrap items-center justify-center gap-3">

                <a id="comfy-download-btn" href="#" download class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-95 text-white font-extrabold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition">

                  <i class="fa-solid fa-cloud-arrow-down text-sm"></i>

                  <span>تنزيل الكادر الأصلي بجودة فائقة (PNG)</span>

                </a>

                <button type="button" id="comfy-open-screening-btn" class="px-4 py-2.5 bg-cinema-800 hover:bg-cinema-700 text-slate-200 border border-cinema-700 font-bold rounded-xl text-xs flex items-center gap-2 transition">

                  <i class="fa-solid fa-film text-cinema-gold"></i>

                  <span>عرض في شاشة السينما الكبرى</span>

                </button>

              </div>

            </div>

          </div>

        </div>

      </div>

    </section>



  </main>



  <script>

    const CINDY_MEMORY = {memory_json_str};

    const MASTER_PROMPTS = {prompts_json_str};

    let currentMode = 'video';

    let currentSelectedModel = 'Google Veo 3.1 Cinematic';

    let voiceOutputEnabled = true;

    let isRecording = false;

    let recognition = null;

    let availableVoices = [];

    if (location.protocol === 'file:') {{ location.replace('http://127.0.0.1:8765/index.html'); }}

    const API_BASE = 'http://127.0.0.1:8765';



    document.addEventListener('DOMContentLoaded', () => {{
      initVoiceRecognition();
      initSpeechVoices();
      loadVaultStatus();
      syncSelectedModel();
      initKeyboardAndInputs();
      refreshWalletStatus(false);
      // Auto-refresh live wallet balance every 25 seconds
      setInterval(() => refreshWalletStatus(false), 25000);

      // Pre-fill latest motion transfer project
      try {{
        const klingActorInp = document.getElementById('comfy-kling-actor-img');
        if (klingActorInp && !klingActorInp.value) {{
          klingActorInp.value = '/outputs/upload_1793745039209_02c844e33a5898c7af2f08144bbb3a0c.jpg';
          const prev = document.getElementById('comfy-kling-actor-preview');
          const icon = document.getElementById('comfy-kling-actor-placeholder');
          const badge = document.getElementById('comfy-kling-actor-badge');
          if (prev) {{ prev.src = klingActorInp.value; prev.classList.remove('hidden'); }}
          if (icon) icon.classList.add('hidden');
          if (badge) {{ badge.innerText = '✓ صورة الشخصية جاهزة'; badge.classList.remove('hidden'); }}
        }}
        const klingVidInp = document.getElementById('comfy-kling-driving-vid');
        if (klingVidInp && !klingVidInp.value) {{
          klingVidInp.value = '/outputs/upload_1793745073905_Handheld_camera_filming_footage_.mp4';
          const prev = document.getElementById('comfy-kling-video-preview');
          const icon = document.getElementById('comfy-kling-video-placeholder');
          const badge = document.getElementById('comfy-kling-video-badge');
          if (prev) {{ prev.src = klingVidInp.value; prev.classList.remove('hidden'); }}
          if (icon) icon.classList.add('hidden');
          if (badge) {{ badge.innerText = '✓ فيديو الحركة جاهز'; badge.classList.remove('hidden'); }}
        }}
        const resBox = document.getElementById('comfy-result-container');
        const resVid = document.getElementById('comfy-result-video');
        const resImg = document.getElementById('comfy-result-img');
        const placeholder = document.getElementById('comfy-placeholder');
        const dlBtn = document.getElementById('comfy-download-btn');
        if (resBox && resVid && placeholder) {{
          resVid.src = '/outputs/Kling_Motion_Render.mp4';
          resVid.classList.remove('hidden');
          if (resImg) resImg.classList.add('hidden');
          resBox.classList.remove('hidden');
          placeholder.classList.add('hidden');
          if (dlBtn) dlBtn.href = '/outputs/Kling_Motion_Render.mp4';
        }}
      }} catch (e) {{
        console.warn('Prefill error:', e);
      }}
    }});



    function initKeyboardAndInputs() {{

      const cInp = document.getElementById('chat-input');

      if (cInp) {{

        cInp.addEventListener('input', function() {{

          this.style.height = 'auto';

          this.style.height = Math.min(this.scrollHeight, 128) + 'px';

        }});

        cInp.addEventListener('keydown', function(e) {{

          if (e.key === 'Enter' && !e.shiftKey) {{

            e.preventDefault();

            handleChatSubmit(e);

          }}

        }});

      }}



      const ePrompt = document.getElementById('edit-media-prompt');

      if (ePrompt) {{

        ePrompt.addEventListener('keydown', function(e) {{

          if (e.key === 'Enter' && !e.shiftKey) {{

            e.preventDefault();

            executeMediaEdit();

          }}

        }});

      }}



      const lPrompt = document.getElementById('lora-gen-prompt');

      if (lPrompt) {{

        lPrompt.addEventListener('keydown', function(e) {{

          if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {{

            e.preventDefault();

            executeLoraGeneration();

          }}

        }});

      }}

    }}



        function switchTab(tabId) {{
      const allTabs = ['chat', 'comfy', 'screening', 'lora', 'flow', 'vault'];
      const ON = 'px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 bg-cinema-gold text-cinema-900 shadow';
      const OFF = 'px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition flex items-center gap-1.5';

      allTabs.forEach(t => {{
        const sec = document.getElementById('tab-' + t);
        const btn = document.getElementById('nav-main-' + t);
        if (sec) sec.classList.toggle('hidden', t !== tabId);
        if (btn) {{
          if (t === tabId) {{
            btn.className = ON;
          }} else {{
            btn.className = OFF;
            if (t === 'comfy') {{
              btn.className += ' border border-emerald-500/40 bg-emerald-500/10 text-emerald-300';
            }}
          }}
        }}
      }});

      if (tabId === 'lora' && typeof refreshLoraLibrary === 'function') refreshLoraLibrary();
        if (tabId === 'vault' && typeof loadVaultStatus === 'function') loadVaultStatus();
      if (tabId === 'comfy') {{
        if (typeof checkComfyStatus === 'function') checkComfyStatus();
        if (typeof refreshWalletStatus === 'function') refreshWalletStatus();
        if (currentMode === 'video' && currentComfySubMode !== 'latentsync' && currentComfySubMode !== 'kling') {{
          switchComfySubMode('video');
        }} else if (currentMode === 'image' && currentComfySubMode !== 'latentsync' && currentComfySubMode !== 'kling') {{
          switchComfySubMode('image');
        }}
      }}
    }}


    function sendPromptToComfyStudio(promptText, mode) {{
      switchTab('comfy');
      if (mode === 'video') {{
        switchComfySubMode('video');
        const pInput = document.getElementById('comfy-video-prompt');
        if (pInput) pInput.value = promptText;
      }} else {{
        switchComfySubMode('image');
        const pInput = document.getElementById('comfy-prompt');
        if (pInput) pInput.value = promptText;
      }}
      showToast('تم نقل البرومبت بنجاح إلى استوديو ComfyUI — حدد الكادر واضغط ريندر!', 'success');
    }}

    function onComfyVideoModelChange() {{
      const ckpt = (document.getElementById('comfy-video-checkpoint')?.value || '').toLowerCase();
      const btnText = document.getElementById('comfy-render-btn-text');
      const hint = document.getElementById('comfy-video-model-hint');
      if (ckpt.includes('wan')) {{
        if (btnText && currentComfySubMode === 'video') btnText.innerText = '▶ ريندر فيديو Alibaba Wan 2.1 الآن (ComfyUI 720p)';
        if (hint) hint.innerText = '⚡ محرك Alibaba Wan 2.1: دقة 720p مع أعلى ثبات فيزيائي وحركة كاميرا سينمائية ثلاثية الأبعاد بدون تشوه.';
      }} else if (ckpt.includes('cogvideo')) {{
        if (btnText && currentComfySubMode === 'video') btnText.innerText = '▶ ريندر فيديو THUDM CogVideoX-5B الآن (ComfyUI مفتوح المصدر)';
        if (hint) hint.innerText = '⚡ محرك THUDM CogVideoX-5B: مفتوح المصدر سريع وخفيف، مخصص للحركات السينمائية السريعة والمؤثرات الواقعية.';
      }} else if (ckpt.includes('hunyuan')) {{
        if (btnText && currentComfySubMode === 'video') btnText.innerText = '▶ ريندر فيديو Tencent HunyuanVideo الآن (ComfyUI 13B)';
        if (hint) hint.innerText = '⚡ محرك Tencent HunyuanVideo: نموذج 13B عملاق بدقة سينمائية 720p وحركة جسدية وفيزيائية فائقة الثبات.';
      }} else {{
        if (btnText && currentComfySubMode === 'video') btnText.innerText = '▶ ريندر فيديو Stability SVD-XT الآن (ComfyUI 25fps)';
        if (hint) hint.innerText = '⚡ محرك Stability AI SVD-XT: تحريك 25 كادر متتالي، سريع جداً وخفيف ومستقر.';
      }}
    }}

    function clearComfyVideoRef() {{
      const inp = document.getElementById('comfy-video-img-source');
      if (inp) inp.value = '';
      const box = document.getElementById('comfy-video-ref-preview-box');
      if (box) box.classList.add('hidden');
    }}

    function switchComfySubMode(mode) {{
      currentComfySubMode = mode;
      const imgBtn = document.getElementById('comfy-mode-img-btn');
      const vidBtn = document.getElementById('comfy-mode-vid-btn');
            const klingBtn = document.getElementById('comfy-mode-kling-btn');
      const lsBtn = document.getElementById('comfy-mode-ls-btn');

      const imgFields = document.getElementById('comfy-image-fields');
      const vidFields = document.getElementById('comfy-video-fields');
            const klingFields = document.getElementById('comfy-kling-fields');
      const lsFields = document.getElementById('comfy-latentsync-fields');

      const btnText = document.getElementById('comfy-render-btn-text');
      const btnIcon = document.getElementById('comfy-render-btn-icon');

      const defaultBtnClass = 'px-3 py-1 rounded-lg bg-cinema-900 text-slate-400 hover:text-white border border-cinema-700 text-xs font-bold transition flex items-center gap-1.5';
      if (imgBtn) imgBtn.className = defaultBtnClass;
      if (vidBtn) vidBtn.className = defaultBtnClass;
            if (klingBtn) klingBtn.className = defaultBtnClass;
      if (lsBtn) lsBtn.className = defaultBtnClass;

      if (imgFields) imgFields.classList.add('hidden');
      if (vidFields) vidFields.classList.add('hidden');
            if (klingFields) klingFields.classList.add('hidden');
      if (lsFields) lsFields.classList.add('hidden');

      const offlineControls = document.getElementById('comfy-offline-controls');
      const onlineControls = document.getElementById('comfy-online-controls');
      const serverlessControls = document.getElementById('comfy-serverless-controls');

      if (mode === 'video') {{
        if (vidBtn) vidBtn.className = 'px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold transition flex items-center gap-1.5';
        if (vidFields) vidFields.classList.remove('hidden');
        onComfyVideoModelChange();
        if (serverlessControls) serverlessControls.classList.add('hidden');
        if (typeof checkComfyStatus === 'function') checkComfyStatus();
      }} else if (mode === 'kling') {{
        if (klingBtn) klingBtn.className = 'px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold transition flex items-center gap-1.5';
        if (klingFields) klingFields.classList.remove('hidden');
        btnText.innerText = '▶ ريندر نقل الحركة بمحرك Kling Motion Control (1080p)';
        btnIcon.className = 'fa-solid fa-crown text-amber-300';
        if (offlineControls) offlineControls.classList.add('hidden');
        if (onlineControls) onlineControls.classList.add('hidden');
        if (serverlessControls) serverlessControls.classList.remove('hidden');
      }} else if (mode === 'latentsync') {{
        if (lsBtn) lsBtn.className = 'px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition flex items-center gap-1.5';
        if (lsFields) lsFields.classList.remove('hidden');
        btnText.innerText = '▶ ريندر مزامنة ونطق الشفاه الآن (LatentSync)';
        btnIcon.className = 'fa-solid fa-lips text-cyan-300';
        if (offlineControls) offlineControls.classList.add('hidden');
        if (onlineControls) onlineControls.classList.add('hidden');
        if (serverlessControls) serverlessControls.classList.remove('hidden');
      }} else {{
        if (imgBtn) imgBtn.className = 'px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-bold transition flex items-center gap-1.5';
        if (imgFields) imgFields.classList.remove('hidden');
        btnText.innerText = '▶ ريندر الكادر السينمائي الآن (ComfyUI Image)';
        btnIcon.className = 'fa-solid fa-clapperboard text-emerald-300';
        if (serverlessControls) serverlessControls.classList.add('hidden');
        if (typeof checkComfyStatus === 'function') checkComfyStatus();
      }}
    }}

    function useLastRenderedImageForVideo() {{
      if (lastRenderedComfyMedia) {{
        setAsVideoReference(lastRenderedComfyMedia);
      }} else {{
        showToast('لم يتم ريندر أي كادر بعد في الاستوديو لاستخدامه كمرجع.', 'warn');
      }}
    }}



    

    function uploadCharacterImage(input) {{

      if (!input.files || !input.files[0]) return;

      const file = input.files[0];

      const textInput = document.getElementById('comfy-lp-source-img');

      const previewImg = document.getElementById('comfy-lp-char-preview');

      const placeholder = document.getElementById('comfy-lp-char-placeholder');

      const badge = document.getElementById('comfy-lp-char-badge');



      // 1. Instant local preview

      const reader = new FileReader();

      reader.onload = async function(e) {{

        if (previewImg) {{

          previewImg.src = e.target.result;

          previewImg.classList.remove('hidden');

        }}

        if (placeholder) placeholder.classList.add('hidden');

        if (badge) {{

          badge.innerText = 'تم اختيار ' + file.name;

          badge.classList.remove('hidden');

        }}

        textInput.value = 'جاري الرفع... (' + file.name + ')';



        // 2. Upload to server

        try {{

          const res = await fetch('/api/upload', {{

            method: 'POST',

            headers: {{ 'Content-Type': 'application/json' }},

            body: JSON.stringify({{ data_url: e.target.result, filename: file.name }})

          }});

          const data = await res.json();

          if (data.success) {{

            textInput.value = data.url;

            showToast('تم اختيار ورفع صورة الشخصية بنجاح! 🎭', 'success');

          }} else {{

            showToast('فشل الرفع: ' + (data.error || 'خطأ'), 'error');

          }}

        }} catch(err) {{

          showToast('خطأ بالرفع: ' + err, 'error');

        }}

      }};

      reader.readAsDataURL(file);

    }}



    function uploadKlingMotionVideo(input) {{

      if (!input.files || !input.files[0]) return;

      const file = input.files[0];

      const textInput = document.getElementById('comfy-lp-driving-video');

      const previewVid = document.getElementById('comfy-lp-video-preview');

      const placeholder = document.getElementById('comfy-lp-video-placeholder');

      const badge = document.getElementById('comfy-lp-video-badge');



      const reader = new FileReader();

      reader.onload = async function(e) {{

        if (previewVid) {{

          previewVid.src = e.target.result;

          previewVid.classList.remove('hidden');

        }}

        if (placeholder) placeholder.classList.add('hidden');

        if (badge) {{

          badge.innerText = 'تم اختيار ' + file.name;

          badge.classList.remove('hidden');

        }}

        textInput.value = 'جاري الرفع... (' + file.name + ')';



        try {{

          const res = await fetch('/api/upload', {{

            method: 'POST',

            headers: {{ 'Content-Type': 'application/json' }},

            body: JSON.stringify({{ data_url: e.target.result, filename: file.name }})

          }});

          const data = await res.json();

          if (data.success) {{

            textInput.value = data.url;

            showToast('تم رفع فيديو التعبير بنجاح! 🎬', 'success');

          }} else {{

            showToast('فشل الرفع: ' + (data.error || 'خطأ'), 'error');

          }}

        }} catch(err) {{

          showToast('خطأ بالرفع: ' + err, 'error');

        }}

      }};

      reader.readAsDataURL(file);

    }}



    function uploadLatentSyncTarget(input) {{

      if (!input.files || !input.files[0]) return;

      const file = input.files[0];

      const textInput = document.getElementById('comfy-ls-video-source');

      const previewImg = document.getElementById('comfy-ls-target-preview');

      const placeholder = document.getElementById('comfy-ls-target-placeholder');

      const badge = document.getElementById('comfy-ls-target-badge');



      const reader = new FileReader();

      reader.onload = async function(e) {{

        if (previewImg && file.type.startsWith('image/')) {{

          previewImg.src = e.target.result;

          previewImg.classList.remove('hidden');

        }}

        if (placeholder) placeholder.classList.add('hidden');

        if (badge) {{

          badge.innerText = 'تم اختيار ' + file.name;

          badge.classList.remove('hidden');

        }}

        textInput.value = 'جاري الرفع... (' + file.name + ')';



        try {{

          const res = await fetch('/api/upload', {{

            method: 'POST',

            headers: {{ 'Content-Type': 'application/json' }},

            body: JSON.stringify({{ data_url: e.target.result, filename: file.name }})

          }});

          const data = await res.json();

          if (data.success) {{

            textInput.value = data.url;

            showToast('تم رفع كادر الشخصية بنجاح! 👄', 'success');

          }} else {{

            showToast('فشل الرفع: ' + (data.error || 'خطأ'), 'error');

          }}

        }} catch(err) {{

          showToast('خطأ بالرفع: ' + err, 'error');

        }}

      }};

      reader.readAsDataURL(file);

    }}



    function uploadLatentSyncAudio(input) {{

      if (!input.files || !input.files[0]) return;

      const file = input.files[0];

      const textInput = document.getElementById('comfy-ls-audio-source');

      const badge = document.getElementById('comfy-ls-audio-badge');



      const reader = new FileReader();

      reader.onload = async function(e) {{

        if (badge) {{

          badge.innerText = 'تم اختيار ' + file.name;

          badge.classList.remove('hidden');

        }}

        textInput.value = 'جاري الرفع... (' + file.name + ')';



        try {{

          const res = await fetch('/api/upload', {{

            method: 'POST',

            headers: {{ 'Content-Type': 'application/json' }},

            body: JSON.stringify({{ data_url: e.target.result, filename: file.name }})

          }});

          const data = await res.json();

          if (data.success) {{

            textInput.value = data.url;

            showToast('تم رفع ملف الصوت بنجاح! 🎙️', 'success');

          }} else {{

            showToast('فشل الرفع: ' + (data.error || 'خطأ'), 'error');

          }}

        }} catch(err) {{

          showToast('خطأ بالرفع: ' + err, 'error');

        }}

      }};

      reader.readAsDataURL(file);

    }}



    function useLastRenderedImageForKlingMotion() {{

      const srcInput = document.getElementById('comfy-lp-source-img');

      const previewImg = document.getElementById('comfy-lp-char-preview');

      const placeholder = document.getElementById('comfy-lp-char-placeholder');

      const badge = document.getElementById('comfy-lp-char-badge');

      if (srcInput && lastRenderedComfyMedia) {{

        srcInput.value = lastRenderedComfyMedia;

        if (previewImg) {{

          previewImg.src = lastRenderedComfyMedia;

          previewImg.classList.remove('hidden');

        }}

        if (placeholder) placeholder.classList.add('hidden');

        if (badge) {{

          badge.innerText = 'آخر كادر تم اختياره';

          badge.classList.remove('hidden');

        }}

        showToast('تم تعيين آخر كادر لصالح Kling Motion Control!', 'success');

      }}

    }}



    function useLastRenderedMediaForLatentSync() {{

      const srcInput = document.getElementById('comfy-ls-video-source');

      const previewImg = document.getElementById('comfy-ls-target-preview');

      const placeholder = document.getElementById('comfy-ls-target-placeholder');

      const badge = document.getElementById('comfy-ls-target-badge');

      if (srcInput && lastRenderedComfyMedia) {{

        srcInput.value = lastRenderedComfyMedia;

        if (previewImg) {{

          previewImg.src = lastRenderedComfyMedia;

          previewImg.classList.remove('hidden');

        }}

        if (placeholder) placeholder.classList.add('hidden');

        if (badge) {{

          badge.innerText = 'آخر ميديا تم اختيارها';

          badge.classList.remove('hidden');

        }}

        showToast('تم تعيين آخر ميديا لصالح LatentSync!', 'success');

      }}

    }}



        function selectMotionEngine(eng) {{

      const rad = document.getElementById('engine-' + eng);

      if (rad) rad.checked = true;

      const btnText = document.getElementById('comfy-render-btn-text');

      const badge = document.getElementById('lp-engine-badge');

      if (eng === 'kling') {{

        if (btnText && currentComfySubMode === 'kling') {{

          btnText.innerText = '▶ ريندر المشهد بمحرك Kling v3 السينمائي (720p HD اقتصادي بدون هزة)';

        }}

        if (badge) {{

          badge.innerText = 'Kling v3 - 720p HD موفر';

          badge.className = 'text-[10px] font-bold text-amber-300 bg-amber-500/20 px-2.5 py-0.5 rounded-full border border-amber-500/30';

        }}

      }} else {{

        if (btnText && currentComfySubMode === 'kling') {{

          btnText.innerText = '▶ ريندر نقل الحركة (Kling Motion 720p)';

        }}

        if (badge) {{

          badge.innerText = 'سيرفرلس سريع 3 ثوانٍ';

          badge.className = 'text-[10px] font-bold text-purple-300 bg-purple-500/20 px-2.5 py-0.5 rounded-full border border-purple-500/30';

        }}

      }}

    }}



    async function executeComfyKlingMotionRender() {{

      const sourceImg = (document.getElementById('comfy-lp-source-img').value || '').trim();

      const drivingVid = (document.getElementById('comfy-lp-driving-video').value || '').trim();



      if (!sourceImg) {{

        showToast('يرجى رفع صورة الشخصية أولاً يا أستاذنا.', 'warn');

        return;

      }}

      if (!drivingVid) {{

        showToast('يرجى رفع فيديو تعابير وانفعال الوجه التوجيهي (Driving Video).', 'warn');

        return;

      }}



      const btn = document.getElementById('comfy-render-btn');

      const btnText = document.getElementById('comfy-render-btn-text');

      const placeholder = document.getElementById('comfy-placeholder');

      const spinner = document.getElementById('comfy-spinner');

      const resultBox = document.getElementById('comfy-result-container');

      const timer = document.getElementById('comfy-render-timer');

      const pBar = document.getElementById('comfy-progressbar');

      const spinnerText = document.getElementById('comfy-spinnerText');



      btn.disabled = true;

      btnText.innerText = '▶ ريندر نقل الحركة (Kling Motion 720p)';

      placeholder.classList.add('hidden');

      resultBox.classList.add('hidden');

      spinner.classList.remove('hidden');

      if (spinnerText) spinnerText.innerText = 'جاري تحليل تعابير الوجه وتطبيقها على بطلك...';



      let sec = 0;

      timer.innerText = '0 ثانية';

      pBar.style.width = '20%';

      const interval = setInterval(() => {{

        sec++;

        timer.innerText = sec + ' ثانية';

        if (sec > 3 && sec <= 20) pBar.style.width = (20 + sec * 4) + '%';

      }}, 1000);



      const selectedEngine = document.querySelector('input[name="motion_engine"]:checked')?.value || 'kling';

      if (selectedEngine === 'kling') {{

        btnText.innerText = 'جاري الريندر بمحرك Kling v3 السينمائي (1080p)... قد يستغرق دقيقة واحدة...';

        if (spinnerText) spinnerText.innerText = 'محرك Kling v3 يعالج فيزياء الحركة وتفاصيل البشرة بدقة 1080p...';

      }}



      try {{

        const res = await fetch('/api/comfyui/motion_control', {{

          method: 'POST',

          headers: {{ 'Content-Type': 'application/json' }},

          body: JSON.stringify({{

            source_image: sourceImg,

            driving_video: drivingVid,

            engine: selectedEngine

          }})

        }});



        const data = await res.json();

        clearInterval(interval);

        btn.disabled = false;

        btnText.innerText = '▶ ريندر نقل الحركة (Kling Motion 720p)';



        if (!data.success) {{

          spinner.classList.add('hidden');

          placeholder.classList.remove('hidden');

          showToast('فشل نقل الانفعال: ' + (data.error || 'خطأ غير معروف'), 'error');

          return;

        }}



        pBar.style.width = '100%';

        spinner.classList.add('hidden');

        resultBox.classList.remove('hidden');



        const previewBox = document.getElementById('comfy-preview-box');

        previewBox.innerHTML = `

          <div class="relative w-full h-full flex flex-col items-center justify-center p-2">

            <video src="${{data.url}}" autoplay loop controls playsinline class="max-h-[460px] max-w-full rounded-xl shadow-2xl border border-purple-500/50 object-contain"></video>

            <div class="mt-3 flex items-center gap-3">

              <a href="${{data.url}}" download="${{data.filename}}" class="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow flex items-center gap-2">

                <i class="fa-solid fa-download"></i> تحميل مشهد الانفعال (MP4)

              </a>

              <span class="text-xs text-purple-300 font-bold bg-purple-900/40 px-3 py-1.5 rounded-lg border border-purple-700/50">🎭 Kling Motion Render</span>

            </div>

          </div>

        `;



        lastRenderedComfyMedia = data.url;

        loadMediaIntoScreening(data.url, 'video', 'Kling Motion', 'نقل انفعالات الوجه');

        showToast('تم ريندر مشهد انفعالات الوجه بالكامل بنجاح! 🎭', 'success');

        speakText('انفعالات الوجه اتنقلت للشخصية بالمللي وجاهزة على الشاشة يا فندم!');

      }} catch(err) {{

        clearInterval(interval);

        btn.disabled = false;

        btnText.innerText = '▶ ريندر نقل الحركة (Kling Motion 720p)';

        spinner.classList.add('hidden');

        placeholder.classList.remove('hidden');

        showToast('تعذر ريندر نقل الحركة: ' + err, 'error');

      }}

    }}



    async function executeComfyLatentSyncRender() {{

      const videoSrc = (document.getElementById('comfy-ls-video-source').value || '').trim();

      const audioSrc = (document.getElementById('comfy-ls-audio-source').value || '').trim();



      if (!videoSrc) {{

        showToast('يرجى رفع كادر أو مشهد الشخصية أولاً يا أستاذنا.', 'warn');

        return;

      }}

      if (!audioSrc) {{

        showToast('يرجى رفع ملف الصوت أو الحوار (Audio Track) للمزامنة.', 'warn');

        return;

      }}



      const btn = document.getElementById('comfy-render-btn');

      const btnText = document.getElementById('comfy-render-btn-text');

      const placeholder = document.getElementById('comfy-placeholder');

      const spinner = document.getElementById('comfy-spinner');

      const resultBox = document.getElementById('comfy-result-container');

      const timer = document.getElementById('comfy-render-timer');

      const pBar = document.getElementById('comfy-progressbar');

      const spinnerText = document.getElementById('comfy-spinnerText');



      btn.disabled = true;

      btnText.innerText = 'جاري مزامنة ونطق الشفاه مع الصوت (LatentSync)...';

      placeholder.classList.add('hidden');

      resultBox.classList.add('hidden');

      spinner.classList.remove('hidden');

      if (spinnerText) spinnerText.innerText = 'جاري مطابقة حركة الشفاه والأسنان مع الحوار الصوتي...';



      let sec = 0;

      timer.innerText = '0 ثانية';

      pBar.style.width = '20%';

      const interval = setInterval(() => {{

        sec++;

        timer.innerText = sec + ' ثانية';

        if (sec > 3 && sec <= 25) pBar.style.width = (20 + sec * 3.5) + '%';

      }}, 1000);



      try {{

        const res = await fetch('/api/comfyui/latentsync', {{

          method: 'POST',

          headers: {{ 'Content-Type': 'application/json' }},

          body: JSON.stringify({{

            video_source: videoSrc,

            audio_source: audioSrc

          }})

        }});



        const data = await res.json();

        clearInterval(interval);

        btn.disabled = false;

        btnText.innerText = '▶ ريندر مزامنة ونطق الشفاه الآن (LatentSync)';



        if (!data.success) {{

          spinner.classList.add('hidden');

          placeholder.classList.remove('hidden');

          showToast('فشلت مزامنة الشفاه: ' + (data.error || 'خطأ غير معروف'), 'error');

          return;

        }}



        pBar.style.width = '100%';

        spinner.classList.add('hidden');

        resultBox.classList.remove('hidden');



        const previewBox = document.getElementById('comfy-preview-box');

        previewBox.innerHTML = `

          <div class="relative w-full h-full flex flex-col items-center justify-center p-2">

            <video src="${{data.url}}" autoplay loop controls playsinline class="max-h-[460px] max-w-full rounded-xl shadow-2xl border border-cyan-500/50 object-contain"></video>

            <div class="mt-3 flex items-center gap-3">

              <a href="${{data.url}}" download="${{data.filename}}" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-500 hover:to-teal-500 text-white text-xs font-bold rounded-xl shadow flex items-center gap-2">

                <i class="fa-solid fa-download"></i> تحميل مشهد الحوار المتزامن (MP4)

              </a>

              <span class="text-xs text-cyan-300 font-bold bg-cyan-900/40 px-3 py-1.5 rounded-lg border border-cyan-700/50">👄 LatentSync LipSync</span>

            </div>

          </div>

        `;



        lastRenderedComfyMedia = data.url;

        loadMediaIntoScreening(data.url, 'video', 'LatentSync', 'مزامنة ونطق الشفاه');

        showToast('تمت مزامنة ونطق الشفاه بنجاح كامل! 👄', 'success');

        speakText('مزامنة الشفايف مع الصوت خلصت ومطابقة تماماً يا أستاذ إيهاب!');

      }} catch(err) {{

        clearInterval(interval);

        btn.disabled = false;

        btnText.innerText = '▶ ريندر مزامنة ونطق الشفاه الآن (LatentSync)';

        spinner.classList.add('hidden');

        placeholder.classList.remove('hidden');

        showToast('تعذر تنفيذ LatentSync: ' + err, 'error');

      }}

    }}



    function handleComfyDispatch() {{
      if (currentComfySubMode === 'video') {{
        executeComfyVideoRender();
      }} else if (currentComfySubMode === 'kling') {{
        executeComfyKlingMotionRender();
      }} else if (currentComfySubMode === 'latentsync') {{
        executeComfyLatentSyncRender();
      }} else {{
        executeComfyRender();
      }}
    }}



    async function executeComfyVideoRender() {{

      const imgSource = document.getElementById('comfy-video-img-source').value.trim();

      if (!imgSource) {{

        showToast('يرجى اختيار كادر الصورة المراد تحريكها يا أستاذنا.', 'warn');

        return;

      }}



      const btn = document.getElementById('comfy-render-btn');

      const btnText = document.getElementById('comfy-render-btn-text');

      const placeholder = document.getElementById('comfy-placeholder');

      const spinner = document.getElementById('comfy-spinner');

      const resultBox = document.getElementById('comfy-result-container');

      const resultImg = document.getElementById('comfy-result-img');

      const timer = document.getElementById('comfy-render-timer');

      const pBar = document.getElementById('comfy-progressbar');

      const dlBtn = document.getElementById('comfy-download-btn');

      const spinnerText = document.getElementById('comfy-spinnerText');



      btn.disabled = true;

      btnText.innerText = 'جاري ريندر الفيديو على كارت الشاشة السحابي...';

      placeholder.classList.add('hidden');

      resultBox.classList.add('hidden');

      spinner.classList.remove('hidden');

      spinnerText.innerText = 'كارت الـ Blackwell يريندر حركة الفيديو الآن...';

      pBar.style.width = '30%';



      const startTs = Date.now();

      const interval = setInterval(() => {{

        const el = Math.floor((Date.now() - startTs) / 1000);

        timer.innerText = `ريندر الفيديو: ${{el}} ثانية`;

      }}, 500);



      const ckpt = document.getElementById('comfy-video-checkpoint').value;

      const motion = parseInt(document.getElementById('comfy-video-motion').value) || 127;

      const fps = parseInt(document.getElementById('comfy-video-fps').value) || 6;

      const autoStop = document.getElementById('comfy-autostop').checked;



      try {{

        pBar.style.width = '65%';

        const res = await fetch(`${{API_BASE}}/api/comfyui/generate_video`, {{

          method: 'POST',

          headers: {{ 'Content-Type': 'application/json' }},

          body: JSON.stringify({{

            image_url: imgSource,

            checkpoint: ckpt,

            motion_bucket_id: motion,

            fps: fps,

            auto_stop: autoStop,
            prompt: (document.getElementById('comfy-video-prompt')?.value || document.getElementById('comfy-prompt')?.value || '').trim()

          }})

        }});



        clearInterval(interval);

        const data = await res.json();

        spinner.classList.add('hidden');

        btn.disabled = false;

        btnText.innerText = '▶ ريندر مشهد الفيديو الآن (Comfy Video)';



        if (data.success && data.url) {{

          lastRenderedComfyMedia = data.url;

          resultBox.classList.remove('hidden');

          const resVid = document.getElementById('comfy-result-video');
          if (data.url.endsWith('.mp4') || data.url.endsWith('.webm') || data.media_type === 'video') {{
            if (resVid) {{
              resVid.src = data.url;
              resVid.classList.remove('hidden');
            }}
            if (resultImg) resultImg.classList.add('hidden');
          }} else {{
            if (resultImg) {{
              resultImg.src = data.url;
              resultImg.classList.remove('hidden');
            }}
            if (resVid) resVid.classList.add('hidden');
          }}

          dlBtn.href = data.url;

          dlBtn.download = data.filename || 'Cindy_Video.mp4';

          dlBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-down text-sm"></i> <span>تنزيل الفيديو فائق الجودة (MP4 / WebP)</span>';

          

          const totalSec = Math.floor((Date.now() - startTs) / 1000);

          timer.innerText = `اكتمل الريندر في ${{totalSec}} ثانية`;

          showToast(`تم ريندر مشهد الفيديو السينمائي بنجاح في ${{totalSec}} ثانية!`, 'success');

          

          if (autoStop) {{

            showToast('تم إيقاف وحذف الكارت السحابي تلقائياً لحماية رصيدك.', 'info');

            checkComfyStatus();

            refreshWalletStatus();

          }}

        }} else {{

          placeholder.classList.remove('hidden');

          showToast(data.error || 'تعذر استكمال ريندر الفيديو.', 'error');

        }}

      }} catch (err) {{

        clearInterval(interval);

        spinner.classList.add('hidden');

        btn.disabled = false;

        btnText.innerText = '▶ ريندر مشهد الفيديو الآن (Comfy Video)';

        placeholder.classList.remove('hidden');

        showToast('خطأ أثناء ريندر الفيديو: ' + err, 'error');

      }}

    }}



    async function refreshWalletStatus(showToastMsg = false) {{

      const icon = document.getElementById('wallet-refresh-icon');

      if (icon) icon.classList.add('fa-spin');

      try {{

        const res = await fetch(`${{API_BASE}}/api/wallet/status`);

        const data = await res.json();

        if (data.success && data.wallet) {{

          const rp = data.wallet.runpod;

          const fal = data.wallet.fal;

          const rpBadge = document.getElementById('wallet-runpod-badge');

          if (rpBadge) {{

            rpBadge.innerText = rp.connected ? `$${{rp.balance}}` : 'غير مربوط';

            if (rp.spend_per_hr > 0) {{

              rpBadge.title = `معدل الاستهلاك: $${{rp.spend_per_hr}}/ساعة`;

            }}

          }}

          const emBtn = document.getElementById('topbar-emergency-stop-btn');
          const emText = document.getElementById('topbar-emergency-stop-text');
          if (emBtn && rp) {{
            if (rp.active_pods > 0) {{
              emBtn.className = 'px-2.5 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] shadow-lg shadow-rose-900/50 border border-rose-400 animate-pulse flex items-center gap-1 transition cursor-pointer';
              if (emText) emText.innerText = `🛑 إيقاف RunPod (${{rp.active_pods}} كارت شغال)`;
            }} else {{
              emBtn.className = 'px-2.5 py-1 rounded-lg bg-cinema-800 hover:bg-rose-900/80 text-rose-300 hover:text-white border border-rose-500/40 font-bold text-[10px] flex items-center gap-1 transition cursor-pointer';
              if (emText) emText.innerText = '🛑 إيقاف RunPod';
            }}
          }}

          const falBadge = document.getElementById('wallet-fal-badge');

          if (falBadge) {{

            falBadge.innerText = fal.balance !== null ? `$${{fal.balance}}` : fal.status;

          }}

          if (showToastMsg) {{

            showToast(`الرصيد المحدث: RunPod ($${{rp.balance}}) | Fal.ai (${{fal.status}})`, 'info');

          }}

        }}

      }} catch (e) {{

        if (showToastMsg) showToast('تعذر جلب بيانات الرصيد: ' + e, 'error');

      }} finally {{

        if (icon) icon.classList.remove('fa-spin');

      }}

    }}



    async function stopComfyStudioPod(confirmUser = true) {{

      if (confirmUser && !confirm('هل تريد إيقاف وحذف استوديو ComfyUI السحابي الآن لحماية رصيدك بالكامل؟')) return;

      if (confirmUser) showToast('جاري إيقاف وحذف السيرفر السحابي...', 'info');

      try {{

        const res = await fetch(`${{API_BASE}}/api/comfyui/stop`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ action: 'terminate' }})
        }});
        const data = await res.json();
        if (confirmUser) showToast(data.message || 'تم إيقاف وحذف السيرفر السحابي بنجاح لحماية رصيدك.', 'success');
        checkComfyStatus();
        refreshWalletStatus(false);

      }} catch (e) {{

        if (confirmUser) showToast('خطأ: ' + e, 'error');

      }}

    }}



  
    // ========================================================
    // CORE DIRECTORIAL & RUNTIME FUNCTIONS RESTORED
    // ========================================================

    function showToast(msg, type = 'info') {{
      const root = document.getElementById('toast-root');
      if (!root) return;
      const toast = document.createElement('div');
      const bg = type === 'success' ? 'bg-emerald-600/90 text-white' : type === 'error' ? 'bg-rose-600/90 text-white' : type === 'warn' ? 'bg-amber-600/90 text-white' : 'bg-cinema-800/90 text-slate-200';
      toast.className = `${{bg}} backdrop-blur-md px-4 py-2.5 rounded-xl border border-white/10 shadow-2xl text-xs font-bold transition-all duration-300 flex items-center gap-2`;
      const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-circle-xmark' : type === 'warn' ? 'fa-triangle-exclamation' : 'fa-circle-info';
      toast.innerHTML = `<i class="fa-solid ${{icon}}"></i> <span>${{escapeHtml(msg)}}</span>`;
      root.appendChild(toast);
      setTimeout(() => {{
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }}, 4000);
    }}

    function copyToClipboard(btn, text) {{
      navigator.clipboard.writeText(text).then(() => {{
        showToast('تم نسخ البرومبت بنجاح! 📋', 'success');
      }}).catch(() => {{
        showToast('تعذر النسخ للحافظة.', 'error');
      }});
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    // --- 1. Mode Switcher (Video vs Image) ---
    function setGenerationMode(mode) {{
      currentMode = mode;
      const vBtn = document.getElementById('mode-btn-video');
      const iBtn = document.getElementById('mode-btn-image');
      const vGroup = document.getElementById('video-controls-group');
      const iGroup = document.getElementById('image-controls-group');

      if (mode === 'video') {{
        if (vBtn) vBtn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-black transition flex items-center gap-1.5 bg-cinema-gold text-cinema-900 shadow';
        if (iBtn) iBtn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-black text-slate-400 hover:text-white transition flex items-center gap-1.5';
        if (vGroup) vGroup.classList.remove('hidden');
        if (iGroup) iGroup.classList.add('hidden');
        currentSelectedModel = document.getElementById('active-video-model')?.value || 'Google Veo 3.1 Cinematic';
        updateDurationsForModel(currentSelectedModel);
        showToast('تم تفعيل أدوات الفيديو السينمائي 🎬', 'info');
      }} else {{
        if (iBtn) iBtn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-black transition flex items-center gap-1.5 bg-cinema-neon text-cinema-900 shadow';
        if (vBtn) vBtn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-black text-slate-400 hover:text-white transition flex items-center gap-1.5';
        if (iGroup) iGroup.classList.remove('hidden');
        if (vGroup) vGroup.classList.add('hidden');
        currentSelectedModel = document.getElementById('active-image-model')?.value || 'fal-ai/flux/schnell';
        showToast('تم تفعيل أدوات الصور والإطارات المفتاحية 📸', 'info');
      }}
    }}

    function syncSelectedModel() {{
      if (currentMode === 'video') {{
        currentSelectedModel = document.getElementById('active-video-model')?.value || 'MiniMax H3 Lite';
        updateDurationsForModel(currentSelectedModel);
      }} else {{
        currentSelectedModel = document.getElementById('active-image-model')?.value || 'fal-ai/flux/schnell';
      }}
      const badge = document.getElementById('active-prompt-target-badge');
      if (badge) badge.innerText = currentSelectedModel;
      const inp = document.getElementById('chat-input');
      if (inp) {{
        inp.placeholder = `اكتب فكرة المشهد هنا للتوليد بـ (${{currentSelectedModel}})... واضغط Enter أو تحدث بالصوت`;
      }}
    }}

    // Reference State
    let activeI2VStartUrl = '';
    let activeI2VEndUrl = '';
    let activeMotionCharUrl = '/outputs/upload_1793745039209_02c844e33a5898c7af2f08144bbb3a0c.jpg';
    let activeMotionVideoUrl = '/outputs/upload_1793745073905_Handheld_camera_filming_footage_.mp4';
    let activeV2VSourceUrl = '';

    const MODEL_REFERENCE_RULES = {{
      // 1. Text-Only Models
      'MiniMax H3 Lite': {{ category: 'text' }},
      'Wan 2.1 (Alibaba 14B)': {{ category: 'text' }},
      'CogVideoX-5B (THUDM)': {{ category: 'text' }},
      'Tencent HunyuanVideo': {{ category: 'text' }},
      'Kling AI Standard': {{ category: 'text' }},
      'Kling 4 / 3.0 Pro': {{ category: 'text' }},
      'Luma Ray 2 & Dream Machine': {{ category: 'text' }},
      'Google Veo 3.1 Fast': {{ category: 'text' }},
      'Google Veo 3.1 Cinematic': {{ category: 'text' }},

      // 2. Image-to-Video Models
      'Wan 2.1 Image-to-Video': {{ category: 'i2v', endFrame: false }},
      'CogVideoX-5B Image-to-Video': {{ category: 'i2v', endFrame: false }},
      'Stability SVD-XT': {{ category: 'i2v', endFrame: false }},
      'Flux 3 Max Image-to-Video': {{ category: 'i2v', endFrame: false }},
      'MiniMax H3 Max Turbo': {{ category: 'i2v', endFrame: false }},
      'Kling 1.6 Pro Image-to-Video': {{ category: 'i2v', endFrame: true }},
      'Luma Ray 2 Image-to-Video': {{ category: 'i2v', endFrame: true }},
      'Mischief-1 Image-to-Video': {{ category: 'i2v', endFrame: false }},

      // 3. Motion Control & Video-to-Video
      'Kling Motion Control (1080p)': {{ category: 'motion' }},
      'Kling O1 Video-to-Video Edit': {{ category: 'v2v' }},
      'Luma Ray 2 Modify': {{ category: 'v2v' }}
    }};

    function updateReferenceInputsForModel(modelName) {{
      const rule = MODEL_REFERENCE_RULES[modelName] || {{ category: 'text' }};
      
      const textBadge = document.getElementById('ref-mode-text-badge');
      const i2vPanel = document.getElementById('ref-mode-i2v-panel');
      const motionPanel = document.getElementById('ref-mode-motion-panel');
      const v2vPanel = document.getElementById('ref-mode-v2v-panel');
      const endWrapper = document.getElementById('i2v-end-wrapper');

      if (textBadge) textBadge.classList.add('hidden');
      if (i2vPanel) i2vPanel.classList.add('hidden');
      if (motionPanel) motionPanel.classList.add('hidden');
      if (v2vPanel) v2vPanel.classList.add('hidden');

      if (rule.category === 'text') {{
        if (textBadge) textBadge.classList.remove('hidden');
      }} else if (rule.category === 'i2v') {{
        if (i2vPanel) i2vPanel.classList.remove('hidden');
        if (endWrapper) {{
          if (rule.endFrame) endWrapper.classList.remove('hidden');
          else endWrapper.classList.add('hidden');
        }}
      }} else if (rule.category === 'motion') {{
        if (motionPanel) motionPanel.classList.remove('hidden');
        // Pre-populate thumbs if active
        if (activeMotionCharUrl) {{
          const t = document.getElementById('motion-char-thumb');
          const emp = document.getElementById('motion-char-empty');
          const act = document.getElementById('motion-char-active');
          if (t) t.src = activeMotionCharUrl;
          if (emp) emp.classList.add('hidden');
          if (act) act.classList.remove('hidden');
        }}
        if (activeMotionVideoUrl) {{
          const empV = document.getElementById('motion-video-empty');
          const actV = document.getElementById('motion-video-active');
          if (empV) empV.classList.add('hidden');
          if (actV) actV.classList.remove('hidden');
        }}
      }} else if (rule.category === 'v2v') {{
        if (v2vPanel) v2vPanel.classList.remove('hidden');
      }}
    }}

    function updateDurationsForModel(modelName) {{
      const durSelect = document.getElementById('video-duration-select');
      if (!durSelect) return;
      updateReferenceInputsForModel(modelName);
    }}

    // Reference Handlers
    async function handleI2VStartSelected(event) {{
      const file = event.target.files[0];
      if (!file) return;
      showToast('جاري رفع كادر البداية...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        activeI2VStartUrl = data.url;
        const thumb = document.getElementById('i2v-start-thumb');
        const emptyState = document.getElementById('i2v-start-empty');
        const activeState = document.getElementById('i2v-start-active');
        if (thumb) thumb.src = activeI2VStartUrl;
        if (emptyState) emptyState.classList.add('hidden');
        if (activeState) activeState.classList.remove('hidden');
        showToast('تم رفع كادر البداية بنجاح 🎬', 'success');
      }} catch (e) {{
        showToast('فشل رفع كادر البداية: ' + e, 'error');
      }}
    }}

    function useLastRenderedAsI2VStart() {{
      if (!lastRenderedComfyMedia) {{
        showToast('لم يتم توليد أي كادر بعد لاستخدامه!', 'warn');
        return;
      }}
      activeI2VStartUrl = lastRenderedComfyMedia;
      const thumb = document.getElementById('i2v-start-thumb');
      const emptyState = document.getElementById('i2v-start-empty');
      const activeState = document.getElementById('i2v-start-active');
      if (thumb) thumb.src = activeI2VStartUrl;
      if (emptyState) emptyState.classList.add('hidden');
      if (activeState) activeState.classList.remove('hidden');
      showToast('تم تثبيت آخر كادر كمرجع بداية!', 'success');
    }}

    function clearI2VStart() {{
      activeI2VStartUrl = '';
      const emptyState = document.getElementById('i2v-start-empty');
      const activeState = document.getElementById('i2v-start-active');
      if (emptyState) emptyState.classList.remove('hidden');
      if (activeState) activeState.classList.add('hidden');
    }}

    async function handleI2VEndSelected(event) {{
      const file = event.target.files[0];
      if (!file) return;
      showToast('جاري رفع كادر النهاية...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        activeI2VEndUrl = data.url;
        const thumb = document.getElementById('i2v-end-thumb');
        const emptyState = document.getElementById('i2v-end-empty');
        const activeState = document.getElementById('i2v-end-active');
        if (thumb) thumb.src = activeI2VEndUrl;
        if (emptyState) emptyState.classList.add('hidden');
        if (activeState) activeState.classList.remove('hidden');
        showToast('تم رفع كادر النهاية بنجاح! سينتقل المشهد بين الكادرين 🎬', 'success');
      }} catch (e) {{
        showToast('فشل رفع كادر النهاية: ' + e, 'error');
      }}
    }}

    function clearI2VEnd() {{
      activeI2VEndUrl = '';
      const emptyState = document.getElementById('i2v-end-empty');
      const activeState = document.getElementById('i2v-end-active');
      if (emptyState) emptyState.classList.remove('hidden');
      if (activeState) activeState.classList.add('hidden');
    }}

    async function handleMotionCharSelected(event) {{
      const file = event.target.files[0];
      if (!file) return;
      try {{
        const data = await uploadMediaFileToServer(file);
        activeMotionCharUrl = data.url;
        const thumb = document.getElementById('motion-char-thumb');
        const emptyState = document.getElementById('motion-char-empty');
        const activeState = document.getElementById('motion-char-active');
        if (thumb) thumb.src = activeMotionCharUrl;
        if (emptyState) emptyState.classList.add('hidden');
        if (activeState) activeState.classList.remove('hidden');
        showToast('تم رفع صورة الممثل لـ Kling Motion Control!', 'success');
      }} catch (e) {{
        showToast('فشل رفع صورة الممثل: ' + e, 'error');
      }}
    }}

    function useLastRenderedAsMotionChar() {{
      if (!lastRenderedComfyMedia) {{
        showToast('لا يوجد كادر سابق!', 'warn');
        return;
      }}
      activeMotionCharUrl = lastRenderedComfyMedia;
      const thumb = document.getElementById('motion-char-thumb');
      const emptyState = document.getElementById('motion-char-empty');
      const activeState = document.getElementById('motion-char-active');
      if (thumb) thumb.src = activeMotionCharUrl;
      if (emptyState) emptyState.classList.add('hidden');
      if (activeState) activeState.classList.remove('hidden');
      showToast('تم تثبيت الكادر الأخير كصورة ممثل!', 'success');
    }}

    function clearMotionChar() {{
      activeMotionCharUrl = '';
      const emptyState = document.getElementById('motion-char-empty');
      const activeState = document.getElementById('motion-char-active');
      if (emptyState) emptyState.classList.remove('hidden');
      if (activeState) activeState.classList.add('hidden');
    }}

    async function handleMotionVideoSelected(event) {{
      const file = event.target.files[0];
      if (!file) return;
      showToast('جاري رفع فيديو الحركة التوجيهي...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        activeMotionVideoUrl = data.url;
        const emptyState = document.getElementById('motion-video-empty');
        const activeState = document.getElementById('motion-video-active');
        if (emptyState) emptyState.classList.add('hidden');
        if (activeState) activeState.classList.remove('hidden');
        showToast('تم رفع فيديو الحركة التوجيهي بنجاح 💃', 'success');
      }} catch (e) {{
        showToast('فشل رفع الفيديو: ' + e, 'error');
      }}
    }}

    function clearMotionVideo() {{
      activeMotionVideoUrl = '';
      const emptyState = document.getElementById('motion-video-empty');
      const activeState = document.getElementById('motion-video-active');
      if (emptyState) emptyState.classList.remove('hidden');
      if (activeState) activeState.classList.add('hidden');
    }}

    async function handleV2VSourceSelected(event) {{
      const file = event.target.files[0];
      if (!file) return;
      showToast('جاري رفع الفيديو الأصلي المراد تعديله...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        activeV2VSourceUrl = data.url;
        const emptyState = document.getElementById('v2v-source-empty');
        const activeState = document.getElementById('v2v-source-active');
        if (emptyState) emptyState.classList.add('hidden');
        if (activeState) activeState.classList.remove('hidden');
        showToast('تم تحديد الفيديو الأصلي بنجاح 🎞️', 'success');
      }} catch (e) {{
        showToast('فشل رفع الفيديو: ' + e, 'error');
      }}
    }}

    function clearV2VSource() {{
      activeV2VSourceUrl = '';
      const emptyState = document.getElementById('v2v-source-empty');
      const activeState = document.getElementById('v2v-source-active');
      if (emptyState) emptyState.classList.remove('hidden');
      if (activeState) activeState.classList.add('hidden');
    }}

    function activateFromCard(mode, modelName) {{
      setGenerationMode(mode);
      if (mode === 'video') {{
        const sel = document.getElementById('active-video-model');
        if (sel) {{
          for (let opt of sel.options) {{
            if (opt.value.includes(modelName) || opt.innerText.includes(modelName)) {{
              sel.value = opt.value;
              break;
            }}
          }}
        }}
      }} else {{
        const sel = document.getElementById('active-image-model');
        if (sel) {{
          for (let opt of sel.options) {{
            if (opt.value.includes(modelName) || opt.innerText.includes(modelName)) {{
              sel.value = opt.value;
              break;
            }}
          }}
        }}
      }}
      syncSelectedModel();
      switchTab('chat');
      showToast(`تم تفعيل النموذج: ${{modelName}}`, 'success');
    }}

    // --- 2. Chat & Directorial Assistant ---
    function clearChatInput() {{
      const inp = document.getElementById('chat-input');
      if (inp) inp.value = '';
    }}

    function quickPrompt(text) {{
      const inp = document.getElementById('chat-input');
      if (inp) inp.value = text;
      handleDirectMessage(text);
    }}

    function handleChatSubmit(e) {{
      if (e && e.preventDefault) e.preventDefault();
      const inp = document.getElementById('chat-input');
      const val = (inp?.value || '').trim();
      if (!val) return;
      inp.value = '';
      handleDirectMessage(val);
    }}

    async function handleDirectMessage(userMessage) {{
      syncSelectedModel();
      appendUserMessage(userMessage);

      const isArabic = /[؀-ۿ]/.test(userMessage);
      appendTypingIndicator('سيندي (المساعدة الإخراجية) تصيغ البرومبت السينمائي...');

      try {{
        const aspectVal = (currentMode === 'video') ?
          (document.getElementById('video-aspect-select')?.value || '16:9') :
          (document.getElementById('image-aspect-select')?.value || '16:9');

        const res = await fetch(`${{API_BASE}}/api/chat`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            message: userMessage,
            current_model: currentSelectedModel,
            current_mode: currentMode,
            aspect_ratio: aspectVal
          }})
        }});

        removeTypingIndicator();

        if (res.ok) {{
          const data = await res.json();
          appendCindyChatReply(data);
          if (voiceOutputEnabled && data.voice_text) {{
            speakText(data.voice_text, isArabic ? 'ar' : 'en');
          }}
        }} else {{
          appendCindyFallback(userMessage);
        }}
      }} catch (err) {{
        removeTypingIndicator();
        appendCindyFallback(userMessage);
      }}
    }}

    function appendUserMessage(text) {{
      const c = document.getElementById('chat-messages-container');
      if (!c) return;
      const div = document.createElement('div');
      div.className = 'flex items-start gap-3 justify-end';
      div.innerHTML = `
        <div class="bg-gradient-to-r from-blue-900/80 to-cinema-700 border border-blue-500/50 rounded-2xl rounded-tl-none p-3.5 max-w-xl text-slate-100 shadow-md">
          <div class="text-[10px] text-blue-200 mb-1 flex items-center justify-end gap-1">
            <span>أنت (المخرج)</span>
            <i class="fa-solid fa-user text-[9px]"></i>
          </div>
          <div class="text-sm font-semibold">${{escapeHtml(text)}}</div>
        </div>
      `;
      c.appendChild(div);
      c.scrollTop = c.scrollHeight;
    }}

    function appendTypingIndicator(msg = 'سيندي تكتب استشارتها الإخراجية...') {{
      removeTypingIndicator();
      const c = document.getElementById('chat-messages-container');
      if (!c) return;
      const div = document.createElement('div');
      div.id = 'chat-typing-indicator';
      div.className = 'flex items-center gap-2 text-slate-400 text-xs py-2';
      div.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-cinema-gold"></i> <span>${{escapeHtml(msg)}}</span>`;
      c.appendChild(div);
      c.scrollTop = c.scrollHeight;
    }}

    function removeTypingIndicator() {{
      const el = document.getElementById('chat-typing-indicator');
      if (el) el.remove();
    }}

    function appendCindyChatReply(data) {{
      const c = document.getElementById('chat-messages-container');
      if (!c) return;
      const div = document.createElement('div');
      div.className = 'flex items-start gap-3';

      let shotCardHtml = '';
      if (data.has_shot && data.shot && data.shot.prompt) {{
        const promptText = data.shot.prompt;
        const shotTitle = data.shot.title || 'كادر سينمائي مقترح';
        const shotNotes = data.shot.notes || '';
        const modelName = data.shot.suggested_model || currentSelectedModel;

        shotCardHtml = `
          <div class="bg-cinema-900/95 border border-cinema-gold/60 rounded-2xl p-4 space-y-3 mt-2 shadow-2xl">
            <div class="flex items-center justify-between text-xs border-b border-cinema-800 pb-2.5">
              <span class="font-black text-cinema-gold flex items-center gap-2 text-sm">
                <i class="fa-solid fa-clapperboard text-amber-400"></i> ${{escapeHtml(shotTitle)}}
              </span>
              <button type="button" data-prompt="${{escapeHtml(promptText)}}" onclick="copyToClipboard(this, this.dataset.prompt)" class="px-3 py-1.5 bg-gradient-to-r from-cinema-gold to-amber-500 hover:from-amber-400 hover:to-yellow-500 text-cinema-900 font-black rounded-xl text-xs flex items-center gap-1.5 shadow-lg transition">
                <i class="fa-solid fa-copy"></i>
                <span>نسخ البرومبت الاحترافي 📋</span>
              </button>
            </div>

            ${{shotNotes ? `<p class="text-xs text-slate-200 leading-relaxed font-semibold"><i class="fa-solid fa-video text-cinema-gold ml-1"></i> ${{escapeHtml(shotNotes)}}</p>` : ''}}

            <pre class="font-mono text-xs text-amber-200 bg-cinema-950/90 p-3.5 rounded-xl border border-cinema-800 whitespace-pre-wrap select-all overflow-x-auto leading-relaxed shadow-inner" dir="ltr">${{escapeHtml(promptText)}}</pre>

            <div class="pt-1 flex flex-wrap items-center gap-2">
              <button type="button" data-prompt="${{escapeHtml(promptText)}}" onclick="copyToClipboard(this, this.dataset.prompt)" class="py-2 px-3 bg-cinema-gold hover:bg-amber-400 text-cinema-900 font-black rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-lg transition">
                <i class="fa-solid fa-copy"></i>
                <span>نسخ البرومبت</span>
              </button>
              <button type="button" data-prompt="${{escapeHtml(promptText)}}" data-mode="${{escapeHtml(data.shot.mode || currentMode)}}" onclick="sendPromptToComfyStudio(this.dataset.prompt, this.dataset.mode)" class="py-2 px-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-extrabold rounded-xl text-xs flex items-center justify-center gap-1.5 shadow-lg transition">
                <i class="fa-solid fa-bolt text-amber-300"></i>
                <span>فتح وريندر في ComfyUI (Wan / SDXL) 🚀</span>
              </button>
              <button type="button" data-prompt="${{escapeHtml(promptText)}}" data-mode="${{escapeHtml(data.shot.mode || currentMode)}}" data-model="${{escapeHtml(modelName)}}" onclick="executeParametricShot(this.dataset.prompt, this.dataset.mode, this.dataset.model)" class="py-2 px-3 bg-cinema-800 hover:bg-cinema-700 border border-cinema-neon/50 text-cyan-200 font-bold rounded-xl text-xs flex items-center justify-center gap-1.5 transition">
                <i class="fa-solid fa-cloud text-cinema-neon"></i>
                <span>تنفيذ سحابي (${{escapeHtml(modelName)}})</span>
              </button>
            </div>
          </div>
        `;
      }}

      div.innerHTML = `
        <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-cinema-gold flex items-center justify-center font-bold text-cinema-900 flex-shrink-0 shadow">
          <i class="fa-solid fa-clapperboard text-xs"></i>
        </div>
        <div class="flex-1 space-y-2">
          <div class="bg-cinema-800/90 border border-cinema-700/80 rounded-2xl rounded-tr-none p-4 shadow-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-black text-cinema-gold">سيندي | المساعدة الإخراجية</span>
              <span class="text-[10px] text-blue-400 font-bold">Cindy 1st AD</span>
            </div>
            <div class="text-sm text-slate-200 leading-relaxed font-medium">
              ${{escapeHtml(data.reply || '').split(String.fromCharCode(10)).join('<br>')}}
            </div>
          </div>
          ${{shotCardHtml}}
        </div>
      `;
      c.appendChild(div);
      c.scrollTop = c.scrollHeight;
    }}

    function appendCindyFallback(userMessage) {{
      appendCindyChatReply({{
        reply: "أنا سامعاك يا أستاذنا المخرج! تم استلام توجيهك وسأقوم بتجهيز البرومبت السينمائي المطلوب.",
        has_shot: false
      }});
    }}

    async function executeParametricShot(promptText, mode, model) {{
      switchTab('screening');
      const loader = document.getElementById('screen-loader');
      const loaderText = document.getElementById('screen-loader-text');
      const img = document.getElementById('screen-img-display');
      const video = document.getElementById('screen-video-display');
      const grid = document.getElementById('screen-grid-display');

      if (loader) loader.classList.remove('hidden');
      if (loaderText) loaderText.innerText = `سيندي تقوم بالريندر السحابي الآن (${{model}})...`;
      const promptEl = document.getElementById('screen-active-prompt');
      if (promptEl) promptEl.innerText = promptText;
      const modelTagEl = document.getElementById('screen-model-tag');
      if (modelTagEl) modelTagEl.innerText = model;

      try {{
        const dur = document.getElementById('video-duration-select')?.value || 5;
        const aspect = (mode === 'video') ? (document.getElementById('video-aspect-select')?.value || '16:9') : (document.getElementById('image-aspect-select')?.value || '16:9');
        const numImgs = document.getElementById('image-count-select')?.value || 1;

        // Build smart reference payload based on model rules
        const customParams = {{}};
        const rule = MODEL_REFERENCE_RULES[model] || {{ category: 'text' }};
        if (rule.category === 'i2v') {{
          if (!activeI2VStartUrl && lastRenderedComfyMedia) {{
            activeI2VStartUrl = lastRenderedComfyMedia;
          }}
          if (activeI2VStartUrl) customParams.image_url = activeI2VStartUrl;
          if (rule.endFrame && activeI2VEndUrl) customParams.end_image_url = activeI2VEndUrl;
        }} else if (rule.category === 'motion') {{
          customParams.image_url = activeMotionCharUrl;
          customParams.video_url = activeMotionVideoUrl;
        }} else if (rule.category === 'v2v') {{
          customParams.video_url = activeV2VSourceUrl;
        }}

        const res = await fetch(`${{API_BASE}}/api/generate`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            prompt: promptText,
            mode: mode,
            model: model,
            duration: dur,
            aspect_ratio: aspect,
            num_images: numImgs,
            params: customParams
          }})
        }});

        if (loader) loader.classList.add('hidden');
        if (res.ok) {{
          const data = await res.json();
          if (data.url) {{
            lastRenderedComfyMedia = data.url;
            if (mode === 'video' || data.url.endsWith('.mp4') || data.url.endsWith('.webm')) {{
              if (video) {{ video.src = data.url; video.classList.remove('hidden'); video.play(); }}
              if (img) img.classList.add('hidden');
              if (grid) grid.classList.add('hidden');
            }} else {{
              if (img) {{ img.src = data.url; img.classList.remove('hidden'); }}
              if (video) video.classList.add('hidden');
              if (grid) grid.classList.add('hidden');
            }}
            showToast('تم الريندر السحابي بنجاح يا مخرجنا!', 'success');
          }} else if (data.images && data.images.length > 1) {{
            if (grid) {{
              grid.innerHTML = data.images.map(u => `<img src="${{u}}" class="w-full h-auto rounded-lg border border-cinema-700 cursor-pointer" onclick="selectGridImageForEdit('${{u}}')">`).join('');
              grid.classList.remove('hidden');
            }}
            if (img) img.classList.add('hidden');
            if (video) video.classList.add('hidden');
            showToast('تم توليد شبكة الصور بنجاح!', 'success');
          }}
        }} else {{
          const err = await res.json();
          showToast(err.error || 'تعذر الريندر السحابي.', 'error');
        }}
      }} catch (e) {{
        if (loader) loader.classList.add('hidden');
        showToast('خطأ أثناء الريندر: ' + e.message, 'error');
      }}
    }}

    // --- 3. Voice Output & Recognition ---
    function toggleVoiceOutput() {{
      voiceOutputEnabled = !voiceOutputEnabled;
      const btn = document.getElementById('voice-output-btn');
      if (btn) {{
        btn.innerHTML = voiceOutputEnabled ? '<i class="fa-solid fa-volume-high text-cinema-gold"></i>' : '<i class="fa-solid fa-volume-xmark text-slate-500"></i>';
      }}
      showToast(voiceOutputEnabled ? 'تم تفعيل صوت سيندي 🔊' : 'تم كتم صوت سيندي 🔇', 'info');
    }}

    function initSpeechVoices() {{
      if ('speechSynthesis' in window) {{
        availableVoices = window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = () => {{
          availableVoices = window.speechSynthesis.getVoices();
        }};
      }}
    }}

    function speakText(text, lang = 'ar') {{
      if (!voiceOutputEnabled || !('speechSynthesis' in window) || !text) return;
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 1.05;
      utt.pitch = 1.1;
      const match = availableVoices.find(v => v.lang.startsWith(lang));
      if (match) utt.voice = match;
      window.speechSynthesis.speak(utt);
    }}

    function initVoiceRecognition() {{
      const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRec) return;
      recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'ar-EG';

      recognition.onresult = (e) => {{
        const transcript = e.results[0][0].transcript;
        const inp = document.getElementById('chat-input');
        if (inp) {{
          inp.value = transcript;
          handleChatSubmit(new Event('submit'));
        }}
      }};

      recognition.onend = () => {{
        isRecording = false;
        const btn = document.getElementById('voice-record-btn');
        if (btn) btn.classList.remove('animate-pulse', 'bg-rose-500');
        const bar = document.getElementById('voice-activity-bar');
        if (bar) bar.classList.add('hidden');
      }};

      recognition.onerror = () => {{
        isRecording = false;
        const btn = document.getElementById('voice-record-btn');
        if (btn) btn.classList.remove('animate-pulse', 'bg-rose-500');
        const bar = document.getElementById('voice-activity-bar');
        if (bar) bar.classList.add('hidden');
      }};
    }}

    function toggleVoiceRecording() {{
      if (!recognition) {{
        showToast('التعرف على الصوت غير مدعوم في هذا المتصفح (يفضل Chrome/Edge).', 'warn');
        return;
      }}
      if (isRecording) {{
        stopVoiceRecognition();
      }} else {{
        try {{
          recognition.start();
          isRecording = true;
          const btn = document.getElementById('voice-record-btn');
          if (btn) btn.classList.add('animate-pulse', 'bg-rose-500');
          const bar = document.getElementById('voice-activity-bar');
          if (bar) bar.classList.remove('hidden');
        }} catch (e) {{}}
      }}
    }}

    function stopVoiceRecognition() {{
      if (recognition && isRecording) {{
        recognition.stop();
      }}
    }}

        // ==========================================
    // --- 4. Vault & API Keys Management ---
    // ==========================================
    const VAULT_METADATA = {{
      fal: {{
        name: 'Fal.ai API Key',
        desc: 'المحرك الأساسي لـ Kling Motion Control, Kling 1.6 Pro, Luma Ray 2, Wan 2.1, FLUX.1 Pro Ultra',
        icon: 'fa-bolt text-amber-400',
        badge: 'مهم جداً للفيديو',
        testable: true
      }},
      runpod: {{
        name: 'RunPod API Key',
        desc: 'إدارة سيرفرات وكروت الشاشة السحابية (RTX 4090, ComfyUI, وتدريب LoRAs)',
        icon: 'fa-server text-purple-400',
        badge: 'إدارة كروت الشاشة',
        testable: true
      }},
      gemini: {{
        name: 'Google Gemini API Key',
        desc: 'مساعد المخرج الفوري وتحليل اللقطات والسيناريو الإخراجي',
        icon: 'fa-brain text-emerald-400',
        badge: 'عقل المخرج الذكي',
        testable: true
      }},
      huggingface: {{
        name: 'Hugging Face Token',
        desc: 'سحب أوزان النماذج والـ Checkpoints وتصدير اللورات إلى HuggingFace Hub',
        icon: 'fa-cube text-yellow-400',
        badge: 'أوزان النماذج',
        testable: false
      }},
      local_comfyui: {{
        name: 'ComfyUI Server Endpoint URL',
        desc: 'رابط خادم ComfyUI السحابي أو المحلي للريندر المباشر بدون أسلاك',
        icon: 'fa-network-wired text-cyan-400',
        badge: 'سيرفر ComfyUI',
        testable: false,
        isUrl: true
      }},
      local_ollama: {{
        name: 'Local Ollama URL',
        desc: 'رابط خادم Ollama لتشغيل نماذج النصوص المحلية بدون إنترنت',
        icon: 'fa-microchip text-slate-400',
        badge: 'محلي أوفلاين',
        testable: false,
        isUrl: true
      }},
      hedra: {{
        name: 'Hedra Character Key',
        desc: 'توليد حركات الوجوه والشخصيات الناطقة التعبيرية',
        icon: 'fa-masks-theater text-indigo-400',
        badge: 'وجوه ناطقة',
        testable: false
      }},
      elevenlabs: {{
        name: 'ElevenLabs Voice Key',
        desc: 'التعليق الصوتي السينمائي وأصوات الشخصيات والدراما الصوتية',
        icon: 'fa-waveform-lines text-rose-400',
        badge: 'أصوات سينمائية',
        testable: false
      }}
    }};

    async function loadVaultStatus() {{
      const icon = document.getElementById('vault-refresh-icon');
      if (icon) icon.classList.add('fa-spin');
      try {{
        const res = await fetch(`${{API_BASE}}/api/vault/status`);
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        const data = await res.json();
        renderVaultCards(data);
      }} catch (e) {{
        console.error('Failed to load vault status:', e);
        showToast('تعذر جلب حالة الخزنة: ' + e, 'error');
      }} finally {{
        if (icon) icon.classList.remove('fa-spin');
      }}
    }}

    function renderVaultCards(vaultData) {{
      const grid = document.getElementById('vault-services-grid');
      if (!grid) return;

      const services = Object.keys(VAULT_METADATA);
      grid.innerHTML = services.map(svc => {{
        const meta = VAULT_METADATA[svc];
        const info = vaultData[svc] || {{ configured: false, masked: 'غير مضاف' }};
        const isConfigured = info.configured;
        const displayVal = meta.isUrl ? (info.url || 'غير محدد') : (info.masked || 'غير مضاف');

        return `
          <div class="vault-key-card bg-cinema-950/90 border ${{isConfigured ? 'border-cinema-700/80' : 'border-dashed border-cinema-800'}} rounded-2xl p-4.5 space-y-3 shadow-lg hover:border-cinema-gold/40 transition">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-xl bg-cinema-900 border border-cinema-700 flex items-center justify-center text-sm shadow">
                  <i class="fa-solid ${{meta.icon}}"></i>
                </div>
                <div>
                  <h4 class="font-bold text-slate-100 text-xs flex items-center gap-1.5">
                    ${{meta.name}}
                  </h4>
                  <span class="text-[10px] text-slate-400">${{meta.desc}}</span>
                </div>
              </div>
              <span class="text-[9px] px-2 py-0.5 rounded-full font-bold font-mono shrink-0 ${{isConfigured ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-slate-800 text-slate-400'}}">
                ${{isConfigured ? '✓ متصل' : '✕ غير مضاف'}}
              </span>
            </div>

            <!-- Current Value Display -->
            <div class="bg-cinema-900/90 rounded-xl p-2.5 border border-cinema-800 flex items-center justify-between text-xs font-mono">
              <div class="flex items-center gap-2 overflow-hidden text-ellipsis">
                <span class="text-slate-500 text-[10px]">القيمة الحالية:</span>
                <span class="font-bold text-amber-200 text-[11px] truncate" id="vault-display-${{svc}}">${{displayVal}}</span>
              </div>
            </div>

            <!-- Input to update key -->
            <div class="space-y-1.5 pt-1">
              <div class="flex items-center gap-2">
                <div class="relative flex-1">
                  <input type="${{meta.isUrl ? 'text' : 'password'}}" id="vault-input-${{svc}}" placeholder="${{meta.isUrl ? 'أدخل الرابط الجديد...' : 'ألصق المفتاح الجديد لتحديثه...'}}" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-1.5 text-xs text-slate-100 font-mono placeholder-slate-500 focus:outline-none focus:border-cinema-gold">
                  ${{!meta.isUrl ? `
                    <button type="button" onclick="toggleVaultVisibility('${{svc}}')" class="absolute left-2.5 top-2 text-slate-500 hover:text-slate-300 text-xs">
                      <i class="fa-solid fa-eye" id="vault-eye-${{svc}}"></i>
                    </button>
                  ` : ''}}
                </div>
                <button type="button" onclick="saveVaultKey('${{svc}}')" class="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 font-bold text-xs flex items-center gap-1 transition shadow cursor-pointer shrink-0">
                  <i class="fa-solid fa-floppy-disk text-[11px]"></i>
                  <span>حفظ</span>
                </button>
                ${{meta.testable ? `
                  <button type="button" onclick="testVaultKey('${{svc}}')" class="px-2.5 py-1.5 rounded-xl bg-cinema-800 hover:bg-cinema-700 text-slate-300 border border-cinema-700 text-xs font-bold flex items-center gap-1 transition shadow cursor-pointer shrink-0" title="اختبار صلاحية المفتاح">
                    <i class="fa-solid fa-bolt text-[11px] text-amber-400"></i>
                    <span>اختبار</span>
                  </button>
                ` : ''}}
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function toggleVaultVisibility(svc) {{
      const inp = document.getElementById(`vault-input-${{svc}}`);
      const eye = document.getElementById(`vault-eye-${{svc}}`);
      if (!inp) return;
      if (inp.type === 'password') {{
        inp.type = 'text';
        if (eye) eye.className = 'fa-solid fa-eye-slash';
      }} else {{
        inp.type = 'password';
        if (eye) eye.className = 'fa-solid fa-eye';
      }}
    }}

    async function saveVaultKey(svc) {{
      const inp = document.getElementById(`vault-input-${{svc}}`);
      if (!inp || !inp.value.trim()) {{
        showToast('يرجى كتابة المفتاح الجديد أولاً قبل الحفظ!', 'warning');
        return;
      }}
      const val = inp.value.trim();
      showToast(`جاري حفظ وتأمين مفتاح ${{svc}} في الخزنة...`, 'info');
      try {{
        const res = await fetch(`${{API_BASE}}/api/vault/update`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ service: svc, key_value: val }})
        }});
        const data = await res.json();
        if (data.success) {{
          showToast(data.message || `تم حفظ وتأمين مفتاح ${{svc}} بنجاح!`, 'success');
          inp.value = '';
          loadVaultStatus();
          refreshWalletStatus(false);
        }} else {{
          showToast(data.error || 'فشل حفظ المفتاح.', 'error');
        }}
      }} catch (e) {{
        showToast('خطأ أثناء الحفظ: ' + e, 'error');
      }}
    }}

    async function testVaultKey(svc) {{
      showToast(`جاري اختبار الاتصال بخدمة ${{svc}}...`, 'info');
      try {{
        const res = await fetch(`${{API_BASE}}/api/vault/test_key`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ service: svc }})
        }});
        const data = await res.json();
        if (data.success) {{
          showToast(data.message || `مفتاح ${{svc}} متصل بنجاح!`, 'success');
        }} else {{
          showToast(data.error || `فشل اختبار مفتاح ${{svc}}`, 'error');
        }}
      }} catch (e) {{
        showToast('خطأ أثناء الاختبار: ' + e, 'error');
      }}
    }}

    function filterVault() {{
      const q = (document.getElementById('vault-search-input')?.value || '').toLowerCase();
      const cards = document.querySelectorAll('.vault-key-card');
      cards.forEach(c => {{
        const txt = c.innerText.toLowerCase();
        c.style.display = txt.includes(q) ? '' : 'none';
      }});
    }}

    // --- 5. LoRA Actors Studio ---
    let currentLoraGenMode = 'image';
    let loraDatasetImages = [];

    function setLoraGenMode(mode) {{
      currentLoraGenMode = mode;
      const imgBtn = document.getElementById('lora-mode-img-btn');
      const vidBtn = document.getElementById('lora-mode-vid-btn');
      if (imgBtn && vidBtn) {{
        if (mode === 'image') {{
          imgBtn.className = 'px-3 py-1 rounded-lg bg-cinema-gold text-cinema-900 font-bold text-xs shadow';
          vidBtn.className = 'px-3 py-1 rounded-lg bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
        }} else {{
          vidBtn.className = 'px-3 py-1 rounded-lg bg-cinema-gold text-cinema-900 font-bold text-xs shadow';
          imgBtn.className = 'px-3 py-1 rounded-lg bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
        }}
      }}
    }}

    function switchLoraSubtab(tab) {{
      const testSec = document.getElementById('lora-subtab-test');
      const trainSec = document.getElementById('lora-subtab-train');
      const btnTest = document.getElementById('lora-btn-subtab-test');
      const btnTrain = document.getElementById('lora-btn-subtab-train');
      if (tab === 'test') {{
        if (testSec) testSec.classList.remove('hidden');
        if (trainSec) trainSec.classList.add('hidden');
        if (btnTest) btnTest.className = 'px-4 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs shadow';
        if (btnTrain) btnTrain.className = 'px-4 py-2 rounded-xl bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
      }} else {{
        if (testSec) testSec.classList.add('hidden');
        if (trainSec) trainSec.classList.remove('hidden');
        if (btnTrain) btnTrain.className = 'px-4 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs shadow';
        if (btnTest) btnTest.className = 'px-4 py-2 rounded-xl bg-cinema-800 text-slate-400 font-bold text-xs hover:text-white';
      }}
    }}

    function toggleTrainEngine(engine) {{}}
    function toggleImportLoraModal(show) {{
      const m = document.getElementById('import-lora-modal');
      if (m) m.classList.toggle('hidden', !show);
    }}

    async function submitImportLora(e) {{
      if (e && e.preventDefault) e.preventDefault();
      showToast('جاري استيراد الممثل (LoRA)...', 'info');
    }}

    function insertLoraTriggerToPrompt(trigger) {{
      const inp = document.getElementById('lora-gen-prompt');
      if (inp) {{
        inp.value = trigger + ' ' + inp.value;
      }}
    }}

    function onLoraSelectChanged() {{
      const sel = document.getElementById('lora-select');
      const trig = sel?.options[sel.selectedIndex]?.dataset?.trigger || '';
      const badge = document.getElementById('lora-trigger-badge');
      if (badge) {{
        badge.innerText = trig ? `Trigger: ${{trig}}` : 'لا توجد كلمة مفتاحية';
      }}
    }}

    function handleLoraFilesSelected(e) {{
      const files = e.target.files;
      if (!files || !files.length) return;
      showToast(`تم اختيار ${{files.length}} ملفات لتدريب الممثل!`, 'success');
    }}

    function clearLoraDataset() {{
      loraDatasetImages = [];
      const prev = document.getElementById('lora-dataset-preview');
      if (prev) prev.innerHTML = '';
      showToast('تم مسح مجموعة صور التدريب.', 'info');
    }}

    async function startLoraTraining() {{
      showToast('جاري بدء جلسة تدريب الممثل LoRA على كروت GPU...', 'info');
    }}

    async function refreshLoraLibrary() {{
      try {{
        const res = await fetch(`${{API_BASE}}/api/lora/list`);
        if (!res.ok) return;
        const d = await res.json();
        const sel = document.getElementById('lora-select');
        if (sel && d.models) {{
          sel.innerHTML = d.models.map(m => `<option value="${{m.path || m.name}}" data-trigger="${{m.trigger_word || ''}}">${{m.name}} (${{m.trigger_word || 'LoRA'}})</option>`).join('');
          onLoraSelectChanged();
        }}
      }} catch (e) {{}}
    }}

    async function executeLoraGeneration() {{
      const prompt = document.getElementById('lora-gen-prompt')?.value || '';
      const lora = document.getElementById('lora-select')?.value || '';
      if (!prompt) {{
        showToast('يرجى كتابة برومبت التوليد للممثل.', 'warn');
        return;
      }}
      executeParametricShot(prompt, currentLoraGenMode, 'FLUX LoRA Actor');
    }}

    // --- 6. Screening & Media Management ---
    function saveCurrentMedia() {{
      const img = document.getElementById('screen-img-display');
      const video = document.getElementById('screen-video-display');
      const src = (!video?.classList.contains('hidden') && video?.src) ? video.src : img?.src;
      if (!src) {{
        showToast('لا توجد وسائط نشطة للحفظ حالياً.', 'warn');
        return;
      }}
      downloadSpecificMedia(src, 'Cindy_Cinema_Shot');
    }}

    function downloadSpecificMedia(url, name) {{
      const a = document.createElement('a');
      a.href = url;
      a.download = name || 'cindy_media';
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast('بدأ تحميل الملف! 📥', 'success');
    }}

    function executeMediaEdit() {{
      const prompt = document.getElementById('edit-media-prompt')?.value || '';
      if (!prompt) {{
        showToast('يرجى كتابة تعليمات التعديل أولاً.', 'warn');
        return;
      }}
      showToast('جاري تطبيق التعديل السينمائي على الكادر...', 'info');
    }}

    
    // Universal Media Uploader (Images & Videos)
    async function uploadMediaFileToServer(file) {{
      return new Promise((resolve, reject) => {{
        if (!file) return reject('لم يتم تحديد أي ملف.');
        const reader = new FileReader();
        reader.onerror = () => reject('فشل قراءة الملف من الجهاز.');
        reader.onload = async (e) => {{
          try {{
            const res = await fetch(`${{API_BASE}}/api/upload`, {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{
                data_url: e.target.result,
                filename: file.name
              }})
            }});
            const data = await res.json();
            if (data.success && data.url) {{
              resolve(data);
            }} else {{
              reject(data.error || 'تعذر حفظ الملف على السيرفر.');
            }}
          }} catch (err) {{
            reject(err.message || err);
          }}
        }};
        reader.readAsDataURL(file);
      }});
    }}

    async function emergencyStopAllRunpod(confirmUser = true) {{
      if (confirmUser && !confirm('هل تريد إيقاف وحذف جميع أجهزة وسيرفرات RunPod فوراً لوقف استهلاك الرصيد؟')) return;
      showToast('جاري إيقاف وحذف سيرفرات RunPod لحماية رصيدك...', 'info');
      try {{
        const res = await fetch(`${{API_BASE}}/api/runpod/terminate_all`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{}})
        }});
        const data = await res.json();
        showToast(data.message || 'تم إيقاف وحذف السيرفرات السحابية بنجاح!', 'success');
        refreshWalletStatus(false);
        checkComfyStatus();
      }} catch (e) {{
        showToast('خطأ أثناء إيقاف RunPod: ' + e, 'error');
      }}
    }}


function triggerMediaUpload(ctx = 'chat') {{
      const f = document.getElementById('media-upload-input');
      if (f) f.click();
    }}

        async function handleMediaFileSelected(e) {{
      const file = e.target.files[0];
      if (!file) return;

      const isVideo = file.type.startsWith('video/') || /\.(mp4|webm|mov|mkv)$/i.test(file.name);
      const prevBox = document.getElementById('chat-attachment-preview');
      const thumbBox = document.getElementById('chat-attach-thumb-box');
      const nameEl = document.getElementById('chat-attach-name');
      const badgeEl = document.getElementById('chat-attach-badge');

      if (prevBox) prevBox.classList.remove('hidden');
      if (nameEl) nameEl.innerText = file.name;
      if (badgeEl) badgeEl.innerText = isVideo ? 'فيديو مرفق (جاري الرفع...)' : 'صورة مرجعية (جاري الرفع...)';

      // Instant local preview
      const localUrl = URL.createObjectURL(file);
      if (thumbBox) {{
        if (isVideo) {{
          thumbBox.innerHTML = `<video src="${{localUrl}}" autoplay muted loop class="w-full h-full object-cover"></video>`;
        }} else {{
          thumbBox.innerHTML = `<img src="${{localUrl}}" class="w-full h-full object-cover">`;
        }}
      }}

      showToast(`جاري رفع ${{isVideo ? 'الفيديو' : 'الصورة'}} إلى السيرفر...`, 'info');

      try {{
        const data = await uploadMediaFileToServer(file);
        currentAttachedMedia = data.url;
        if (!isVideo) {{
          setAsVideoReference(data.url);
          if (badgeEl) badgeEl.innerText = 'صورة مرجعية مثبتة للفيديو 🔒';
        }} else {{
          if (badgeEl) badgeEl.innerText = 'فيديو مرفق للمناقشة والتعديل 🎬';
        }}
        showToast(`تم رفع وإرفاق ${{file.name}} بنجاح! ✓`, 'success');
      }} catch (err) {{
        showToast('فشل الرفع: ' + err, 'error');
        if (badgeEl) badgeEl.innerText = 'فشل الرفع';
      }}
    }}

    function clearMediaAttachment() {{
      currentAttachedMedia = null;
      clearVideoReference();
      const prevBox = document.getElementById('chat-attachment-preview');
      if (prevBox) prevBox.classList.add('hidden');
      const f = document.getElementById('media-upload-input');
      if (f) f.value = '';
    }}

    function openAttachedInScreening() {{
      const prevImg = document.getElementById('chat-media-preview-img');
      if (prevImg && prevImg.src) {{
        switchTab('screening');
        const img = document.getElementById('screen-img-display');
        const vid = document.getElementById('screen-video-display');
        if (img) {{ img.src = prevImg.src; img.classList.remove('hidden'); }}
        if (vid) vid.classList.add('hidden');
      }}
    }}

    function analyzeCurrentScreeningMedia() {{
      switchTab('chat');
      handleDirectMessage('يا سيندي، حللي لي الكادر المعروض حالياً في شاشة العرض سينمائياً واقترحي لي تحسينات في التكوين والإضاءة.');
    }}

    function handleDiscussionChoice(choice) {{
      handleDirectMessage(choice);
    }}

    function openBridgeGuide() {{
      const m = document.getElementById('flow-bridge-guide-modal');
      if (m) m.classList.remove('hidden');
    }}

    function closeBridgeGuide() {{
      const m = document.getElementById('flow-bridge-guide-modal');
      if (m) m.classList.add('hidden');
    }}

    function syncFromFlowTab() {{
      showToast('تمت مزامنة المشاريع مع Google Flow!', 'success');
    }}

    // --- 7. ComfyUI Pod Operations ---
    async function checkComfyStatus() {{
      const dot = document.getElementById('comfy-status-dot');
      const txt = document.getElementById('comfy-status-text');
      try {{
        const res = await fetch(`${{API_BASE}}/api/comfyui/status`);
        if (res.ok) {{
          const data = await res.json();
          if (data.online) {{
            if (dot) dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
            if (txt) txt.innerText = 'متصل (RunPod / Local ComfyUI)';
          }} else {{
            if (dot) dot.className = 'w-2 h-2 rounded-full bg-amber-400';
            if (txt) txt.innerText = 'سيرفر ComfyUI مغلق (جاهز للتشغيل عند الطلب)';
          }}
        }}
      }} catch (e) {{}}
    }}

    async function launchComfyStudioPod() {{
      showToast('جاري تشغيل استوديو ComfyUI السحابي على RunPod...', 'info');
      try {{
        const res = await fetch(`${{API_BASE}}/api/comfyui/launch`, {{ method: 'POST' }});
        const d = await res.json();
        showToast(d.message || 'تم إرسال أمر التشغيل بنجاح!', 'success');
        checkComfyStatus();
        refreshWalletStatus(false);
      }} catch (e) {{
        showToast('خطأ: ' + e, 'error');
      }}
    }}

    async function terminateAllRunpodPods() {{
      if (!confirm('هل تريد حذف جميع سيرفرات RunPod لحماية رصيدك؟')) return;
      showToast('جاري إيقاف وحذف جميع السيرفرات...', 'info');
      try {{
        const res = await fetch(`${{API_BASE}}/api/comfyui/stop`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ action: 'terminate_all' }})
        }});
        const d = await res.json();
        showToast(d.message || 'تم إيقاف وحذف السيرفرات بنجاح.', 'success');
        checkComfyStatus();
        refreshWalletStatus(false);
      }} catch (e) {{
        showToast('خطأ: ' + e, 'error');
      }}
    }}

  
    function selectGridImageForEdit(url) {{
      lastRenderedComfyMedia = url;
      const img = document.getElementById('screen-img-display');
      const grid = document.getElementById('screen-grid-display');
      if (img) {{ img.src = url; img.classList.remove('hidden'); }}
      if (grid) grid.classList.add('hidden');
      showToast('تم اختيار الصورة للمعاينة والتعديل!', 'success');
    }}

    function submitVoiceDirected() {{
      handleChatSubmit(new Event('submit'));
    }}

    // --- REFERENCE IMAGE & PROMPT TARGETING LOGIC ---
    let activeReferenceImage = '';
    let currentAttachedMedia = null;

    function setAsVideoReference(dataUrl) {{
      if (!dataUrl) return;
      activeReferenceImage = dataUrl;
      lastRenderedComfyMedia = dataUrl;

      // 1. Top bar state
      const emptyBox = document.getElementById('video-ref-empty-state');
      const activeBox = document.getElementById('video-ref-active-state');
      const thumb = document.getElementById('video-ref-thumb');
      if (emptyBox) emptyBox.classList.add('hidden');
      if (activeBox) activeBox.classList.remove('hidden');
      if (thumb) thumb.src = dataUrl;

      // 2. ComfyUI Video Source
      const comfySrc = document.getElementById('comfy-video-img-source');
      if (comfySrc) comfySrc.value = dataUrl;
      const comfyThumbBox = document.getElementById('comfy-video-ref-preview-box');
      const comfyThumb = document.getElementById('comfy-video-ref-preview-thumb');
      if (comfyThumbBox) comfyThumbBox.classList.remove('hidden');
      if (comfyThumb) comfyThumb.src = dataUrl;

      // 3. Prompt badge in chat
      const refBadge = document.getElementById('active-prompt-ref-badge');
      if (refBadge) refBadge.classList.remove('hidden');

      showToast('تم تثبيت الصورة كمرجع لأدوات الفيديو بنجاح! 🔒', 'success');
    }}

    function clearVideoReference() {{
      activeReferenceImage = '';
      const emptyBox = document.getElementById('video-ref-empty-state');
      const activeBox = document.getElementById('video-ref-active-state');
      if (emptyBox) emptyBox.classList.remove('hidden');
      if (activeBox) activeBox.classList.add('hidden');

      const refBadge = document.getElementById('active-prompt-ref-badge');
      if (refBadge) refBadge.classList.add('hidden');

      const comfySrc = document.getElementById('comfy-video-img-source');
      if (comfySrc) comfySrc.value = '';
      const comfyThumbBox = document.getElementById('comfy-video-ref-preview-box');
      if (comfyThumbBox) comfyThumbBox.classList.add('hidden');

      const f = document.getElementById('video-ref-file-input');
      if (f) f.value = '';
      const cf = document.getElementById('comfy-video-file-input');
      if (cf) cf.value = '';

      const prevBox = document.getElementById('chat-attachment-preview');
      if (prevBox) prevBox.classList.add('hidden');

      showToast('تمت إزالة الصورة المرجعية.', 'info');
    }}

    function useLastRenderedAsVideoRef() {{
      if (!lastRenderedComfyMedia) {{
        showToast('لم يتم توليد أي كادر بعد لاستخدامه كمرجع. يمكنك رفع صورة من جهازك بالزر المجاور.', 'warn');
        return;
      }}
      setAsVideoReference(lastRenderedComfyMedia);
    }}

        async function handleVideoRefFileSelected(e) {{
      const file = e.target.files[0];
      if (!file) return;
      showToast('جاري رفع الكادر المرجعي إلى السيرفر...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        setAsVideoReference(data.url);
        showToast('تم رفع وتثبيت الكادر كمرجع لأدوات الفيديو بنجاح! 🔒', 'success');
      }} catch (err) {{
        showToast('فشل رفع الكادر: ' + err, 'error');
      }}
    }}

    async function handleComfyVideoFileSelected(e) {{
      const file = e.target.files[0];
      if (!file) return;
      showToast('جاري رفع كادر الفيديو إلى الاستوديو...', 'info');
      try {{
        const data = await uploadMediaFileToServer(file);
        setAsVideoReference(data.url);
        showToast('تم رفع كادر الفيديو بنجاح وجاهز للتحريك! 🎬', 'success');
      }} catch (err) {{
        showToast('فشل رفع الكادر: ' + err, 'error');
      }}
    }}

    function handleTopbarRefImage(e) {{
      handleVideoRefFileSelected(e);
    }}


    // ==========================================
    // DAILY PRICING & CLOUD RATES LOGIC
    // ==========================================
    window.DAILY_PRICING = null;

    const MODEL_COST_MAP = {{
      'Kling Motion Control (1080p)': '~$0.63 / 5s',
      'Kling 1.6 Pro Image-to-Video': '~$0.49 / 5s',
      'Kling 4 / 3.0 Pro': '~$0.49 / 5s',
      'Kling AI Standard': '~$0.28 / 5s',
      'Luma Ray 2 Image-to-Video': '$0.50 / 5s',
      'Luma Ray 2 & Dream Machine': '$0.50 / 5s',
      'Luma Ray 2 Modify': '~$1.75 / 5s',
      'Kling O1 Video-to-Video Edit': '~$0.50 / 5s',
      'Wan 2.1 (Alibaba 14B)': '~$0.03 / 5s (اقتصادي)',
      'Wan 2.1 Image-to-Video': '~$0.03 / 5s (اقتصادي)',
      'MiniMax H3 Lite': '~$0.04 / 5s',
      'MiniMax H3 Max Turbo': '~$0.08 / 5s',
      'CogVideoX-5B (THUDM)': '~$0.03 / 5s',
      'Flux 3 Max Image-to-Video': '~$0.08 / 5s'
    }};

    async function loadDailyPricing(forceRefresh = false) {{
      try {{
        const url = forceRefresh ? `${{API_BASE}}/api/pricing/refresh` : `${{API_BASE}}/api/pricing/daily`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.success && data.pricing) {{
          window.DAILY_PRICING = data.pricing;
          updatePricingUI(data.pricing);
          return data.pricing;
        }}
      }} catch (e) {{
        console.warn('Failed to load daily pricing:', e);
      }}
      return null;
    }}

    function updatePricingUI(pricing) {{
      if (!pricing) return;
      
      const datePill = document.getElementById('topbar-pricing-date-pill');
      if (datePill && pricing.date) {{
        datePill.innerText = pricing.date;
      }}

      const modalDate = document.getElementById('pricing-modal-date');
      if (modalDate && pricing.date) {{
        modalDate.innerText = pricing.date;
      }}

      const modalTime = document.getElementById('pricing-modal-time');
      if (modalTime && pricing.last_updated_formatted) {{
        modalTime.innerText = pricing.last_updated_formatted;
      }}

      const activeSelect = document.getElementById('active-video-model');
      if (activeSelect) {{
        const costVal = document.getElementById('active-model-cost-val');
        if (costVal) {{
          costVal.innerText = MODEL_COST_MAP[activeSelect.value] || '~$0.50 / 5s';
        }}
      }}

      renderPricingGrids(pricing);
      runSceneCalc();
    }}

    function renderPricingGrids(pricing) {{
      if (!pricing) return;

      const vGrid = document.getElementById('pricing-video-grid');
      if (vGrid && pricing.fal_models) {{
        const vModels = pricing.fal_models.filter(m => m.category.startsWith('video'));
        vGrid.innerHTML = vModels.map(m => `
          <div class="bg-cinema-950/80 border border-cinema-700/80 rounded-xl p-3.5 space-y-2 hover:border-amber-500/50 transition shadow">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-100 flex items-center gap-1.5 text-xs">
                ${{m.name}}
              </span>
              <span class="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded font-bold">
                ${{m.badge}}
              </span>
            </div>
            <div class="flex items-center justify-between text-[11px] bg-cinema-900/90 px-2.5 py-1.5 rounded-lg border border-cinema-800">
              <span class="text-slate-400">سعر الوحدة: <strong class="text-slate-200 font-mono">$${{m.unit_price}} / ${{m.unit}}</strong></span>
              <span class="text-amber-400 font-bold font-mono">شوت 5 ثوانٍ: ~$${{m.estimated_shot_cost}}</span>
            </div>
            <p class="text-[10px] text-slate-400 leading-relaxed">${{m.recommendation}}</p>
          </div>
        `).join('');
      }}

      const iGrid = document.getElementById('pricing-image-grid');
      if (iGrid && pricing.fal_models) {{
        const iModels = pricing.fal_models.filter(m => m.category === 'image');
        iGrid.innerHTML = iModels.map(m => `
          <div class="bg-cinema-950/80 border border-cinema-700/80 rounded-xl p-3.5 space-y-2 hover:border-purple-500/50 transition shadow">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-100 flex items-center gap-1.5 text-xs">
                ${{m.name}}
              </span>
              <span class="text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded font-bold">
                ${{m.badge}}
              </span>
            </div>
            <div class="flex items-center justify-between text-[11px] bg-cinema-900/90 px-2.5 py-1.5 rounded-lg border border-cinema-800">
              <span class="text-slate-400">السعر: <strong class="text-slate-200 font-mono">$${{m.unit_price}} / ${{m.unit}}</strong></span>
              <span class="text-purple-300 font-bold font-mono">~$${{m.estimated_shot_cost}} للكادر</span>
            </div>
            <p class="text-[10px] text-slate-400 leading-relaxed">${{m.recommendation}}</p>
          </div>
        `).join('');
      }}

      const gGrid = document.getElementById('pricing-gpus-grid');
      if (gGrid && pricing.runpod_gpus) {{
        gGrid.innerHTML = pricing.runpod_gpus.map(g => `
          <div class="bg-cinema-950/80 border border-cinema-700/80 rounded-xl p-3.5 space-y-2 hover:border-blue-500/50 transition shadow">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-100 flex items-center gap-1.5 text-xs">
                <i class="fa-solid fa-microchip text-blue-400"></i> ${{g.name}}
              </span>
              <span class="text-[9px] bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded font-mono font-bold">
                ${{g.vram}}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-[10px] bg-cinema-900/90 p-2 rounded-lg border border-cinema-800 font-mono">
              <div>سيرفر مجتمعي: <strong class="text-emerald-400">$${{g.community_per_hr || '--'}}/ساعة</strong></div>
              <div>سيرفر آمن: <strong class="text-blue-300">$${{g.on_demand_per_hr || '--'}}/ساعة</strong></div>
            </div>
            <div class="flex items-center justify-between text-[10px] text-slate-400">
              <span>الدقيقة: ~$${{g.approx_per_min}}</span>
              <span class="text-slate-300 font-bold">${{g.recommended_use}}</span>
            </div>
          </div>
        `).join('');
      }}

      const lGrid = document.getElementById('pricing-llms-grid');
      if (lGrid && pricing.llm_engines) {{
        lGrid.innerHTML = pricing.llm_engines.map(l => `
          <div class="bg-cinema-950/80 border border-cinema-700/80 rounded-xl p-3.5 space-y-2 hover:border-emerald-500/50 transition shadow">
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-100 flex items-center gap-1.5 text-xs">
                <i class="fa-solid fa-brain text-emerald-400"></i> ${{l.name}}
              </span>
              <span class="text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">
                ${{l.status}}
              </span>
            </div>
            <p class="text-[10px] text-slate-300">${{l.role}}</p>
            <div class="text-[10px] bg-cinema-900/90 p-2 rounded-lg border border-cinema-800 text-slate-400 space-y-0.5">
              <div>الإدخال: <span class="text-slate-200 font-mono">${{l.input_rate}}</span></div>
              <div>الإخراج: <span class="text-slate-200 font-mono">${{l.output_rate}}</span></div>
              <div class="text-emerald-400 font-bold pt-1">تكلفة المشهد الإخراجي: ${{l.cost_per_scene}}</div>
            </div>
          </div>
        `).join('');
      }}
    }}

    function openDailyPricingModal() {{
      const modal = document.getElementById('daily-pricing-modal');
      if (modal) modal.classList.remove('hidden');
      if (!window.DAILY_PRICING) {{
        loadDailyPricing(false);
      }} else {{
        updatePricingUI(window.DAILY_PRICING);
      }}
    }}

    function closeDailyPricingModal() {{
      const modal = document.getElementById('daily-pricing-modal');
      if (modal) modal.classList.add('hidden');
    }}

    async function refreshDailyPricingLive() {{
      const icon = document.getElementById('pricing-sync-icon');
      if (icon) icon.classList.add('fa-spin');
      showToast('جاري سحب أحدث أسعار الأدوات من السحابة...', 'info');
      try {{
        const pricing = await loadDailyPricing(true);
        if (pricing) {{
          showToast('تم تحديث أسعار الأدوات والخدمات السحابية بنجاح!', 'success');
        }} else {{
          showToast('تعذر تحديث الأسعار لحظياً، تم عرض الأسعار المحفوظة.', 'warning');
        }}
      }} catch (e) {{
        showToast('خطأ أثناء التحديث: ' + e, 'error');
      }} finally {{
        if (icon) icon.classList.remove('fa-spin');
      }}
    }}

    function switchPricingTab(tabName) {{
      const tabs = ['video', 'image', 'gpus', 'llms', 'calc'];
      tabs.forEach(t => {{
        const pane = document.getElementById(`pricing-tab-${{t}}`);
        const btn = document.getElementById(`ptab-btn-${{t}}`);
        if (pane) {{
          if (t === tabName) pane.classList.remove('hidden');
          else pane.classList.add('hidden');
        }}
        if (btn) {{
          if (t === tabName) {{
            btn.className = 'px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/50 flex items-center gap-1.5 shrink-0 transition shadow';
          }} else {{
            btn.className = 'px-3 py-1.5 rounded-lg bg-cinema-800/80 hover:bg-cinema-800 text-slate-400 hover:text-slate-200 border border-cinema-700 flex items-center gap-1.5 shrink-0 transition';
          }}
        }}
      }});
    }}

    function runSceneCalc() {{
      const vModelRate = parseFloat(document.getElementById('calc-video-model')?.value || 0.63);
      const shotsCount = parseInt(document.getElementById('calc-shots-count')?.value || 4);
      const iModelRate = parseFloat(document.getElementById('calc-image-model')?.value || 0.06);
      const imagesCount = parseInt(document.getElementById('calc-images-count')?.value || 6);

      const totalVideoCost = vModelRate * shotsCount;
      const totalImageCost = iModelRate * imagesCount;
      const totalUSD = totalVideoCost + totalImageCost;
      const totalEGP = Math.round(totalUSD * 50);

      const totalUsdEl = document.getElementById('calc-total-usd');
      const totalEgpEl = document.getElementById('calc-total-egp');
      if (totalUsdEl) totalUsdEl.innerText = `$${{totalUSD.toFixed(2)}} USD`;
      if (totalEgpEl) totalEgpEl.innerText = `(~${{totalEGP}} جنيه مصري)`;

      const rpBadge = document.getElementById('wallet-runpod-badge');
      const balText = rpBadge ? rpBadge.innerText.replace('$', '') : '13.19';
      const balNum = parseFloat(balText) || 13.19;

      const calcBalEl = document.getElementById('calc-wallet-rp');
      if (calcBalEl) calcBalEl.innerText = `$${{balNum.toFixed(2)}}`;

      const covEl = document.getElementById('calc-coverage-status');
      if (covEl) {{
        if (balNum >= totalUSD) {{
          covEl.className = 'text-emerald-400 font-bold';
          covEl.innerText = `✓ رصيدك يغطي إنتاج هذا المشهد بالكامل وزيادة (${{(balNum - totalUSD).toFixed(2)}}$ فائض)!`;
        }} else {{
          covEl.className = 'text-rose-400 font-bold';
          covEl.innerText = `⚠️ التكلفة تتجاوز رصيدك الحالي بمقدار $${{(totalUSD - balNum).toFixed(2)}}`;
        }}
      }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      loadDailyPricing(false);
    }});

</script>



  <div id="toast-root" class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 w-[min(92vw,26rem)] pointer-events-none"></div>



  <!-- MODAL: DAILY PRICING & CLOUD RATES INDEX -->
  <div id="daily-pricing-modal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5">
    <div class="bg-cinema-900 border border-cinema-gold/70 rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col shadow-2xl relative text-slate-100 overflow-hidden">
      
      <!-- Modal Header -->
      <div class="p-5 border-b border-cinema-700/80 bg-cinema-950/90 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-600 flex items-center justify-center text-cinema-950 font-black text-xl shadow-lg">
            <i class="fa-solid fa-tags"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-cinema-gold flex items-center gap-2">
              <span>مؤشر أسعار الأدوات والخدمات السحابية اليومي</span>
              <span class="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded-full font-mono font-bold">Live Daily Rates</span>
            </h3>
            <p class="text-xs text-slate-400 mt-0.5 flex items-center gap-2">
              <span>📅 <span id="pricing-modal-date" class="font-bold text-slate-300">اليوم</span></span>
              <span>•</span>
              <span>آخر تحديث: <span id="pricing-modal-time" class="font-mono text-amber-300">--:--</span></span>
              <span>•</span>
              <span class="text-slate-400">تحديث دوري لحماية الميزانية</span>
            </p>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <button type="button" onclick="refreshDailyPricingLive()" id="pricing-sync-btn" class="px-3 py-1.5 rounded-xl bg-cinema-800 hover:bg-cinema-700 border border-amber-500/40 text-amber-300 text-xs font-bold flex items-center gap-1.5 transition cursor-pointer shadow">
            <i class="fa-solid fa-arrows-rotate text-[11px]" id="pricing-sync-icon"></i>
            <span>تحديث الأسعار الآن</span>
          </button>
          <button type="button" onclick="closeDailyPricingModal()" class="w-8 h-8 rounded-xl bg-cinema-800 hover:bg-rose-900/60 text-slate-400 hover:text-white flex items-center justify-center text-sm transition border border-cinema-700">
            <i class="fa-solid fa-xmark"></i>
          </button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center gap-1.5 p-3 bg-cinema-950/60 border-b border-cinema-800 overflow-x-auto text-xs font-bold scrollbar-none">
        <button type="button" onclick="switchPricingTab('video')" id="ptab-btn-video" class="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/50 flex items-center gap-1.5 shrink-0 transition">
          <i class="fa-solid fa-video text-amber-400"></i> 🎬 محركات الفيديو والحركة
        </button>
        <button type="button" onclick="switchPricingTab('image')" id="ptab-btn-image" class="px-3 py-1.5 rounded-lg bg-cinema-800/80 hover:bg-cinema-800 text-slate-400 hover:text-slate-200 border border-cinema-700 flex items-center gap-1.5 shrink-0 transition">
          <i class="fa-solid fa-image text-purple-400"></i> 🖼️ محركات الكوادر والصور
        </button>
        <button type="button" onclick="switchPricingTab('gpus')" id="ptab-btn-gpus" class="px-3 py-1.5 rounded-lg bg-cinema-800/80 hover:bg-cinema-800 text-slate-400 hover:text-slate-200 border border-cinema-700 flex items-center gap-1.5 shrink-0 transition">
          <i class="fa-solid fa-server text-blue-400"></i> 🖥️ كروت الشاشة RunPod
        </button>
        <button type="button" onclick="switchPricingTab('llms')" id="ptab-btn-llms" class="px-3 py-1.5 rounded-lg bg-cinema-800/80 hover:bg-cinema-800 text-slate-400 hover:text-slate-200 border border-cinema-700 flex items-center gap-1.5 shrink-0 transition">
          <i class="fa-solid fa-brain text-emerald-400"></i> 🧠 عقول المخرج الذكية (LLMs)
        </button>
        <button type="button" onclick="switchPricingTab('calc')" id="ptab-btn-calc" class="px-3 py-1.5 rounded-lg bg-cinema-800/80 hover:bg-cinema-800 text-slate-400 hover:text-slate-200 border border-cinema-700 flex items-center gap-1.5 shrink-0 transition">
          <i class="fa-solid fa-calculator text-rose-400"></i> 🧮 حاسبة ميزانية المشهد
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        
        <!-- Tab 1: Video Models -->
        <div id="pricing-tab-video" class="space-y-3">
          <div class="flex items-center justify-between text-slate-400 text-[11px] pb-1">
            <span>محركات الفيديو المدعومة في السيرفر مع حساب تكلفة الشوت بدقة:</span>
            <span class="text-amber-400">الأسعار تسحب مباشرة من API السحابة</span>
          </div>
          <div id="pricing-video-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Injected dynamically via JS -->
          </div>
        </div>

        <!-- Tab 2: Image Models -->
        <div id="pricing-tab-image" class="hidden space-y-3">
          <div class="flex items-center justify-between text-slate-400 text-[11px] pb-1">
            <span>محركات تصميم الكوادر، بوسترات المشاهد ولورات الممثلين:</span>
            <span class="text-purple-400">تكلفة الصورة أو الميجا بكسل</span>
          </div>
          <div id="pricing-image-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Injected dynamically via JS -->
          </div>
        </div>

        <!-- Tab 3: RunPod GPUs -->
        <div id="pricing-tab-gpus" class="hidden space-y-3">
          <div class="flex items-center justify-between text-slate-400 text-[11px] pb-1">
            <span>سيرفرات كروت الشاشة السحابية (ComfyUI / Wan 2.1 محلياً / تدريب اللورا):</span>
            <span class="text-blue-400">أسعار فورية من RunPod GraphQL</span>
          </div>
          <div id="pricing-gpus-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Injected dynamically via JS -->
          </div>
        </div>

        <!-- Tab 4: LLMs -->
        <div id="pricing-tab-llms" class="hidden space-y-3">
          <div class="flex items-center justify-between text-slate-400 text-[11px] pb-1">
            <span>عقول السيناريو والتحليل الإخراجي:</span>
            <span class="text-emerald-400">تسعيرة الـ Tokens لكل مليون رمز</span>
          </div>
          <div id="pricing-llms-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Injected dynamically via JS -->
          </div>
        </div>

        <!-- Tab 5: Scene Budget Calculator -->
        <div id="pricing-tab-calc" class="hidden space-y-4 bg-cinema-950/80 p-5 rounded-2xl border border-cinema-700">
          <h4 class="text-sm font-bold text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-calculator text-amber-400"></i> حاسبة ميزانية المشهد السينمائي قبل الريندر
          </h4>
          <p class="text-slate-400 text-[11px]">حدد مكونات المشهد وشوف التكلفة الإجمالية بالدولار، وتأكد من كفاية رصيدك الحالي فوراً:</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label class="block text-slate-300 font-bold mb-1">اختر محرك الفيديو الأساسي:</label>
              <select id="calc-video-model" onchange="runSceneCalc()" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-slate-200 font-bold text-xs focus:border-cinema-gold">
                <option value="0.63" selected>👑 Kling Motion Control (1080p) [~$0.63 / 5s]</option>
                <option value="0.49">👑 Kling 1.6 Pro I2V [~$0.49 / 5s]</option>
                <option value="0.28">⚡ Kling 1.6 Standard [~$0.28 / 5s]</option>
                <option value="0.50">🌊 Luma Ray 2 I2V [$0.50 / 5s]</option>
                <option value="0.03">💎 Alibaba Wan 2.1 [~$0.03 / 5s - اقتصادي]</option>
              </select>
            </div>

            <div>
              <label class="block text-slate-300 font-bold mb-1">عدد شوتات الفيديو في المشهد:</label>
              <input type="number" id="calc-shots-count" value="4" min="1" max="50" onchange="runSceneCalc()" oninput="runSceneCalc()" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-amber-300 font-bold text-xs focus:border-cinema-gold font-mono">
            </div>

            <div>
              <label class="block text-slate-300 font-bold mb-1">اختر محرك الكوادر المرجعية (Concept Art):</label>
              <select id="calc-image-model" onchange="runSceneCalc()" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-slate-200 font-bold text-xs focus:border-cinema-gold">
                <option value="0.06" selected>🌟 FLUX.1 [pro] v1.1 Ultra ($0.06 / كادر)</option>
                <option value="0.025">💎 FLUX.1 [dev] ($0.025 / كادر)</option>
                <option value="0.003">⚡ FLUX.1 [schnell] ($0.003 / كادر)</option>
              </select>
            </div>

            <div>
              <label class="block text-slate-300 font-bold mb-1">عدد الكوادر الثابتة المطلوبة للمشهد:</label>
              <input type="number" id="calc-images-count" value="6" min="0" max="100" onchange="runSceneCalc()" oninput="runSceneCalc()" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-amber-300 font-bold text-xs focus:border-cinema-gold font-mono">
            </div>
          </div>

          <!-- Calculation Result Summary Banner -->
          <div class="mt-4 p-4 rounded-xl bg-gradient-to-r from-cinema-900 to-cinema-950 border border-cinema-gold/60 flex flex-wrap items-center justify-between gap-3 shadow-lg">
            <div>
              <span class="text-slate-400 block text-[11px]">التكلفة المقدرة لإنتاج المشهد بالكامل:</span>
              <span id="calc-total-usd" class="text-2xl font-black text-amber-300 font-mono">$2.88 USD</span>
              <span id="calc-total-egp" class="text-xs text-slate-400 mr-2">(~144 جنيه مصري)</span>
            </div>
            <div class="text-left text-[11px] text-slate-300 space-y-1">
              <div>🛡️ رصيدك المتاح في RunPod: <span id="calc-wallet-rp" class="font-bold text-emerald-400 font-mono">$13.19</span></div>
              <div id="calc-coverage-status" class="text-emerald-400 font-bold">✓ رصيدك يغطي إنتاج هذا المشهد بالكامل وزيادة!</div>
            </div>
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-cinema-850 bg-cinema-950/80 flex items-center justify-between text-xs text-slate-400">
        <span class="flex items-center gap-1.5">
          <i class="fa-solid fa-shield-halved text-emerald-400"></i> حماية ميزانية المخرج: لا يتم سحب سنت واحد بدون إذن مسبق
        </span>
        <button type="button" onclick="closeDailyPricingModal()" class="px-5 py-2 rounded-xl bg-cinema-800 hover:bg-cinema-700 text-slate-200 font-bold transition">
          إغلاق المؤشر
        </button>
      </div>

    </div>
  </div>

  <!-- MODAL: GOOGLE FLOW BRIDGE SETUP GUIDE -->

  <div id="bridge-guide-modal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">

    <div class="bg-cinema-900 border border-cinema-gold/60 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl relative text-slate-100">

      <button onclick="closeBridgeGuide()" class="absolute top-4 left-4 text-slate-400 hover:text-white text-lg">

        <i class="fa-solid fa-xmark"></i>

      </button>



      <div class="flex items-center gap-3 border-b border-cinema-700 pb-3">

        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-yellow-500 flex items-center justify-center text-cinema-950 font-black text-xl shadow-lg">

          <i class="fa-solid fa-puzzle-piece"></i>

        </div>

        <div>

          <h3 class="text-base font-bold text-cinema-gold">تفعيل جسر سيندي لجوجل فلو (Cindy Flow Bridge)</h3>

          <p class="text-xs text-slate-400">اربط سيندي بتبويب Google Flow المفتوح بحسابك في 10 ثوانٍ!</p>

        </div>

      </div>



      <div class="space-y-3 text-xs leading-relaxed">

        <div class="flex gap-2.5 items-start bg-cinema-800/80 p-3 rounded-xl border border-cinema-700">

          <span class="w-5 h-5 rounded-full bg-cinema-gold text-cinema-950 font-bold flex items-center justify-center text-[11px] shrink-0">1</span>

          <div>

            <strong class="text-slate-200">افتح صفحة الإضافات في متصفح كروم:</strong>

            <p class="text-slate-400 mt-0.5">افتح تبويب جديد واكتب في شريط العنوان: <code class="bg-cinema-950 px-1.5 py-0.5 rounded text-amber-300 font-mono select-all">chrome://extensions</code></p>

          </div>

        </div>



        <div class="flex gap-2.5 items-start bg-cinema-800/80 p-3 rounded-xl border border-cinema-700">

          <span class="w-5 h-5 rounded-full bg-cinema-gold text-cinema-950 font-bold flex items-center justify-center text-[11px] shrink-0">2</span>

          <div>

            <strong class="text-slate-200">فعّل وضع المطور (Developer mode):</strong>

            <p class="text-slate-400 mt-0.5">شغّل مفتاح التبديل <strong class="text-emerald-400">Developer mode</strong> الموجود في أعلى اليمين.</p>

          </div>

        </div>



        <div class="flex gap-2.5 items-start bg-cinema-800/80 p-3 rounded-xl border border-cinema-700">

          <span class="w-5 h-5 rounded-full bg-cinema-gold text-cinema-950 font-bold flex items-center justify-center text-[11px] shrink-0">3</span>

          <div>

            <strong class="text-slate-200">اضغط "Load unpacked" واختر مجلد الإضافة:</strong>

            <p class="text-slate-400 mt-0.5">اضغط على زر <strong class="text-blue-400">Load unpacked (تحميل حزمة غير مضغوطة)</strong> في أعلى اليسار، ثم اختر مجلد الإضافة:</p>

            <div class="mt-1.5 p-2 bg-cinema-950 border border-cinema-800 rounded font-mono text-[11px] text-amber-200 select-all" dir="ltr">C:\\Users\\DELL\\Desktop\\Cindy-AI-Director\\cindy-flow-bridge</div>

          </div>

        </div>

      </div>



      <div class="pt-2 flex gap-2">

        <button onclick="closeBridgeGuide()" class="flex-1 py-2.5 bg-gradient-to-r from-cinema-gold to-yellow-600 hover:opacity-90 text-cinema-950 font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg">

          <i class="fa-solid fa-check"></i>

          <span>تم تفعيل الإضافة — إغلاق</span>

        </button>

      </div>

    </div>

  </div>


  <script>

  function selectDirectComfyModel(engine) {{
    const allBtns = ['btn-engine-wan22', 'btn-engine-wan21', 'btn-engine-hunyuan', 'btn-engine-cogvideo', 'btn-engine-svd', 'btn-engine-flux', 'btn-engine-sd35', 'btn-engine-sdxl', 'btn-engine-ls', 'btn-engine-kling'];
    allBtns.forEach(id => {{
      const b = document.getElementById(id);
      if (b) {{
        b.className = 'p-2 rounded-lg bg-cinema-900 border border-cinema-700 hover:border-amber-400 text-right transition flex flex-col justify-between';
      }}
    }});

    const activeBtn = document.getElementById('btn-engine-' + (engine === 'flux_dev' ? 'flux' : (engine === 'cogvideox' ? 'cogvideo' : (engine === 'latentsync' ? 'ls' : engine))));
    if (activeBtn) {{
      activeBtn.className = 'p-2 rounded-lg bg-amber-500/25 border-2 border-amber-400 text-right transition flex flex-col justify-between shadow-lg ring-1 ring-amber-400/50';
    }}

    const videoEngines = ['wan22', 'wan21', 'hunyuan', 'cogvideox', 'svd'];
    const imageEngines = ['flux_dev', 'sd35', 'sdxl'];

    if (videoEngines.includes(engine)) {{
      switchComfySubMode('video');
      const ckptSel = document.getElementById('comfy-video-checkpoint-select');
      const btnText = document.getElementById('comfy-render-btn-text');
      const hint = document.getElementById('comfy-engine-hint');

      if (engine === 'wan22') {{
        if (ckptSel) ckptSel.value = 'Wan2.2/wan2.2_i2v_720p_14B_fp8_e4m3fn.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر المشهد الآن عبر Alibaba Wan 2.2 (720p فائق الحركية)';
        if (hint) hint.innerText = '⚡ محرك Alibaba Wan 2.2 (14B): أعلى ثبات فيزيائي وكاميرا سينمائية ثلاثية الأبعاد مع حركية ديناميكية متقدمة.';
      }} else if (engine === 'wan21') {{
        if (ckptSel) ckptSel.value = 'Wan2.1/wan2.1_i2v_720p_14B_fp8_e4m3fn.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر المشهد الآن عبر Alibaba Wan 2.1 (720p سينمائي)';
        if (hint) hint.innerText = '⚡ محرك Alibaba Wan 2.1: دقة 720p مع أعلى ثبات فيزيائي وحركة كاميرا بدون تشوه.';
      }} else if (engine === 'hunyuan') {{
        if (ckptSel) ckptSel.value = 'HunyuanVideo/hunyuan_video_720p_fp8_e4m3fn.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر المشهد الآن عبر Tencent HunyuanVideo (720p 24fps)';
        if (hint) hint.innerText = '⚡ محرك Tencent HunyuanVideo (13B): محاكاة فيزيائية واقعية للضوء والظلال وحركة الشخصيات 24fps.';
      }} else if (engine === 'cogvideox') {{
        if (ckptSel) ckptSel.value = 'CogVideoX/cogvideox_5b_i2v.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر المشهد الآن عبر THUDM CogVideoX-5B';
        if (hint) hint.innerText = '⚡ محرك THUDM CogVideoX: استقرار عالي للكاميرا وتفاصيل دقيقة في المشاهد الثابتة.';
      }} else if (engine === 'svd') {{
        if (ckptSel) ckptSel.value = 'SVD/svd_xt.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر المشهد الآن عبر Stability SVD-XT (كلاسيكي)';
        if (hint) hint.innerText = '⚡ محرك Stability AI SVD-XT: سريع وخفيف لتحريك اللقطات الكلاسيكية.';
      }}
    }} else if (imageEngines.includes(engine)) {{
      switchComfySubMode('image');
      const imgCkpt = document.getElementById('comfy-checkpoint-select');
      const btnText = document.getElementById('comfy-render-btn-text');
      if (engine === 'flux_dev') {{
        if (imgCkpt) imgCkpt.value = 'Flux/flux1-dev.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر كادر فوتوغرافي الآن عبر FLUX.1 Dev (RAW 1080p)';
      }} else if (engine === 'sd35') {{
        if (imgCkpt) imgCkpt.value = 'Stability/sd3.5_large.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر كادر فوتوغرافي الآن عبر Stability SD 3.5 Large';
      }} else if (engine === 'sdxl') {{
        if (imgCkpt) imgCkpt.value = 'SDXL/sd_xl_base_1.0_0.9vae.safetensors';
        if (btnText) btnText.innerText = '▶ ريندر كادر فوتوغرافي الآن عبر Stability SDXL Base';
      }}
    }} else if (engine === 'latentsync') {{
      switchComfySubMode('latentsync');
    }} else if (engine === 'kling') {{
      switchComfySubMode('kling');
    }}
  }}

  </script>
</body>

</html>

'''



target_html = r'C:\Users\DELL\Desktop\Cindy-AI-Director\index.html'

with open(target_html, 'w', encoding='utf-8') as f:

    f.write(html_content)



print(f"Generated parametric UI with separated dropdowns, duration and image counts ({len(html_content)} bytes)")

