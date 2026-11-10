# Translation dictionary for metadata badges and recommendations
BADGE_TRANSLATIONS = {
    'الأرخص إطلاقاً (سنتات)': {'en': 'Lowest Cost (Cents)', 'fr': 'Le Plus Économique', 'es': 'El Más Económico'},
    'الأرخص إطلاقاً': {'en': 'Lowest Cost', 'fr': 'Le Plus Économique', 'es': 'El Más Económico'},
    'اقتصادي سريع': {'en': 'Budget Fast', 'fr': 'Rapide & Éco', 'es': 'Rápido y Económico'},
    'حركية وفيزياء عالية': {'en': 'High Motion & Physics', 'fr': 'Haute Dynamique & Physique', 'es': 'Alta Dinámica y Física'},
    'توليد درافت سريع': {'en': 'Fast Draft Generation', 'fr': 'Génération Draft Rapide', 'es': 'Generación Rápida Draft'},
    'فيزياء 13B عالية': {'en': 'High Physics 13B', 'fr': 'Physique 13B Élevée', 'es': 'Física 13B Alta'},
    'لقطات سينمائية سلسة': {'en': 'Smooth Cinematic Shots', 'fr': 'Prises Cinématiques Fluides', 'es': 'Tomas Cinemáticas Suaves'},
    'أعلى جودة + قفل': {'en': 'Top Quality + LoRA', 'fr': 'Top Qualité + LoRA', 'es': 'Máxima Calidad + LoRA'},
    'قفل ملامح بالـ LoRA': {'en': 'LoRA Likeness Lock', 'fr': 'Verrouillage LoRA', 'es': 'Bloqueo LoRA'},
    'تحكم مداري ثلاثي الأبعاد': {'en': '3D Orbit Control', 'fr': 'Contrôle Orbital 3D', 'es': 'Control Orbital 3D'},
    'توليد طويل + صور متعددة': {'en': 'Long Render + Multi-Ref', 'fr': 'Rendu Long + Multi-Réf', 'es': 'Render Largo + Multi-Ref'},
    'توليد سينمائي هوليوودي': {'en': 'Hollywood Cinematic Render', 'fr': 'Rendu Cinéma Hollywood', 'es': 'Render Cinemático Hollywood'},
    'الأعلى احترافية عالمياً': {'en': 'World Standard Pro', 'fr': 'Standard Pro Mondial', 'es': 'Estándar Pro Mundial'},
    'تتبع حركة احترافي 1080p': {'en': 'Pro Motion Control 1080p', 'fr': 'Contrôle Mouvement 1080p', 'es': 'Control Movimiento 1080p'},
    'تعديل وإعادة تلوين الفيديو': {'en': 'Video Restyle & Grade', 'fr': 'Restylage Vidéo & Étallonage', 'es': 'Restilizado y Color de Video'},
    'حركة ناعمة وانفعالات': {'en': 'Smooth Motion & Acting', 'fr': 'Mouvement Fluide & Jeu', 'es': 'Movimiento Fluido y Expresión'},
    'تعديل لقطات الفيديو بالـ AI': {'en': 'AI Video Shot Editing', 'fr': 'Édition Vidéo par IA', 'es': 'Edición de Video por IA'},
    'ترقية 4K سينمائية': {'en': '4K Cinematic Upscale', 'fr': 'Upscale Cinématique 4K', 'es': 'Escalado Cinemático 4K'},
    'تزامن شفاه استوديو': {'en': 'Studio Lipsync', 'fr': 'Lipsync Studio', 'es': 'Lipsync de Estudio'},
    'دوبلاج صوتي اقتصادي': {'en': 'Budget Voice Dub', 'fr': 'Doublage Économique', 'es': 'Doblaje Económico'},
    'سريع وشبه مجاني': {'en': 'Ultra Fast & Cheap', 'fr': 'Ultra Rapide & Pas Cher', 'es': 'Ultra Rápido y Económico'},
    'فوتوغرافي سريع': {'en': 'Fast Photo Keyframe', 'fr': 'Plan Clé Photo Rapide', 'es': 'Cuadro Clave Rápido'},
    'جودة 2K Pro': {'en': '2K Pro Quality', 'fr': 'Qualité 2K Pro', 'es': 'Calidad 2K Pro'},
    'متوازن ويدعم LoRA': {'en': 'Balanced + LoRA Support', 'fr': 'Équilibré + Support LoRA', 'es': 'Equilibrado + Soporte LoRA'},
    'تعديل كادر سريع بالـ LoRA': {'en': 'Fast LoRA Frame Edit', 'fr': 'Édition Rapide par LoRA', 'es': 'Edición Rápida con LoRA'},
    'قفل ملامح متعدد': {'en': 'Multi-Identity Lock', 'fr': 'Verrouillage Multi-Identités', 'es': 'Bloqueo Multi-Identidad'},
    'تعديل كادر ذكي': {'en': 'Smart Frame Inpainting', 'fr': 'Inpainting Intelligent', 'es': 'Edición Inteligente de Cuadros'},
    'تصميم وفيكتور': {'en': 'Design & Posters', 'fr': 'Design & Affiches', 'es': 'Diseño y Pósters'},
    'تايبوجرافي وبوسترات': {'en': 'Typography & Posters', 'fr': 'Typographie & Affiches', 'es': 'Tipografía y Pósters'},
    'أعلى دقة تفاصيل فوتوغرافية': {'en': 'Peak Photographic Detail', 'fr': 'Détail Photo Maximal', 'es': 'Máximo Detalle Fotográfico'}
}

