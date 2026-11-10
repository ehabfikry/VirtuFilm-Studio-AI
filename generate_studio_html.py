# -*- coding: utf-8 -*-
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

memory_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\cindy_memory.json'
with open(memory_file, 'r', encoding='utf-8') as f:
    memory_data = json.load(f)

memory_json_str = json.dumps(memory_data, ensure_ascii=False)

# Read master prompts
prompts_file = r'C:\Users\DELL\Desktop\Cindy-AI-Director\master_prompts_db.json'
with open(prompts_file, 'r', encoding='utf-8') as f:
    prompts_data = json.load(f)

prompts_json_str = json.dumps(prompts_data, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CINDY AI | سيندي - مستشارة ومخرجة الذكاء الاصطناعي السينمائي</title>
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
              red: '#ff0055'
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      font-family: 'Cairo', sans-serif;
      background-color: #07090e;
      color: #e2e8f0;
      overflow-x: hidden;
    }}
    .glow-gold {{
      box-shadow: 0 0 25px rgba(230, 175, 46, 0.25);
    }}
    .glow-neon {{
      box-shadow: 0 0 25px rgba(0, 240, 255, 0.25);
    }}
    .glow-purple {{
      box-shadow: 0 0 25px rgba(157, 78, 221, 0.25);
    }}
    .glow-red {{
      box-shadow: 0 0 25px rgba(255, 0, 85, 0.25);
    }}
    .border-glow {{
      border: 1px solid rgba(230, 175, 46, 0.2);
    }}
    .glass-panel {{
      background: rgba(13, 17, 26, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
    }}
    /* Pulse mic animation */
    @keyframes pulse-ring {{
      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.7); }}
      70% {{ transform: scale(1.1); box-shadow: 0 0 0 15px rgba(255, 0, 85, 0); }}
      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }}
    }}
    .recording-pulse {{
      animation: pulse-ring 1.5s infinite cubic-bezier(0.45, 0, 0.55, 1);
      background: #ff0055 !important;
      color: white !important;
    }}
    /* Waveform visualizer */
    .wave-bar {{
      animation: wave 1.2s ease-in-out infinite alternate;
    }}
    @keyframes wave {{
      0% {{ height: 4px; }}
      100% {{ height: 28px; }}
    }}
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #07090e;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #1e2638;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #e6af2e;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col bg-cinema-900 text-slate-100">

  <!-- TOP CINEMATIC HEADER -->
  <header class="glass-panel border-b border-cinema-700/60 sticky top-0 z-50 px-4 py-3">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
      
      <!-- Brand & Status -->
      <div class="flex items-center gap-3">
        <div class="relative">
          <div class="w-11 h-11 rounded-xl bg-gradient-to-tr from-cinema-purple via-cinema-red to-cinema-gold flex items-center justify-center text-white shadow-lg shadow-cinema-purple/30">
            <i class="fa-solid fa-clapperboard text-xl"></i>
          </div>
          <span class="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-cinema-900 rounded-full animate-pulse"></span>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-black font-cinzel tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cinema-gold via-amber-200 to-yellow-500">CINDY AI</h1>
            <span class="text-xs px-2 py-0.5 rounded-full bg-cinema-purple/30 text-purple-300 font-bold border border-cinema-purple/50">سيندي</span>
          </div>
          <p class="text-xs text-slate-400 font-semibold flex items-center gap-1.5">
            <span>مستشارة ومخرجة الذكاء الاصطناعي السينمائي والتوليد التنفيذي</span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-cinema-neon"></span>
            <span class="text-cinema-neon text-[10px]" id="current-lang-indicator">Bilingual (عربي / English)</span>
          </p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="hidden md:flex items-center bg-cinema-800/80 p-1 rounded-xl border border-cinema-700">
        <button onclick="switchTab('chat')" id="tab-btn-chat" class="px-4 py-1.5 rounded-lg text-sm font-bold transition flex items-center gap-2 bg-cinema-gold text-cinema-900 shadow">
          <i class="fa-solid fa-comments"></i>
          <span>المحادثة والاستشارة</span>
        </button>
        <button onclick="switchTab('storyboard')" id="tab-btn-storyboard" class="px-4 py-1.5 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition flex items-center gap-2">
          <i class="fa-solid fa-film"></i>
          <span>مهندسة المشاهد (Storyboard)</span>
        </button>
        <button onclick="switchTab('vault')" id="tab-btn-vault" class="px-4 py-1.5 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition flex items-center gap-2">
          <i class="fa-solid fa-vault"></i>
          <span>بنك المعرفة (244 برومبت)</span>
        </button>
        <button onclick="switchTab('tools')" id="tab-btn-tools" class="px-4 py-1.5 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition flex items-center gap-2">
          <i class="fa-solid fa-terminal"></i>
          <span>التنفيذ والأدوات</span>
        </button>
        <button onclick="switchTab('memory')" id="tab-btn-memory" class="px-4 py-1.5 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition flex items-center gap-2">
          <i class="fa-solid fa-brain"></i>
          <span>الذاكرة والتعلم (<span id="rules-count-badge">5</span>)</span>
        </button>
      </div>

      <!-- Right Controls: Permissions & Voice Toggle -->
      <div class="flex items-center gap-2">
        <!-- Voice TTS Toggle -->
        <button onclick="toggleVoiceOutput()" id="tts-toggle-btn" class="px-3 py-1.5 rounded-lg bg-cinema-800 border border-cinema-700 text-xs font-bold text-slate-300 hover:text-cinema-gold transition flex items-center gap-1.5" title="تشغيل/كتم صوت سيندي">
          <i class="fa-solid fa-volume-high text-cinema-gold" id="tts-icon"></i>
          <span class="hidden sm:inline" id="tts-text">صوت سيندي: مفعل</span>
        </button>

        <!-- Permissions Badge -->
        <div class="relative">
          <button onclick="togglePermDropdown()" id="perm-badge-btn" class="px-3 py-1.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-bold transition flex items-center gap-1.5">
            <i class="fa-solid fa-shield-halved"></i>
            <span id="perm-label">إذن مسبق (Supervised)</span>
            <i class="fa-solid fa-chevron-down text-[10px]"></i>
          </button>
          
          <!-- Dropdown -->
          <div id="perm-dropdown" class="hidden absolute left-0 mt-2 w-64 glass-panel border border-cinema-700 rounded-xl shadow-2xl p-2 z-50">
            <div class="text-[11px] font-bold text-slate-400 mb-2 px-2">مستوى صلاحيات سيندي للتنفيذ:</div>
            <button onclick="setPermission('advisor')" class="w-full text-right p-2 rounded-lg hover:bg-cinema-700/50 text-xs flex items-center justify-between">
              <div>
                <div class="font-bold text-emerald-400">🟢 استشارة وتخطيط فقط</div>
                <div class="text-[10px] text-slate-400">توليد برومبتس وأفكار دون أي أوامر</div>
              </div>
            </button>
            <button onclick="setPermission('supervised')" class="w-full text-right p-2 rounded-lg hover:bg-cinema-700/50 text-xs flex items-center justify-between">
              <div>
                <div class="font-bold text-amber-400">🟡 تنفيذ بإذن مسبق (الموصى به)</div>
                <div class="text-[10px] text-slate-400">عرض الأوامر والموافقة قبل التشغيل</div>
              </div>
            </button>
            <button onclick="setPermission('autonomous')" class="w-full text-right p-2 rounded-lg hover:bg-cinema-700/50 text-xs flex items-center justify-between">
              <div>
                <div class="font-bold text-rose-400">🔴 تنفيذ فوري مباشر</div>
                <div class="text-[10px] text-slate-400">تشغيل الأدوات والتحويلات تلقائياً</div>
              </div>
            </button>
          </div>
        </div>

      </div>

    </div>

    <!-- Mobile Nav Bar -->
    <div class="flex md:hidden items-center justify-around mt-2 pt-2 border-t border-cinema-800 text-xs">
      <button onclick="switchTab('chat')" class="text-cinema-gold font-bold"><i class="fa-solid fa-comments"></i> محادثة</button>
      <button onclick="switchTab('storyboard')" class="text-slate-400"><i class="fa-solid fa-film"></i> مشاهد</button>
      <button onclick="switchTab('vault')" class="text-slate-400"><i class="fa-solid fa-vault"></i> المعرفة</button>
      <button onclick="switchTab('tools')" class="text-slate-400"><i class="fa-solid fa-terminal"></i> أدوات</button>
      <button onclick="switchTab('memory')" class="text-slate-400"><i class="fa-solid fa-brain"></i> ذاكرة</button>
    </div>
  </header>

  <!-- MAIN VIEWPORT -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-4 flex flex-col gap-4">

    <!-- ======================================================== -->
    <!-- TAB 1: CHAT & VOICE CONSULTATION WITH CINDY -->
    <!-- ======================================================== -->
    <section id="tab-chat" class="flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl overflow-hidden shadow-2xl">
      
      <!-- Cindy Avatar & Quick Model Select -->
      <div class="px-5 py-3 border-b border-cinema-700/80 bg-cinema-800/50 flex flex-wrap items-center justify-between gap-3">
        
        <div class="flex items-center gap-3">
          <div class="relative">
            <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-cinema-purple to-cinema-gold flex items-center justify-center font-bold text-cinema-900 border-2 border-cinema-gold/60">
              <i class="fa-solid fa-wand-magic-sparkles text-sm text-cinema-900"></i>
            </div>
            <span class="absolute 0 0 w-full h-full rounded-full border border-cinema-gold/40 animate-ping"></span>
          </div>
          <div>
            <div class="text-sm font-black text-slate-100 flex items-center gap-2">
              <span>سيندي متصلة ومستعدة للتوجيه والتنفيذ</span>
              <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Online & Ready</span>
            </div>
            <div class="text-[11px] text-slate-400">تحدث معها صوتياً أو كتابياً بالعربية أو الإنجليزية، وستصمم لك أفضل لقطات الفيديو.</div>
          </div>
        </div>

        <!-- Target AI Engine Selector -->
        <div class="flex items-center gap-2 text-xs">
          <label class="text-slate-400 font-bold"><i class="fa-solid fa-microchip text-cinema-gold"></i> النموذج المستهدف:</label>
          <select id="chat-model-select" class="bg-cinema-900 border border-cinema-700 rounded-lg px-2.5 py-1 text-slate-200 font-bold focus:outline-none focus:border-cinema-gold">
            <option value="Kling AI 1.5">Kling AI 1.5 / 1.0 (حركة وفيزياء)</option>
            <option value="Runway Gen-3 Alpha">Runway Gen-3 Alpha / Turbo (إخراج هوليوود)</option>
            <option value="Minimax Hailuo">Minimax Hailuo (واقعية تعابير الوجه)</option>
            <option value="Luma Dream Machine">Luma Dream Machine (حركة وانتقالات)</option>
            <option value="Wan 2.1">Wan 2.1 / Wan 2.2 (مفتوح المصدر)</option>
            <option value="OpenAI Sora / Veo 3">Sora & Veo 3 (فيزياء وتناغم)</option>
            <option value="Midjourney / FLUX">Midjourney / FLUX (إطار أول Keyframe)</option>
            <option value="Universal Cinematic">نموذج عام (لجميع المنصات)</option>
          </select>
        </div>

      </div>

      <!-- Live Waveform & Speaking Animation Bar -->
      <div id="voice-activity-bar" class="hidden px-5 py-2 bg-gradient-to-r from-cinema-purple/20 via-cinema-red/20 to-cinema-gold/20 border-b border-cinema-700 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1 h-6">
            <span class="w-1 bg-cinema-neon rounded-full wave-bar" style="animation-delay: 0.1s;"></span>
            <span class="w-1 bg-cinema-gold rounded-full wave-bar" style="animation-delay: 0.3s;"></span>
            <span class="w-1 bg-cinema-purple rounded-full wave-bar" style="animation-delay: 0.2s;"></span>
            <span class="w-1 bg-cinema-red rounded-full wave-bar" style="animation-delay: 0.4s;"></span>
            <span class="w-1 bg-emerald-400 rounded-full wave-bar" style="animation-delay: 0.15s;"></span>
          </div>
          <span class="text-xs font-bold text-slate-200" id="voice-activity-text">سيندي تستمع إليك الآن... (تحدث بكل حرية)</span>
        </div>
        <button onclick="stopVoiceRecognition()" class="text-xs px-2 py-0.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded hover:bg-rose-500/40">إيقاف الاستماع</button>
      </div>

      <!-- Messages Stream -->
      <div id="chat-messages-container" class="flex-1 p-5 overflow-y-auto space-y-4 max-h-[520px]">
        
        <!-- Welcome Cindy Message -->
        <div class="flex items-start gap-3">
          <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-cinema-purple to-cinema-gold flex items-center justify-center font-bold text-cinema-900 flex-shrink-0 shadow">
            <i class="fa-solid fa-clapperboard text-xs"></i>
          </div>
          <div class="flex-1 bg-cinema-800/90 border border-cinema-700/80 rounded-2xl rounded-tr-none p-4 shadow-lg">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-black text-cinema-gold">المخرجة سيندي | Cindy</span>
              <span class="text-[10px] text-slate-400">الآن</span>
            </div>
            <div class="text-sm text-slate-200 leading-relaxed space-y-2">
              <p>أهلاً بك يا فنان! أنا <strong class="text-cinema-gold">سيندي (Cindy)</strong>، مستشارتك ومخرجتك المتخصصة في هندسة وتنفيذ الفيديو بالذكاء الاصطناعي 🎬✨.</p>
              <p>مجهزة بكل البيانات وحزم البرومبتس الـ 244، وقواعد الإخراج السينمائي لأقوى النماذج (Kling, Runway, Luma, Wan, Hailuo, Sora, Midjourney, وغيرها). كلمني بالعربي أو بالإنجليزي، بالكتابة أو بالصوت عبر المايكروفون، وسأرد عليك صوتاً ونصاً!</p>
              <div class="pt-2 flex flex-wrap gap-2 text-xs">
                <button onclick="quickPrompt('عايز مشهد سينمائي ملحمي لمقاتل ساموراي في غابة خيزران ممطرة مع حركة كاميرا درامية')" class="px-3 py-1.5 rounded-lg bg-cinema-700/60 hover:bg-cinema-700 border border-cinema-600 text-slate-300 transition">
                  <i class="fa-solid fa-wand-magic-sparkles text-cinema-gold"></i> مشهد ساموراي ممطر (Kling/Runway)
                </button>
                <button onclick="quickPrompt('أحتاج إعلان عطر فاخر 10 ثواني بألوان النيون وانعكاسات زجاجية')" class="px-3 py-1.5 rounded-lg bg-cinema-700/60 hover:bg-cinema-700 border border-cinema-600 text-slate-300 transition">
                  <i class="fa-solid fa-sparkles text-cinema-neon"></i> إعلان عطر فاخر (Luma/Hailuo)
                </button>
                <button onclick="quickPrompt('Show me a high-speed cyberpunk car chase through neon-lit rainy Tokyo alleys with FPV drone camera')" class="px-3 py-1.5 rounded-lg bg-cinema-700/60 hover:bg-cinema-700 border border-cinema-600 text-slate-300 transition">
                  <i class="fa-solid fa-bolt text-cinema-purple"></i> Cyberpunk Chase (English)
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Chat Input Controls with Voice Mic Button -->
      <div class="p-3 bg-cinema-800/80 border-t border-cinema-700">
        
        <form onsubmit="handleChatSubmit(event)" class="flex items-center gap-2">
          
          <!-- Voice Record Button -->
          <button type="button" id="voice-record-btn" onclick="toggleVoiceRecording()" class="w-12 h-12 rounded-xl bg-cinema-700 hover:bg-cinema-600 border border-cinema-600 text-cinema-gold flex items-center justify-center transition shadow-lg group relative" title="اضغط للتحدث بصوتك مع سيندي">
            <i class="fa-solid fa-microphone text-lg group-hover:scale-110 transition"></i>
            <span class="absolute -top-8 px-2 py-0.5 bg-cinema-900 border border-cinema-700 text-[10px] text-slate-300 rounded whitespace-nowrap hidden group-hover:block">تحدث بالصوت</span>
          </button>

          <!-- Text Input Field -->
          <div class="flex-1 relative">
            <input type="text" id="chat-input" placeholder="اكتب فكرتك أو اسأل سيندي عن أي مشهد سينمائي (عربي أو English)..." class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cinema-gold pr-10">
            <button type="button" onclick="clearChatInput()" class="absolute left-3 top-3.5 text-slate-400 hover:text-slate-300 text-xs">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- Send Button -->
          <button type="submit" id="send-btn" class="px-5 py-3 rounded-xl bg-gradient-to-r from-cinema-gold to-amber-500 hover:from-amber-400 hover:to-yellow-500 text-cinema-900 font-bold text-sm flex items-center gap-2 shadow-lg shadow-amber-500/20 transition">
            <span>إرسال</span>
            <i class="fa-solid fa-paper-plane text-xs"></i>
          </button>

        </form>

        <div class="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1">
          <span>💡 نصيحة سيندي: حدد المشاعر، زاوية الكاميرا، ونوع الإضاءة لتحصل على برومبت فائق الدقة.</span>
          <span class="flex items-center gap-1"><i class="fa-solid fa-microphone-lines text-cinema-neon"></i> يدعم الإدخال الصوتي باللغتين</span>
        </div>

      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 2: MULTI-SHOT STORYBOARD ARCHITECT -->
    <!-- ======================================================== -->
    <section id="tab-storyboard" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">
      
      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-film"></i>
            <span>مهندسة المشاهد المتسلسلة (Multi-Shot Storyboard Architect)</span>
          </h2>
          <p class="text-xs text-slate-400">حولي فكرة فيلمك أو إعلانك إلى خطة لقطات متتالية مع ضمان ثبات الشخصيات (Character Consistency) وتوجيهات الكاميرا لكل لقطة.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="generateSampleStoryboard()" class="px-3 py-1.5 bg-cinema-800 hover:bg-cinema-700 border border-cinema-600 rounded-lg text-xs font-bold text-slate-300">
            <i class="fa-solid fa-lightbulb text-cinema-gold"></i> مثال عملي جاهز
          </button>
        </div>
      </div>

      <!-- Storyboard Generator Form -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        <div class="md:col-span-2 space-y-3">
          <label class="block text-xs font-bold text-slate-300">فكرة الفيلم أو الإعلان / Concept & Storyline:</label>
          <textarea id="storyboard-concept" rows="3" placeholder="مثال: إعلان تجاري لسيارة كهربائية خارقة تسير في صحراء مستقبلية ليلاً تحت سماء مرصعة بالنجوم مع عاصفة رملية نيون..." class="w-full bg-cinema-900 border border-cinema-700 rounded-xl p-3 text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cinema-gold"></textarea>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">النموذج المقترح لتوليد اللقطات:</label>
            <select id="storyboard-model" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl p-2.5 text-xs text-slate-200 font-bold focus:outline-none focus:border-cinema-gold">
              <option value="Kling AI 1.5">Kling AI 1.5 (الأفضل للفيزياء والحركة)</option>
              <option value="Runway Gen-3">Runway Gen-3 (الأفضل للتكوين والتحكم بالكاميرا)</option>
              <option value="Minimax Hailuo">Minimax Hailuo (الأفضل للدراما والوجوه)</option>
              <option value="Wan 2.1">Wan 2.1 (مفتوح المصدر)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-300 mb-1">عدد اللقطات المطلوبة:</label>
            <select id="storyboard-shots-count" class="w-full bg-cinema-900 border border-cinema-700 rounded-xl p-2.5 text-xs text-slate-200 font-bold focus:outline-none focus:border-cinema-gold">
              <option value="3">3 لقطات (إعلان قصير 10-15 ثانية)</option>
              <option value="4" selected>4 لقطات (مشهد سينمائي متكامل 20 ثانية)</option>
              <option value="6">6 لقطات (تريلر / إعلان ملحمي 30 ثانية)</option>
            </select>
          </div>
          <button onclick="buildStoryboardPlan()" class="w-full py-2.5 bg-gradient-to-r from-cinema-purple to-cinema-red hover:opacity-95 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            <span>توليد خطة الستوري بورد بذكاء سيندي</span>
          </button>
        </div>

      </div>

      <!-- Generated Shots Cards Container -->
      <div id="storyboard-results-container" class="space-y-4">
        <!-- Placeholder / Results injected via JS -->
        <div class="p-8 text-center border-2 border-dashed border-cinema-700/60 rounded-xl text-slate-400">
          <i class="fa-solid fa-clapperboard text-4xl text-cinema-700 mb-3"></i>
          <p class="text-sm font-bold text-slate-300">أدخل فكرتك واضغط "توليد خطة الستوري بورد"</p>
          <p class="text-xs text-slate-400 mt-1">ستقوم سيندي بتقسيم المشهد إلى لقطات متتالية (Establishing, Medium, Close-up, Climax) مع البرومبت الخاص بكل لقطة.</p>
        </div>
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 3: KNOWLEDGE VAULT (244 PROMPTS & GUIDES) -->
    <!-- ======================================================== -->
    <section id="tab-vault" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-4">
      
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-cinema-700/80 pb-4">
        <div>
          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-vault"></i>
            <span>بنك المعرفة السينمائية الموثق (244 برومبت احترافي)</span>
          </h2>
          <p class="text-xs text-slate-400">تصفح وابحث في المخزون الضخم الذي تستند إليه سيندي في استشاراتها، متضمناً قوالب Seedance وهوليوود ولقطات الكاميرا المتقدمة.</p>
        </div>
        <div class="flex items-center gap-2 text-xs">
          <span class="px-2.5 py-1 rounded bg-cinema-800 border border-cinema-700 text-slate-300 font-bold" id="vault-count-badge">244 برومبت متوفر</span>
        </div>
      </div>

      <!-- Search & Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex-1 min-w-[240px] relative">
          <input type="text" id="vault-search" oninput="filterVault()" placeholder="ابحث بالكلمات المفتاحية (ساموراي، سيارات، نيون، FPV، كاميرا، ليل)..." class="w-full bg-cinema-900 border border-cinema-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cinema-gold pl-8">
          <i class="fa-solid fa-magnifying-glass absolute left-3 top-3 text-slate-400 text-xs"></i>
        </div>

        <select id="vault-category-filter" onchange="filterVault()" class="bg-cinema-900 border border-cinema-700 rounded-xl px-3 py-2 text-xs text-slate-200 font-bold focus:outline-none focus:border-cinema-gold">
          <option value="all">جميع التصنيفات</option>
          <option value="seedance">حزمة Seedance 2.0 / 2.5</option>
          <option value="cases">حالات الفيديو الصينية المصورة (50 حالة)</option>
          <option value="creative">التقنيات الإبداعية (Creative Techniques)</option>
          <option value="hollywood">قوالب هوليوود والإخراج (Directorial)</option>
          <option value="ovi_wan">Wan 2.1 & OVI & Doodle</option>
        </select>
      </div>

      <!-- Prompts Grid -->
      <div id="vault-cards-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[550px] overflow-y-auto pr-1">
        <!-- Rendered by JS -->
      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 4: TOOLS & EXECUTION RUNNER -->
    <!-- ======================================================== -->
    <section id="tab-tools" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">
      
      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-terminal"></i>
            <span>مركز الصلاحيات والتنفيذ العملي (Execution & Tools Runner)</span>
          </h2>
          <p class="text-xs text-slate-400">تحكم في صلاحيات سيندي التنفيذية، وقم بتوليد وتشغيل أوامر المعالجة وتجهيز الفيديوهات ودمج اللقطات عبر FFmpeg.</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold" id="tools-perm-status">صلاحية التنفيذ: بإذن مسبق</span>
        </div>
      </div>

      <!-- Tool Modules Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Module 1: FFmpeg Lossless Video Stitcher -->
        <div class="bg-cinema-800/80 border border-cinema-700 rounded-xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-100 flex items-center gap-2">
              <i class="fa-solid fa-object-ungroup text-cinema-neon"></i>
              <span>دمج لقطات الفيديو بدون فقدان جودة (FFmpeg Concat)</span>
            </h3>
            <span class="text-[10px] bg-cinema-700 px-2 py-0.5 rounded text-slate-300">Lossless</span>
          </div>
          <p class="text-xs text-slate-400">توليد أمر الدمج الفوري لجميع لقطات الـ AI المتتالية في ملف فيديو سينمائي نهائي واحد.</p>
          <div class="space-y-2">
            <input type="text" id="concat-input-files" placeholder="مسار المجلد أو الملفات (مثال: shot1.mp4, shot2.mp4, shot3.mp4)" class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-xs text-slate-200">
            <div class="flex gap-2">
              <button onclick="generateFFmpegConcat()" class="flex-1 py-1.5 bg-cinema-neon/20 hover:bg-cinema-neon/30 text-cinema-neon border border-cinema-neon/40 font-bold rounded-lg text-xs">
                <i class="fa-solid fa-code"></i> توليد أمر الدمج
              </button>
              <button onclick="executeAction('ffmpeg-concat')" class="px-4 py-1.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold rounded-lg text-xs">
                <i class="fa-solid fa-play"></i> تشغيل
              </button>
            </div>
          </div>
          <pre id="concat-cmd-output" class="bg-cinema-900 p-2.5 rounded-lg border border-cinema-700 text-[11px] font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap select-all">ffmpeg -f concat -safe 0 -i list.txt -c copy final_movie.mp4</pre>
        </div>

        <!-- Module 2: Aspect Ratio & Crop Resizer (9:16 vs 16:9) -->
        <div class="bg-cinema-800/80 border border-cinema-700 rounded-xl p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-100 flex items-center gap-2">
              <i class="fa-solid fa-crop text-cinema-gold"></i>
              <span>تحويل أبعاد الفيديو (TikTok/Reels 9:16 أو Cinema 16:9)</span>
            </h3>
            <span class="text-[10px] bg-cinema-700 px-2 py-0.5 rounded text-slate-300">Format Reframe</span>
          </div>
          <p class="text-xs text-slate-400">إعادة ضبط أبعاد اللقطة السينمائية مع الحفاظ على تمركز العنصر أو إضافة خلفية بلور ضبابية.</p>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <button onclick="generateResizerCmd('9:16')" class="py-2 bg-cinema-700 hover:bg-cinema-600 rounded-lg font-bold text-slate-200">
              📱 تحويل إلى 9:16 (عمودي)
            </button>
            <button onclick="generateResizerCmd('16:9')" class="py-2 bg-cinema-700 hover:bg-cinema-600 rounded-lg font-bold text-slate-200">
              🖥️ تحويل إلى 16:9 (عريض)
            </button>
          </div>
          <pre id="resize-cmd-output" class="bg-cinema-900 p-2.5 rounded-lg border border-cinema-700 text-[11px] font-mono text-emerald-400 overflow-x-auto whitespace-pre-wrap select-all">ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih" -c:a copy output_9_16.mp4</pre>
        </div>

        <!-- Module 3: External API & Local LLM Connectors -->
        <div class="bg-cinema-800/80 border border-cinema-700 rounded-xl p-4 space-y-3 md:col-span-2">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-100 flex items-center gap-2">
              <i class="fa-solid fa-key text-cinema-purple"></i>
              <span>ربط المفاتيح الخارجية والذكاء الاصطناعي الإضافي (اختياري)</span>
            </h3>
            <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">يعمل بدون مفاتيح محلياً 100%</span>
          </div>
          <p class="text-xs text-slate-400">تمتلك سيندي عقلية إخراجية مدمجة تعمل محلياً وفورياً، ولكن يمكنك تزويدها بمفاتيح إضافية لربطها بنماذج التوليد المباشرة إن رغبت:</p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div>
              <label class="block text-slate-400 font-bold mb-1">Google Gemini API Key:</label>
              <input type="password" id="cfg-gemini-key" placeholder="AIzaSy..." class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-slate-200">
            </div>
            <div>
              <label class="block text-slate-400 font-bold mb-1">Groq API Key (سرعة فائقة):</label>
              <input type="password" id="cfg-groq-key" placeholder="gsk_..." class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-slate-200">
            </div>
            <div>
              <label class="block text-slate-400 font-bold mb-1">Local LLM Endpoint (Ollama / Local):</label>
              <input type="text" id="cfg-local-endpoint" value="http://localhost:11434" class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-slate-200">
            </div>
          </div>
          <div class="flex justify-end">
            <button onclick="saveApiKeys()" class="px-4 py-1.5 bg-cinema-purple/30 hover:bg-cinema-purple/50 text-purple-200 border border-cinema-purple/50 rounded-lg text-xs font-bold">
              <i class="fa-solid fa-floppy-disk"></i> حفظ الإعدادات في المتصفح
            </button>
          </div>
        </div>

      </div>

    </section>

    <!-- ======================================================== -->
    <!-- TAB 5: LEARNING & MEMORY DASHBOARD -->
    <!-- ======================================================== -->
    <section id="tab-memory" class="hidden flex-1 flex flex-col glass-panel border border-cinema-700 rounded-2xl p-6 shadow-2xl space-y-6">
      
      <div class="border-b border-cinema-700/80 pb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-black text-cinema-gold flex items-center gap-2">
            <i class="fa-solid fa-brain"></i>
            <span>سجل الذاكرة والتعلم التراكمي لسيندي (Cindy's Learning Brain)</span>
          </h2>
          <p class="text-xs text-slate-400">تتعلم سيندي من كل تفاعل وقاعدة وتطور قدراتها باستمرار. يمكنك إضافة قواعد جديدة أو تعليمها ملاحظاتك الإخراجية المفضلة.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="exportMemoryJson()" class="px-3 py-1.5 bg-cinema-800 hover:bg-cinema-700 border border-cinema-600 rounded-lg text-xs font-bold text-slate-300">
            <i class="fa-solid fa-download"></i> تصدير الذاكرة (JSON)
          </button>
        </div>
      </div>

      <!-- Add New Learning Rule Form -->
      <div class="bg-cinema-800/60 border border-cinema-700 rounded-xl p-4 space-y-3">
        <h3 class="text-xs font-black text-cinema-gold flex items-center gap-2">
          <i class="fa-solid fa-graduation-cap"></i>
          <span>علمي سيندي قاعدة جديدة (Teach Cindy a New Directorial Rule):</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label class="block text-slate-400 font-bold mb-1">النموذج / التصنيف:</label>
            <select id="new-rule-category" class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-slate-200">
              <option value="Kling AI">Kling AI</option>
              <option value="Runway Gen-3">Runway Gen-3</option>
              <option value="Minimax Hailuo">Minimax Hailuo</option>
              <option value="Luma Dream Machine">Luma Dream Machine</option>
              <option value="Wan 2.1">Wan 2.1</option>
              <option value="Camera Movement">حركات الكاميرا</option>
              <option value="Lighting & Colors">الإضاءة والألوان</option>
              <option value="General Direction">قاعدة إخراجية عامة</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-slate-400 font-bold mb-1">القاعدة أو الملاحظة المتعلمة:</label>
            <input type="text" id="new-rule-text" placeholder="مثال: في اللقطات الليلية بـ Kling، وضع كلمة 'cinematic volumetric haze' يمنع تشوه الإضاءة..." class="w-full bg-cinema-900 border border-cinema-700 rounded-lg p-2 text-slate-200">
          </div>
          <div class="flex items-end">
            <button onclick="addNewLearnedRule()" class="w-full py-2 bg-gradient-to-r from-cinema-gold to-amber-500 hover:opacity-90 text-cinema-900 font-bold rounded-lg text-xs shadow">
              <i class="fa-solid fa-plus"></i> حفظ في ذاكرة سيندي
            </button>
          </div>
        </div>
      </div>

      <!-- Active Rules List -->
      <div class="space-y-3">
        <h3 class="text-xs font-bold text-slate-300">القواعد الإخراجية المسجلة في ذاكرة سيندي حالياً:</h3>
        <div id="learned-rules-list" class="space-y-2 max-h-[380px] overflow-y-auto pr-1">
          <!-- Rendered by JS -->
        </div>
      </div>

    </section>

  </main>

  <!-- DATA INJECTION SCRIPT -->
  <script>
    // Injected Memory and Master Prompts from Python
    const CINDY_MEMORY = {memory_json_str};
    const MASTER_PROMPTS = {prompts_json_str};
  </script>

  <!-- APP ENGINE SCRIPT -->
  <script>
    // State management
    let activeTab = 'chat';
    let voiceOutputEnabled = true;
    let isRecording = false;
    let recognition = null;
    let currentPermission = CINDY_MEMORY.permissions.current_level || 'supervised';
    let learnedRules = JSON.parse(localStorage.getItem('cindy_learned_rules')) || CINDY_MEMORY.learned_rules || [];
    let chatHistory = [];

    // Initialize application
    document.addEventListener('DOMContentLoaded', () => {{
      initVoiceRecognition();
      renderLearnedRules();
      renderVaultCards(MASTER_PROMPTS);
      updateRulesBadge();
      initSpeechVoices();
      
      // Load saved permission
      const savedPerm = localStorage.getItem('cindy_permission');
      if (savedPerm) setPermission(savedPerm);

      // Load saved API keys
      document.getElementById('cfg-gemini-key').value = localStorage.getItem('cindy_gemini_key') || '';
      document.getElementById('cfg-groq-key').value = localStorage.getItem('cindy_groq_key') || '';
      document.getElementById('cfg-local-endpoint').value = localStorage.getItem('cindy_local_endpoint') || 'http://localhost:11434';
    }});

    // Tab switcher
    function switchTab(tabId) {{
      activeTab = tabId;
      const tabs = ['chat', 'storyboard', 'vault', 'tools', 'memory'];
      tabs.forEach(t => {{
        const sec = document.getElementById('tab-' + t);
        const btn = document.getElementById('tab-btn-' + t);
        if (t === tabId) {{
          sec.classList.remove('hidden');
          if (btn) {{
            btn.className = 'px-4 py-1.5 rounded-lg text-sm font-bold transition flex items-center gap-2 bg-cinema-gold text-cinema-900 shadow';
          }}
        }} else {{
          sec.classList.add('hidden');
          if (btn) {{
            btn.className = 'px-4 py-1.5 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition flex items-center gap-2';
          }}
        }}
      }});
    }}

    // Permission Manager
    function togglePermDropdown() {{
      const dd = document.getElementById('perm-dropdown');
      dd.classList.toggle('hidden');
    }}

    function setPermission(level) {{
      currentPermission = level;
      localStorage.setItem('cindy_permission', level);
      const label = document.getElementById('perm-label');
      const status = document.getElementById('tools-perm-status');
      const dd = document.getElementById('perm-dropdown');
      dd.classList.add('hidden');

      if (level === 'advisor') {{
        label.innerText = 'استشارة فقط (Advisor)';
        status.innerText = 'صلاحية التنفيذ: استشارة وتخطيط فقط';
      }} else if (level === 'supervised') {{
        label.innerText = 'إذن مسبق (Supervised)';
        status.innerText = 'صلاحية التنفيذ: بإذن مسبق (الموصى به)';
      }} else {{
        label.innerText = 'تنفيذ فوري (Autonomous)';
        status.innerText = 'صلاحية التنفيذ: تنفيذ فوري مباشر';
      }}
    }}

    // Voice Output Toggle (TTS)
    function toggleVoiceOutput() {{
      voiceOutputEnabled = !voiceOutputEnabled;
      const icon = document.getElementById('tts-icon');
      const text = document.getElementById('tts-text');
      if (voiceOutputEnabled) {{
        icon.className = 'fa-solid fa-volume-high text-cinema-gold';
        text.innerText = 'صوت سيندي: مفعل';
      }} else {{
        icon.className = 'fa-solid fa-volume-xmark text-slate-500';
        text.innerText = 'صوت سيندي: مكتوم';
        window.speechSynthesis.cancel();
      }}
    }}

    // Speech Voices loader
    let availableVoices = [];
    function initSpeechVoices() {{
      if ('speechSynthesis' in window) {{
        availableVoices = window.speechSynthesis.getVoices();
        window.speechSynthesis.onvoiceschanged = () => {{
          availableVoices = window.speechSynthesis.getVoices();
        }};
      }}
    }}

    // Cindy Natural Voice Speaker
    function speakText(text, lang = 'ar') {{
      if (!voiceOutputEnabled || !('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel(); // Stop any previous speech

      // Clean text from markdown / symbols
      const cleanText = text
        .replace(/[*#_`]/g, '')
        .replace(/https?:\/\/\S+/g, '')
        .substring(0, 300); // Speak first punchy segment

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;

      // Select voice matching language
      const isArabic = /[\u0600-\u06FF]/.test(cleanText);
      if (isArabic) {{
        utterance.lang = 'ar-SA';
        const arVoice = availableVoices.find(v => v.lang.includes('ar') || v.name.includes('Arabic') || v.name.includes('Hoda') || v.name.includes('Naayf') || v.name.includes('Salma'));
        if (arVoice) utterance.voice = arVoice;
      }} else {{
        utterance.lang = 'en-US';
        const enVoice = availableVoices.find(v => v.lang.includes('en') && (v.name.includes('Zira') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Female')));
        if (enVoice) utterance.voice = enVoice;
      }}

      window.speechSynthesis.speak(utterance);
    }}

    // Voice Recognition (Speech to Text)
    function initVoiceRecognition() {{
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {{
        console.warn('Speech Recognition not supported in this browser.');
        return;
      }}

      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'ar-EG'; // Defaults to Arabic, auto fallback

      recognition.onstart = () => {{
        isRecording = true;
        document.getElementById('voice-record-btn').classList.add('recording-pulse');
        document.getElementById('voice-activity-bar').classList.remove('hidden');
        document.getElementById('voice-activity-text').innerText = 'سيندي تستمع إليك باهتمام... (تحدث بالصوت)';
      }};

      recognition.onresult = (event) => {{
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {{
          transcript += event.results[i][0].transcript;
        }}
        document.getElementById('chat-input').value = transcript;
      }};

      recognition.onerror = (event) => {{
        console.error('Recognition error:', event.error);
        stopVoiceRecognition();
      }};

      recognition.onend = () => {{
        stopVoiceRecognition();
        const inputVal = document.getElementById('chat-input').value.trim();
        if (inputVal.length > 2) {{
          handleDirectMessage(inputVal);
        }}
      }};
    }}

    function toggleVoiceRecording() {{
      if (!recognition) {{
        alert('ميزة التعرف الصوتي تتطلب متصفح Chrome أو متصفح يدعم Web Speech API.');
        return;
      }}
      if (isRecording) {{
        recognition.stop();
      }} else {{
        // Toggle language based on user intention or default
        recognition.lang = document.getElementById('chat-input').value && /[a-zA-Z]/.test(document.getElementById('chat-input').value) ? 'en-US' : 'ar-SA';
        recognition.start();
      }}
    }}

    function stopVoiceRecognition() {{
      isRecording = false;
      if (recognition) {{
        try {{ recognition.stop(); }} catch (e) {{}}
      }}
      document.getElementById('voice-record-btn').classList.remove('recording-pulse');
      document.getElementById('voice-activity-bar').classList.add('hidden');
    }}

    // Chat Handlers
    function clearChatInput() {{
      document.getElementById('chat-input').value = '';
    }}

    function quickPrompt(text) {{
      document.getElementById('chat-input').value = text;
      handleDirectMessage(text);
    }}

    function handleChatSubmit(e) {{
      e.preventDefault();
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      handleDirectMessage(text);
    }}

    function handleDirectMessage(userMessage) {{
      const model = document.getElementById('chat-model-select').value;
      const isArabic = /[\u0600-\u06FF]/.test(userMessage);

      // Render User Message
      appendUserMessage(userMessage);

      // Generate Cindy's Cinematic Intelligence Response
      setTimeout(() => {{
        const cindyReply = generateCindyConsultation(userMessage, model, isArabic);
        appendCindyMessage(cindyReply);
        speakText(cindyReply.voiceSummary, isArabic ? 'ar' : 'en');
      }}, 500);
    }}

    function appendUserMessage(text) {{
      const container = document.getElementById('chat-messages-container');
      const div = document.createElement('div');
      div.className = 'flex items-start gap-3 justify-end';
      div.innerHTML = `
        <div class="bg-gradient-to-r from-cinema-purple/80 to-cinema-700 border border-cinema-purple/50 rounded-2xl rounded-tl-none p-3.5 max-w-xl text-slate-100 shadow-md">
          <div class="text-[10px] text-purple-200 mb-1 flex items-center justify-end gap-1">
            <span>أنت (المخرج)</span>
            <i class="fa-solid fa-user text-[9px]"></i>
          </div>
          <div class="text-sm font-semibold">${{escapeHtml(text)}}</div>
        </div>
      `;
      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    }}

    function appendCindyMessage(data) {{
      const container = document.getElementById('chat-messages-container');
      const div = document.createElement('div');
      div.className = 'flex items-start gap-3';
      
      div.innerHTML = `
        <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-cinema-purple to-cinema-gold flex items-center justify-center font-bold text-cinema-900 flex-shrink-0 shadow">
          <i class="fa-solid fa-clapperboard text-xs"></i>
        </div>
        <div class="flex-1 bg-cinema-800/90 border border-cinema-700 rounded-2xl rounded-tr-none p-4 shadow-lg space-y-3">
          
          <div class="flex items-center justify-between border-b border-cinema-700/60 pb-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-black text-cinema-gold">سيندي | Cindy</span>
              <span class="text-[10px] px-2 py-0.5 rounded bg-cinema-700 text-cinema-neon font-bold">${{escapeHtml(data.model)}}</span>
            </div>
            <button onclick="speakText('${{escapeHtml(data.voiceSummary)}}')" class="text-xs text-slate-400 hover:text-cinema-gold transition" title="إعادة تشغيل الصوت">
              <i class="fa-solid fa-volume-high"></i>
            </button>
          </div>

          <div class="text-sm text-slate-200 leading-relaxed font-semibold">
            ${{data.arabicDirectorialNote}}
          </div>

          <!-- The Engineered Prompt Block -->
          <div class="bg-cinema-900/90 border border-cinema-gold/40 rounded-xl p-3 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-cinema-gold flex items-center gap-1.5">
                <i class="fa-solid fa-code"></i> البرومبت الهندسي المولد (جاهز للنسخ):
              </span>
              <button onclick="copyToClipboard(this, \`${{data.englishPrompt}}\`)" class="px-2.5 py-1 bg-cinema-gold/20 hover:bg-cinema-gold/30 text-cinema-gold border border-cinema-gold/40 rounded text-[11px] font-bold transition flex items-center gap-1">
                <i class="fa-solid fa-copy"></i>
                <span>نسخ البرومبت</span>
              </button>
            </div>
            <div class="font-mono text-xs text-amber-200 select-all bg-cinema-950 p-2.5 rounded-lg border border-cinema-800 break-words" dir="ltr">
              ${{escapeHtml(data.englishPrompt)}}
            </div>
          </div>

          <!-- Specs Badges -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            <div class="bg-cinema-900/60 p-2 rounded-lg border border-cinema-700/60">
              <span class="text-slate-400 font-bold">حركة الكاميرا والعدسة:</span>
              <span class="text-cinema-neon block font-mono font-semibold" dir="ltr">${{escapeHtml(data.cameraSpecs)}}</span>
            </div>
            <div class="bg-cinema-900/60 p-2 rounded-lg border border-cinema-700/60">
              <span class="text-slate-400 font-bold">الإضاءة ولوحة الألوان:</span>
              <span class="text-amber-300 block font-semibold">${{escapeHtml(data.lightingSpecs)}}</span>
            </div>
          </div>

          <!-- Negative Prompt -->
          <div class="text-xs bg-rose-950/20 border border-rose-900/40 p-2.5 rounded-lg text-rose-300">
            <span class="font-bold text-rose-400 block mb-0.5">البرومبت السلبي الموصى به (Negative Prompt):</span>
            <span class="font-mono text-[11px] select-all" dir="ltr">${{escapeHtml(data.negativePrompt)}}</span>
          </div>

          <!-- Cindy Pro Tip & Action Buttons -->
          <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-cinema-700/60 text-xs">
            <span class="text-slate-400 text-[11px]">💡 ${{escapeHtml(data.cindyTip)}}</span>
            <div class="flex items-center gap-2">
              <button onclick="learnFromThisPrompt(this, '${{escapeHtml(data.model)}}', \`${{data.englishPrompt}}\`)" class="px-2 py-1 rounded bg-cinema-purple/20 hover:bg-cinema-purple/40 text-purple-300 border border-cinema-purple/40 text-[10px] font-bold">
                <i class="fa-solid fa-star"></i> ممتازة! احفظيها في الذاكرة
              </button>
            </div>
          </div>

        </div>
      `;
      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    }}

    // Cindy's Local AI Generation Logic (Grounding on Models & Prompts)
    function generateCindyConsultation(query, model, isArabic) {{
      const qLower = query.toLowerCase();

      // Determine shot style & atmosphere
      let camera = "Slow dramatic Dolly-in, 35mm anamorphic lens, shallow depth of field, 24fps";
      let lighting = "Volumetric cinematic rim lighting, deep chiaroscuro contrast, atmospheric haze";
      let subjectEn = query;
      let note = "";
      let tip = "";

      if (qLower.includes("ساموراي") || qLower.includes("samurai") || qLower.includes("معركة") || qLower.includes("sword")) {{
        camera = "Low-angle smooth tracking shot with gentle arc, 50mm T1.5 prime lens, slow motion 60fps";
        lighting = "Moody stormy rain, volumetric golden lanterns casting wet reflections on bamboo leaves";
        subjectEn = "A weary master samurai standing motionless in a torrential bamboo forest, rain dripping from his weathered hat, hand resting on the hilt of his katana, blade subtly catching moonlight";
        note = isArabic ? "صممت لك مشهد ساموراي مشحوناً بالتوتر الدرامي! ركزت على إبراز تفاصيل قطرات المطر وجمود المقاتل ليعطي تأثيراً سينمائياً بطيئاً وعميقاً." : "I crafted an emotionally intense samurai composition with deliberate low-angle tracking and high-contrast rain physics.";
        tip = "في Kling AI، حدد حركة الكاميرا بنعومة (Tracking) ولا تزد الـ Motion Index عن 5 لتفادي تشوه السيف.";
      }} else if (qLower.includes("عطر") || qLower.includes("perfume") || qLower.includes("إعلان") || qLower.includes("commercial")) {{
        camera = "Ultra-macro orbital push-in, 100mm macro cine lens, crystal-clear focus rack";
        lighting = "Luxury prism caustic reflections, soft champagne gold ambient, subtle drifting liquid droplets";
        subjectEn = "Luxury emerald glass perfume bottle floating weightlessly, liquid ripples and golden micro-particles suspended in air, hyper-detailed caustics catching light";
        note = isArabic ? "هذا برومبت إعلاني فخم جداً، استعملت تقنية الـ Macro مع الإضاءة المنكسرة لإظهار نقاء الزجاج وقطرات العطر بدقة هوليوودية." : "Commercial luxury aesthetics with prism caustics and weightless micro-droplets.";
        tip = "في Runway Gen-3، استخدم وسم [Style]: Commercial Luxury Fashion لتحصل على أنقى تدريج ألوان.";
      }} else if (qLower.includes("سيار") || qLower.includes("car") || qLower.includes("chase") || qLower.includes("مطاردة") || qLower.includes("tokyo")) {{
        camera = "High-speed low-slung chase camera, dynamic FPV drone banking around corners, anamorphic horizontal lens flare";
        lighting = "Cyberpunk neon magenta and cyan reflections on glistening wet asphalt, volumetric exhaust fumes";
        subjectEn = "Aggressive customized sports car drifting smoothly through narrow neon-lit Tokyo back-alleys at midnight, tire smoke, water splashes illuminated by pink and cyan signs";
        note = isArabic ? "لقطة مطاردة فائقة السرعة مع عدسة أنامورفيك وفلير أفقي نيون، تعطي إحساس السرعة المشوقة بدون اهتزاز غير مريح." : "High-octane night street drift with neon puddles and dynamic anamorphic lens flares.";
        tip = "في Luma أو Wan 2.1، حدد اتجاه الكاميرا (Forward tracking) لتحافظ على ثبات هيكل السيارة.";
      }} else {{
        subjectEn = isArabic ? `Cinematic high-end production: ${{query}}, master shot, 35mm anamorphic film grain, dramatic visual storytelling` : query;
        note = isArabic ? "قمت بتحويل فكرتك إلى تركيبة بصرية سينمائية متكاملة وموزونة فيزيائياً." : "Synthesized your concept into a production-grade cinematic sequence.";
        tip = "احرص دائماً على ثبات الإضاءة (Volumetric Lighting) لربط المشهد بما قبله وبعده.";
      }}

      // Format prompt specifically per model
      let formattedPrompt = "";
      if (model.includes("Runway")) {{
        formattedPrompt = `[Camera]: ${{camera}} -- [Lighting]: ${{lighting}} -- [Subject & Action]: ${{subjectEn}} -- [Aesthetic]: Cinematic 35mm film, hyper-realistic, photorealistic, 4K resolution.`;
      }} else if (model.includes("Kling")) {{
        formattedPrompt = `${{subjectEn}}, ${{camera}}, ${{lighting}}, ultra-detailed cinematic motion, realistic physics, 8k textures, masterwork, natural movement.`;
      }} else if (model.includes("Luma")) {{
        formattedPrompt = `Cinematic sequence: ${{subjectEn}}. Seamless fluid movement, ${{camera}}, ${{lighting}}, photorealistic atmosphere.`;
      }} else if (model.includes("Wan")) {{
        formattedPrompt = `${{subjectEn}}. Highly consistent visual, camera moving smoothly with ${{camera}}, ${{lighting}}, high dynamic range, crisp textures.`;
      }} else {{
        formattedPrompt = `${{subjectEn}}, ${{camera}}, ${{lighting}}, 35mm anamorphic lens, master cinematography, photorealistic, 4k.`;
      }}

      const negative = CINDY_MEMORY.user_preferences.global_negative_prompts;
      const voiceSummary = isArabic ? `${{note}} البرومبت جاهز تماماً للنسخ والتوليد في ${{model}}!` : `Scene direction ready for ${{model}}. Enjoy your cinematic production!`;

      return {{
        model: model,
        arabicDirectorialNote: note,
        englishPrompt: formattedPrompt,
        cameraSpecs: camera,
        lightingSpecs: lighting,
        negativePrompt: negative,
        cindyTip: tip,
        voiceSummary: voiceSummary
      }};
    }}

    // Multi-Shot Storyboard Plan Builder
    function buildStoryboardPlan() {{
      const concept = document.getElementById('storyboard-concept').value.trim();
      const model = document.getElementById('storyboard-model').value;
      const count = parseInt(document.getElementById('storyboard-shots-count').value);
      const container = document.getElementById('storyboard-results-container');

      if (!concept) {{
        alert('يرجى كتابة فكرة المشهد أو القصة أولاً!');
        return;
      }}

      container.innerHTML = `
        <div class="text-center py-6 text-cinema-gold">
          <i class="fa-solid fa-spinner fa-spin text-2xl mb-2"></i>
          <p class="text-xs font-bold">سيندي ترسم وتخطط تسلسل المشاهد الإخراجية والبرومبتس المتتابعة...</p>
        </div>
      `;

      setTimeout(() => {{
        const shots = generateStoryboardShots(concept, model, count);
        renderStoryboardShots(shots, model);
        speakText('تم الانتهاء من تصميم الستوري بورد المتكامل لكل لقطات المشهد!');
      }}, 600);
    }}

    function generateStoryboardShots(concept, model, count) {{
      const shotTemplates = [
        {{
          type: "اللقطة 1: التأسيس والبيئة (Wide Establishing Shot)",
          lens: "24mm Anamorphic Ultra-Wide",
          motion: "Slow Cinematic Crane Down to Horizon",
          descAr: "لقطة تأسيسية عريضة تكشف الموقع والجو العام وتبني الهيبة البصرية والغموض.",
          promptEn: `Wide establishing master shot of ${{concept}}, sweeping horizon, atmospheric haze, volumetric dawn light, 24mm anamorphic lens, epic scale, cinematic depth --ar 16:9`
        }},
        {{
          type: "اللقطة 2: الفعل والتفاعل (Medium Action Shot)",
          lens: "50mm Prime Lens T1.8",
          motion: "Smooth Steadicam Tracking alongside subject",
          descAr: "لقطة متوسطة تتابع حركة الشخصية وتفاعلها الحقيقي مع المحيط والبيئة.",
          promptEn: `Medium shot of subject in ${{concept}}, moving with purposeful momentum, dust and particles swirling, tracking camera moving parallel, 50mm cinematic lens, natural lighting --ar 16:9`
        }},
        {{
          type: "اللقطة 3: المشاعر والتفاصيل الحميمية (Intense Close-Up)",
          lens: "85mm Portrait Cine Lens",
          motion: "Subtle Micro Push-In on eyes/details",
          descAr: "لقطة قريبة مكثفة تبرز تعابير الوجه، دقات النبض، وقطرات العرق أو التفاصيل العضوية.",
          promptEn: `Intense close-up portrait of the main character from ${{concept}}, eyes reflecting the environmental light, micro-facial tension, shallow depth of field, 85mm lens, golden rim light --ar 16:9`
        }},
        {{
          type: "اللقطة 4: الذروة والحركة الحاسمة (Climax / Reveal Shot)",
          lens: "35mm Wide-Angle Low-Angle",
          motion: "Dynamic FPV Arc 180 Around Action",
          descAr: "لحظة الذروة والانفراج الحركي مع حركة كاميرا دائرية ملحمية تخطف الأنفاس.",
          promptEn: `Dynamic heroic climax shot of ${{concept}}, explosive kinetic action, 180-degree arc tracking, lens flare, dust shockwave, 35mm cinematic film grain, hyper-dramatic lighting --ar 16:9`
        }}
      ];

      return shotTemplates.slice(0, count);
    }}

    function renderStoryboardShots(shots, model) {{
      const container = document.getElementById('storyboard-results-container');
      container.innerHTML = `
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-bold text-slate-300">خطة المشاهد المخرجة (${{shots.length}} لقطات متتالية لـ ${{model}}):</span>
          <button onclick="copyAllStoryboardPrompts()" class="text-xs px-3 py-1 bg-cinema-gold/20 text-cinema-gold border border-cinema-gold/40 rounded-lg hover:bg-cinema-gold/30">
            <i class="fa-solid fa-copy"></i> نسخ جميع برومبتات اللقطات
          </button>
        </div>
      `;

      shots.forEach((s, idx) => {{
        const card = document.createElement('div');
        card.className = 'bg-cinema-800/90 border border-cinema-700 rounded-xl p-4 space-y-2 shadow-md';
        card.innerHTML = `
          <div class="flex items-center justify-between border-b border-cinema-700/60 pb-2">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-cinema-gold text-cinema-900 font-black text-xs flex items-center justify-center">${{idx + 1}}</span>
              <h4 class="text-xs font-bold text-cinema-gold">${{s.type}}</h4>
            </div>
            <span class="text-[10px] font-mono text-cinema-neon">${{s.lens}} | ${{s.motion}}</span>
          </div>
          <p class="text-xs text-slate-300">${{s.descAr}}</p>
          <div class="bg-cinema-950 p-2.5 rounded-lg border border-cinema-800 text-xs font-mono text-amber-200 select-all" dir="ltr">
            ${{escapeHtml(s.promptEn)}}
          </div>
          <div class="flex items-center justify-between pt-1 text-[11px]">
            <span class="text-slate-400">💡 نصيحة سيندي: حافظ على نفس الإضاءة لضمان التماسك البصري.</span>
            <button onclick="copyToClipboard(this, \`${{s.promptEn}}\`)" class="text-cinema-gold hover:underline font-bold">
              <i class="fa-solid fa-copy"></i> نسخ البرومبت
            </button>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function generateSampleStoryboard() {{
      document.getElementById('storyboard-concept').value = "مشهد ملحمي لمركبة فضاء أثرية يتم اكتشافها داخل كهف جليدي متجمد على كوكب فضائي مهجور";
      buildStoryboardPlan();
    }}

    function copyAllStoryboardPrompts() {{
      const blocks = document.querySelectorAll('#storyboard-results-container .font-mono');
      let combined = "";
      blocks.forEach((b, i) => {{
        combined += `// Shot ${{i + 1}}\n${{b.innerText.trim()}}\n\n`;
      }});
      if (combined) {{
        navigator.clipboard.writeText(combined);
        alert('تم نسخ جميع البرومبتات بنجاح إلى الحافظة!');
      }}
    }}

    // Vault Browser & Filter
    function renderVaultCards(items) {{
      const grid = document.getElementById('vault-cards-grid');
      grid.innerHTML = '';
      
      const slice = items.slice(0, 50); // Fast render first 50
      slice.forEach(p => {{
        const div = document.createElement('div');
        div.className = 'bg-cinema-800/80 border border-cinema-700/80 rounded-xl p-3.5 space-y-2 hover:border-cinema-gold/50 transition';
        div.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-cinema-gold">${{escapeHtml(p.title_ar || 'برومبت سينمائي')}}</span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-cinema-700 text-slate-300">${{escapeHtml(p.source_label || p.category || 'Cinematic')}}</span>
          </div>
          <p class="text-xs text-slate-400 line-clamp-2">${{escapeHtml(p.desc_ar || '')}}</p>
          <div class="bg-cinema-900 p-2 rounded text-[11px] font-mono text-amber-200 line-clamp-3 select-all" dir="ltr">
            ${{escapeHtml(p.en_prompt || '')}}
          </div>
          <div class="flex items-center justify-between pt-1 text-xs">
            <button onclick="sendVaultPromptToChat(\`${{escapeHtml(p.title_ar || '')}}\`, \`${{escapeHtml(p.en_prompt || '')}}\`)" class="text-cinema-neon hover:underline font-bold flex items-center gap-1">
              <i class="fa-solid fa-comments"></i> استشيري سيندي بهذا البرومبت
            </button>
            <button onclick="copyToClipboard(this, \`${{p.en_prompt || ''}}\`)" class="text-slate-400 hover:text-white">
              <i class="fa-solid fa-copy"></i>
            </button>
          </div>
        `;
        grid.appendChild(div);
      }});

      document.getElementById('vault-count-badge').innerText = `${{items.length}} برومبت متوفر`;
    }}

    function filterVault() {{
      const query = document.getElementById('vault-search').value.toLowerCase();
      const cat = document.getElementById('vault-category-filter').value;

      const filtered = MASTER_PROMPTS.filter(p => {{
        const matchQ = (p.title_ar && p.title_ar.toLowerCase().includes(query)) ||
                       (p.desc_ar && p.desc_ar.toLowerCase().includes(query)) ||
                       (p.en_prompt && p.en_prompt.toLowerCase().includes(query));
        let matchCat = true;
        if (cat === 'seedance') matchCat = (p.source || '').includes('seedance');
        else if (cat === 'cases') matchCat = (p.source || '').includes('awesome_video') || (p.source || '').includes('case');
        else if (cat === 'creative') matchCat = (p.source || '').includes('creative');
        else if (cat === 'hollywood') matchCat = (p.source || '').includes('hollywood') || (p.category || '').includes('Director');
        else if (cat === 'ovi_wan') matchCat = (p.source || '').includes('ovi') || (p.source || '').includes('wan');
        return matchQ && matchCat;
      }});

      renderVaultCards(filtered);
    }}

    function sendVaultPromptToChat(title, prompt) {{
      switchTab('chat');
      document.getElementById('chat-input').value = `عايزك تطوري لي هذا البرومبت السينمائي وتحسني حركته: "${{title}}"\n${{prompt}}`;
      handleDirectMessage(document.getElementById('chat-input').value);
    }}

    // Tools Generator
    function generateFFmpegConcat() {{
      const input = document.getElementById('concat-input-files').value.trim() || 'shot1.mp4, shot2.mp4, shot3.mp4';
      const files = input.split(',').map(s => s.trim()).filter(s => s);
      let listContent = files.map(f => `file '${{f}}'`).join('\\n');
      const cmd = `# 1. أنشئ ملف list.txt وضع بداخله:\\n${{listContent}}\\n\\n# 2. شغل الأمر التالي للدمج الفوري بدون فقدان جودة:\\nffmpeg -f concat -safe 0 -i list.txt -c copy master_cinematic_cut.mp4`;
      document.getElementById('concat-cmd-output').innerText = cmd;
    }}

    function generateResizerCmd(ratio) {{
      if (ratio === '9:16') {{
        document.getElementById('resize-cmd-output').innerText = `ffmpeg -i input_16_9.mp4 -vf "crop=ih*9/16:ih:(iw-ow)/2:0" -c:a copy reel_output_9_16.mp4`;
      }} else {{
        document.getElementById('resize-cmd-output').innerText = `ffmpeg -i input_vertical.mp4 -vf "pad=ih*16/9:ih:(ow-iw)/2:0" -c:a copy widescreen_output_16_9.mp4`;
      }}
    }}

    function executeAction(actionType) {{
      if (currentPermission === 'advisor') {{
        alert('أنت حالياً في وضع "الاستشارة فقط". قم بتغيير الصلاحية إلى "تنفيذ بإذن مسبق" أو "تنفيذ فوري" من الأعلى لتفعيل التشغيل!');
        return;
      }}
      if (currentPermission === 'supervised') {{
        const ok = confirm(`[موافقة المخرج مطلوبة]\\nهل توافق على تشغيل أمر ${{actionType}} على جهازك الآن؟`);
        if (!ok) return;
      }}
      alert(`تم إرسال الأمر [${{actionType}}] إلى محرك التنفيذ بنجاح!`);
    }}

    function saveApiKeys() {{
      localStorage.setItem('cindy_gemini_key', document.getElementById('cfg-gemini-key').value);
      localStorage.setItem('cindy_groq_key', document.getElementById('cfg-groq-key').value);
      localStorage.setItem('cindy_local_endpoint', document.getElementById('cfg-local-endpoint').value);
      alert('تم حفظ الإعدادات والمفاتيح في المتصفح بأمان!');
    }}

    // Memory & Learning
    function renderLearnedRules() {{
      const list = document.getElementById('learned-rules-list');
      list.innerHTML = '';

      learnedRules.forEach((r, idx) => {{
        const item = document.createElement('div');
        item.className = 'bg-cinema-800/80 border border-cinema-700 rounded-xl p-3 flex items-start justify-between gap-3 text-xs';
        item.innerHTML = `
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded bg-cinema-purple/30 text-purple-300 font-bold text-[10px]">${{escapeHtml(r.category)}}</span>
              <span class="text-slate-400 text-[10px]">${{escapeHtml(r.date_added || '2026')}}</span>
            </div>
            <p class="text-slate-200 font-semibold">${{escapeHtml(r.rule)}}</p>
          </div>
          <button onclick="deleteLearnedRule(${{idx}})" class="text-rose-400 hover:text-rose-300 p-1" title="حذف القاعدة">
            <i class="fa-solid fa-trash-can text-xs"></i>
          </button>
        `;
        list.appendChild(item);
      }});

      updateRulesBadge();
    }}

    function addNewLearnedRule() {{
      const cat = document.getElementById('new-rule-category').value;
      const text = document.getElementById('new-rule-text').value.trim();
      if (!text) {{
        alert('يرجى كتابة نص القاعدة أولاً!');
        return;
      }}

      const newRule = {{
        id: "LR-" + String(learnedRules.length + 1).padStart(3, '0'),
        category: cat,
        rule: text,
        date_added: new Date().toISOString().split('T')[0],
        source: "User Taught"
      }};

      learnedRules.unshift(newRule);
      localStorage.setItem('cindy_learned_rules', JSON.stringify(learnedRules));
      document.getElementById('new-rule-text').value = '';
      renderLearnedRules();
      speakText('تم حفظ القاعدة الإخراجية الجديدة في ذاكرتي التراكمية بنجاح!');
    }}

    function learnFromThisPrompt(btn, model, prompt) {{
      const newRule = {{
        id: "LR-" + String(learnedRules.length + 1).padStart(3, '0'),
        category: model,
        rule: `برومبت ناجح ومفضل للمخرج: "${{prompt.substring(0, 120)}}..."`,
        date_added: new Date().toISOString().split('T')[0],
        source: "Successful Generation Feedback"
      }};

      learnedRules.unshift(newRule);
      localStorage.setItem('cindy_learned_rules', JSON.stringify(learnedRules));
      renderLearnedRules();
      btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> تم الحفظ في الذاكرة!`;
      btn.disabled = true;
      speakText('شكراً لملاحظتك! سجلت هذا النمط في ذاكرتي وسأعتمده في مشروعاتك القادمة.');
    }}

    function deleteLearnedRule(idx) {{
      if (confirm('هل تريد حذف هذه القاعدة من ذاكرة سيندي؟')) {{
        learnedRules.splice(idx, 1);
        localStorage.setItem('cindy_learned_rules', JSON.stringify(learnedRules));
        renderLearnedRules();
      }}
    }}

    function updateRulesBadge() {{
      const badge = document.getElementById('rules-count-badge');
      if (badge) badge.innerText = learnedRules.length;
    }}

    function exportMemoryJson() {{
      const exportData = {{
        ...CINDY_MEMORY,
        learned_rules: learnedRules,
        exported_at: new Date().toISOString()
      }};
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: 'application/json' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cindy_memory_updated.json';
      a.click();
    }}

    // Utilities
    function copyToClipboard(btn, text) {{
      navigator.clipboard.writeText(text).then(() => {{
        const orig = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> تم النسخ`;
        setTimeout(() => {{ btn.innerHTML = orig; }}, 1800);
      }}).catch(err => {{
        alert('فشل النسخ: ' + err);
      }});
    }}

    function escapeHtml(str) {{
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}
  </script>

</body>
</html>
'''

target_html = r'C:\Users\DELL\Desktop\Cindy-AI-Director\index.html'
with open(target_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated Cindy Director Studio index.html successfully ({len(html_content)} bytes)")