RECOMMENDATION_TRANSLATIONS = {
    'الأرخص عالمياً (~$0.03 للشوت) وجودة سينمائية مذهلة بفيزياء طبيعية': {
        'en': 'Lowest cost worldwide (~$0.03/shot) with stunning cinematic quality and realistic physics.',
        'fr': 'Le plus économique au monde (~0.03$/plan) avec une physique réaliste remarquable.',
        'es': 'El más económico del mundo (~$0.03/toma) con calidad cinematográfica y física realista.'
    },
    'تحريك كوادر الممثلين بأقل تكلفة ممكنة مع نتائج طبيعية وحركة كاميرا سلسة': {
        'en': 'Animate actor keyframes at minimal cost with organic results and smooth camera moves.',
        'fr': 'Animez les plans clés des acteurs au coût minimal avec des mouvements fluides.',
        'es': 'Anime cuadros de actores al menor costo con movimientos suaves de cámara.'
    },
    'حركة ممثلين سريعة وواقعية بـ 4 سنتات فقط للشوت الثابت 6 ثوانٍ': {
        'en': 'Fast and lifelike character motion for just 4 cents on a fixed 6-second shot.',
        'fr': 'Mouvement de personnage rapide et réaliste pour seulement 4 cents sur un plan fixe de 6s.',
        'es': 'Movimiento realista de personajes por solo 4 centavos en toma fija de 6s.'
    },
    'نسخة محسنة بحركية وفيزياء أعلى وتفاصيل إضاءة أدق': {
        'en': 'Enhanced version with higher motion dynamics, refined physics, and precise cinematic lighting.',
        'fr': 'Version améliorée avec dynamique accrue, physique raffinée et éclairage précis.',
        'es': 'Versión mejorada con mayor dinámica, física refinada e iluminación precisa.'
    },
    'مسودة سريعة جداً للمشاهد مع إمكانية دمج لورا الممثل لتجربة التتابع': {
        'en': 'Ultra-fast draft pass for sequences with actor LoRA integration to test rhythm.',
        'fr': 'Passe de prévisualisation ultra-rapide avec intégration LoRA pour tester le rythme.',
        'es': 'Pase ultra rápido para secuencias con integración de LoRA para probar ritmo.'
    },
    'محرك مفتوح المصدر قوي في فهم الحركة المعقدة والإضاءة الدرامية': {
        'en': 'Powerful open-source engine with robust comprehension of complex action and dramatic lighting.',
        'fr': 'Moteur open-source puissant pour les actions complexes et l\'éclairage dramatique.',
        'es': 'Potente motor open source para comprender acción compleja e iluminación dramática.'
    },
    'حركات كاميرا انسيابية وسينمائية ممتازة للشوتات الإعلانية والدرامية': {
        'en': 'Fluid cinematic camera choreography ideal for commercials and dramatic scenes.',
        'fr': 'Mouvements de caméra fluides idéaux pour les publicités et scènes dramatiques.',
        'es': 'Movimientos suaves de cámara ideales para comerciales y drama.'
    },
    'المعيار الذهبي الهوليوودي للإنتاج السينمائي مع قفل وجه وهوية الممثل بدقة 22B': {
        'en': 'Hollywood gold standard for cinematic production with locked character identity via 22B architecture.',
        'fr': 'Le standard hollywoodien pour préserver l\'identité des acteurs grâce au modèle 22B.',
        'es': 'Estándar de Hollywood para producción cinematográfica con identidad fija gracias a 22B.'
    },
    'ثبات ملامح الوجه وتعبيرات الممثل الدرامية مع تحريك كادر البداية': {
        'en': 'Stable facial likeness and dramatic acting expressions driven from the starting keyframe.',
        'fr': 'Fidélité des expressions dramatiques de l\'acteur à partir de l\'image de départ.',
        'es': 'Fidelidad facial y expresiones dramáticas de actuación a partir del cuadro inicial.'
    },
    'تحكم كامل في مسار الكاميرا (Pan / Tilt / Zoom / Orbit) بزوايا سينمائية محددة': {
        'en': 'Full orbital camera path control (Pan / Tilt / Zoom / Orbit) with director-defined angles.',
        'fr': 'Contrôle complet de la caméra (Pan / Tilt / Zoom / Orbit) selon des axes précis.',
        'es': 'Control total de la trayectoria de cámara (Pan / Tilt / Zoom / Orbit).'
    },
    'توليد مشاهد طويلة حتى 30 ثانية مع دعم صور متعددة لنفس المشهد بزوايا مختلفة': {
        'en': 'Generates continuous shots up to 30 seconds with multi-angle reference image support.',
        'fr': 'Génère des séquences continues jusqu\'à 30s avec références multi-angles.',
        'es': 'Genera tomas continuas de hasta 30s con soporte multiángulo de referencia.'
    },
    'محرك Luma الشهير لإنتاج حركة سينمائية غنية وانتقالات إخراجية عميقة': {
        'en': 'Famous Luma engine for rich cinematic motion and deep directorial transitions.',
        'fr': 'Moteur Luma réputé pour des mouvements riches et des transitions cinématographiques.',
        'es': 'Reconocido motor Luma para movimientos ricos y transiciones cinematográficas.'
    },
    'أعلى جودة إخراجية لتوليد مشاهد سينمائية من كادر البداية والنهاية بدقة Full HD': {
        'en': 'Peak directorial quality generating cinematic sequences from start/end keyframes in Full HD.',
        'fr': 'Qualité maximale pour générer des séquences cinématiques de début/fin en Full HD.',
        'es': 'Máxima calidad cinematográfica generando secuencias entre cuadros inicial y final en Full HD.'
    },
    'نقل حركة الممثل أو الكاميرا بدقة 100% من فيديو مرجعي مع تطبيقها على الشخصية': {
        'en': 'Transfers 100% exact actor or camera motion from a reference video onto your character.',
        'fr': 'Transfère fidèlement les mouvements d\'une vidéo de référence sur votre personnage.',
        'es': 'Transfiere con precisión los movimientos de un video de referencia a su personaje.'
    },
    'تعديل أي مشهد فيديو بإضافة عناصر، تغيير ملابس، أو تعديل الجو العام والألوان': {
        'en': 'Restyles any video clip: adds objects, alters wardrobe, and changes atmosphere/color palette.',
        'fr': 'Modifie n\'importe quelle prise: ajoute des objets, change les costumes et l\'ambiance.',
        'es': 'Modifica cualquier toma: agrega elementos, cambia vestuario y ajusta la atmósfera.'
    },
    'محرك Luma Ray-2 لتوليد حركة سينمائية نقية من الأوامر النصية المباشرة': {
        'en': 'Luma Ray-2 engine generating pristine cinematic movement straight from text prompts.',
        'fr': 'Moteur Luma Ray-2 produisant un mouvement cinématographique pur à partir du texte.',
        'es': 'Motor Luma Ray-2 que genera movimiento cinematográfico puro desde texto.'
    },
    'تعديل وإعادة إخراج مقاطع فيديو موجودة وتوجيه حركتها بأوامر ذكية': {
        'en': 'Direct and re-choreograph existing video clips with precise AI motion prompts.',
        'fr': 'Réalisez et rééditez des prises existantes avec des directives précises.',
        'es': 'Dirija y reedite tomas existentes con indicaciones precisas.'
    },
    'رفع دقة الفيديو وإزالة التشويش السينمائي للحصول على جودة 4K جاهزة للعرض': {
        'en': 'Upscales footage and refines cinematic grain for theater-ready 4K screening output.',
        'fr': 'Améliore la résolution et affine le grain pour une projection 4K en salle.',
        'es': 'Escala metraje y refina grano para proyección cinematográfica en 4K.'
    },
    'تزامن دقيق جداً لحركة الشفاه مع الأداء الصوتي بجودة بث استوديو': {
        'en': 'Broadcast-grade lip synchronization aligned to vocal performance with precision.',
        'fr': 'Synchronisation labiale de qualité studio alignée sur la performance vocale.',
        'es': 'Sincronización labial de calidad estudio alineada a la interpretación vocal.'
    },
    'دوبلاج صوتي اقتصادي وفوري لمقاطع الفيديو التمثيلية': {
        'en': 'Instant and budget-friendly voice dubbing for actor performance clips.',
        'fr': 'Doublage vocal instantané et économique pour les extraits d\'acteurs.',
        'es': 'Doblaje vocal instantáneo y económico para clips de actuación.'
    },
    'توليد فوري للستوري بورد وتجربة الإضاءة (0.3 سنت فقط للكادر)': {
        'en': 'Instant storyboard generation and lighting previews (only 0.3 cents per frame).',
        'fr': 'Génération instantanée de storyboard et tests d\'éclairage (0.3 cent par image).',
        'es': 'Generación instantánea de storyboard y pruebas de iluminación (0.3 centavos por cuadro).'
    },
    'فوتوغرافي سريع وعالي النقاء لكوادر الممثلين بنصف سنت': {
        'en': 'Fast, high-fidelity photographic actor keyframes for only half a cent.',
        'fr': 'Plans clés photographiques nets et rapides pour un demi-cent.',
        'es': 'Cuadros clave fotográficos rápidos y nítidos por medio centavo.'
    },
    'دقة 2K سينمائية متوازنة واحترافية للكوادر والمراجع': {
        'en': 'Balanced 2K cinema resolution for concept references and hero frames.',
        'fr': 'Résolution cinéma 2K équilibrée pour les références et plans principaux.',
        'es': 'Resolución 2K equilibrada para referencias conceptuales y cuadros clave.'
    },
    'الموديل المعتمد لدمج لورات الممثلين وتوليد الشخصيات المتطابقة بدقة 1080p': {
        'en': 'Certified model for actor LoRA likeness and generating consistent 1080p characters.',
        'fr': 'Modèle certifié pour intégrer les LoRA d\'acteurs et générer des personnages fidèles en 1080p.',
        'es': 'Modelo certificado para LoRA de actores y generar personajes consistentes en 1080p.'
    },
    'تعديل الإضاءة والملابس والبيئة مع الحفاظ الكامل على ملامح الممثل بواسطة LoRA': {
        'en': 'Alter lighting, wardrobe, and environment while preserving actor features via LoRA.',
        'fr': 'Modifie éclairage, garde-robe et environnement tout en préservant l\'identité par LoRA.',
        'es': 'Ajuste iluminación, vestuario y entorno preservando la identidad del actor con LoRA.'
    },
    'توليد كوادر سينمائية للشخصيات مع تثبيت الهوية بالـ LoRA بدقة متناهية': {
        'en': 'Generate cinematic character frames with precise identity preservation via LoRA.',
        'fr': 'Générez des cadres cinématiques en verrouillant l\'identité grâce au LoRA.',
        'es': 'Genere cuadros cinematográficos con bloqueo exacto de identidad mediante LoRA.'
    },
    'تعديل أجزاء محددة من الصورة بالأوامر النصية مع الحفاظ على باقي الكادر': {
        'en': 'Edit targeted frame regions via text prompts while keeping the rest untouched.',
        'fr': 'Modifiez des zones ciblées par commandes textuelles en conservant le reste.',
        'es': 'Edite regiones específicas mediante texto conservando el resto del cuadro.'
    },
    'تصاميم فنية مميزة وضبط كامل للألوان والبوسترات': {
        'en': 'Distinctive visual aesthetics with comprehensive palette and poster design controls.',
        'fr': 'Esthétique visuelle distinctive avec contrôle complet des palettes et affiches.',
        'es': 'Estética visual distintiva con control total de color y diseño de pósters.'
    },
    'أقوى محرك للتايبوجرافي والبوسترات وتصميم لوحات الأفلام والخطوط الدقيقة': {
        'en': 'Industry-leading engine for typography, movie title cards, and sharp lettering.',
        'fr': 'Moteur de référence pour la typographie, les affiches de films et lettrages nets.',
        'es': 'Motor líder para tipografía, carteles de películas y rotulación nítida.'
    },
    'الخيار الأول للكوادر الفائقة الدقة للسينما والبوسترات الرسمية بدقة 4K Raw': {
        'en': 'Top choice for ultra-high-definition film stills and official 4K Raw movie posters.',
        'fr': 'Premier choix pour les plans cinéma ultra-HD et les affiches officielles en 4K Raw.',
        'es': 'Primera elección para planos cinematográficos ultra-HD y pósters oficiales en 4K Raw.'
    }
}
