/**
 * CropCare AI — Translation Strings
 * All UI text in English and Tamil
 */

const TRANSLATIONS = {
  en: {
    // Nav
    nav_home: 'Home', nav_community: 'Community', nav_dashboard: 'Dashboard', nav_history: 'History',
    nav_about: 'About', nav_login: 'Login', nav_signup: 'Sign Up',

    // Hero
    hero_badge: 'AI-Powered Plant Analysis',
    hero_title: 'Detect Crop Disease Instantly with AI',
    hero_subtitle: 'Upload a leaf photo. Our deep-learning model identifies the disease and gives you actionable recommendations in seconds.',
    stat_classes: 'Disease Classes', stat_images: 'Training Images', stat_crops: 'Crop Types',
    demo_mode_notice: '⚠ Demo Mode — Train the model first for real predictions.',

    // Upload
    upload_title: 'Drop your leaf image here',
    upload_subtitle: 'or click to browse — JPG, PNG (max 5 MB)',
    or_divider: 'or',
    btn_camera: 'Take Photo', btn_capture: 'Capture', btn_cancel: 'Cancel',
    btn_detect: 'Detect Disease',

    // Sections
    crops_title: 'Supported Crops', crops_subtitle: 'Trained on the PlantVillage dataset across 14 crop species',
    how_title: 'How It Works',
    step1_title: 'Upload Leaf', step1_desc: 'Take a clear close-up photo of the affected leaf and upload it.',
    step2_title: 'AI Analysis', step2_desc: 'Our MobileNetV2 deep-learning model analyzes the image instantly.',
    step3_title: 'Get Results', step3_desc: 'Receive disease name, confidence, symptoms, and smart recommendations.',

    // Result
    result_title: 'Disease Detection Result',
    result_crop: 'Crop', result_disease: 'Disease', result_confidence: 'Confidence',
    tab_original: 'Original', tab_gradcam: 'AI Focus (Grad-CAM)',
    gradcam_note: 'Red/warm regions show where the AI focused its attention.',
    rec_symptoms: 'Symptoms', rec_prevention: 'Prevention',
    rec_management: 'Management', rec_monitoring: 'Monitoring',
    no_data: 'No data available.',
    chemical_disclaimer: 'Always follow locally approved pesticide labels and consult an agricultural extension officer before applying any chemical treatment.',
    healthy_msg: 'Great news! Your crop appears healthy. Continue regular monitoring and good agricultural practices.',
    btn_scan_another: 'Scan Another Leaf', btn_history: 'View History', btn_print: 'Print',

    // Disease Report
    report_title: 'Disease Report',
    healthy_report_title: 'Crop Health Report',
    healthy_observations: 'Health Observations',
    healthy_care: 'Maintenance & Preventive Care',
    steps_title: 'How to Remove This Disease',
    healthy_steps_title: '6 Steps for Healthy Crop Maintenance',
    steps_subtitle: 'Follow these 6 steps to treat and eliminate the disease from your crop',
    healthy_steps_subtitle: 'Follow these 6 steps to maintain optimal growth and prevent infections',
    step_label_1: 'Isolate & Assess',
    step_label_2: 'Remove Infected Parts',
    step_label_3: 'Apply Treatment',
    step_label_4: 'Sanitize & Clean',
    step_label_5: 'Monitor Progress',
    step_label_6: 'Prevent Recurrence',
    step_desc_1: 'Identify all infected plants and separate them to prevent spreading to healthy plants nearby.',
    step_desc_2: 'Carefully remove and bag all infected leaves, stems, or fruits. Do not compost infected material.',
    step_desc_3: 'Apply an appropriate fungicide or bactericide as advised by your local agricultural extension officer.',
    step_desc_4: 'Disinfect all tools used with 70% alcohol or bleach solution. Clean the surrounding soil area.',
    step_desc_5: 'Check the plant every 3–5 days. Look for new symptoms and repeat treatment if needed after 7–10 days.',
    step_desc_6: 'Improve drainage, air circulation and avoid overhead watering. Use disease-resistant varieties next season.',

    // Auth
    login_title: 'Welcome Back', login_sub: 'Sign in to access your dashboard and history',
    register_title: 'Create Your Account', register_sub: 'Join CropCare AI and start protecting your crops',
    label_email: 'Email Address', label_password: 'Password', label_confirm: 'Confirm Password',
    label_name: 'Full Name', label_remember: 'Remember me', label_lang: 'Preferred Language',
    btn_login: 'Sign In', btn_register: 'Create Account',
    no_account: "Don't have an account?", link_signup: 'Create one',
    have_account: 'Already have an account?', link_login: 'Sign in',

    // Dashboard
    dash_title: 'Dashboard', btn_new_scan: 'New Scan',
    stat_total: 'Total Scans', stat_detected: 'Diseases Detected',
    stat_healthy: 'Healthy Leaves', stat_avg_conf: 'Avg. Confidence',
    chart_confidence: 'Prediction Confidence Over Time',
    chart_breakdown: 'Disease Breakdown',
    top_diseases: 'Most Detected Diseases',
    recent_preds: 'Recent Predictions', view_all: 'View All',
    th_crop: 'Crop', th_disease: 'Disease', th_confidence: 'Confidence',
    th_status: 'Status', th_date: 'Date', th_image: 'Image', th_action: 'Action',
    no_scans: 'No scans yet. Scan your first leaf!',

    // History
    history_title: 'Prediction History',
    no_history: 'No prediction history yet.', btn_start: 'Start Scanning',

    // Community
    comm_title: 'Community',
    comm_subtitle: 'Working together to keep our fields safe.',
    comm_tab_alerts: 'Regional Alerts',
    comm_tab_schemes: 'Govt Schemes & Subsidies',
    comm_stat_farmers: 'Active Farmers Nearby',
    comm_stat_reports: 'Reports in Region Today',
    comm_stat_hotspots: 'Disease Hotspots',
    comm_alerts_heading: 'Community Disease Alerts',
    comm_view_guidance: 'View Guidance',
    comm_reports_nearby: 'REPORTS NEARBY',
    comm_support_heading: 'Community Support',
    comm_reply: 'Reply',
    comm_post_placeholder: 'Share an observation or ask your local farming community...',
    comm_btn_post: 'Post to Community',
    comm_forecast_heading: 'Yield Forecasting',
    comm_forecast_insight: 'Regional data suggests a 15% increase in Rice yields this season due to favorable weather and low disease impact in the southern quadrants.',
    comm_conf_score: 'CONFIDENCE SCORE',
    comm_schemes_heading: 'Govt Schemes & Subsidies',
    comm_btn_apply: 'Apply Now',
  },

  ta: {
    // Nav
    nav_home: 'முகப்பு', nav_community: 'சமூகம்', nav_dashboard: 'டாஷ்போர்டு', nav_history: 'வரலாறு',
    nav_about: 'பற்றி', nav_login: 'உள்நுழைவு', nav_signup: 'பதிவு செய்',

    // Hero
    hero_badge: 'AI-இயக்கப்படும் தாவர பகுப்பாய்வு',
    hero_title: 'பயிர் நோயை உடனடியாக AI மூலம் கண்டறியுங்கள்',
    hero_subtitle: 'இலை புகைப்படம் பதிவேற்றுங்கள். நமது ஆழ்கற்றல் மாதிரி நோயை கண்டுபிடித்து பரிந்துரைகளை வழங்கும்.',
    stat_classes: 'நோய் வகைகள்', stat_images: 'பயிற்சி படங்கள்', stat_crops: 'பயிர் வகைகள்',
    demo_mode_notice: '⚠ டெமோ பயன்முறை — உண்மையான முன்கணிப்புகளுக்கு முதலில் மாதிரியை பயிற்றுவிக்கவும்.',

    // Upload
    upload_title: 'உங்கள் இலை படத்தை இங்கே இழுத்து விடுங்கள்',
    upload_subtitle: 'அல்லது கிளிக் செய்து தேர்வு செய்யுங்கள் — JPG, PNG (அதிகபட்சம் 5 MB)',
    or_divider: 'அல்லது',
    btn_camera: 'புகைப்படம் எடு', btn_capture: 'கைப்பற்று', btn_cancel: 'ரத்து செய்',
    btn_detect: 'நோயை கண்டறி',

    // Sections
    crops_title: 'ஆதரிக்கப்படும் பயிர்கள்', crops_subtitle: '14 பயிர் இனங்களில் PlantVillage தரவுத்தொகுப்பில் பயிற்றுவிக்கப்பட்டது',
    how_title: 'எப்படி செயல்படுகிறது',
    step1_title: 'இலை பதிவேற்று', step1_desc: 'பாதிக்கப்பட்ட இலையின் தெளிவான நெருங்கிய புகைப்படம் எடுத்து பதிவேற்றுங்கள்.',
    step2_title: 'AI பகுப்பாய்வு', step2_desc: 'நமது MobileNetV2 ஆழ்கற்றல் மாதிரி படத்தை உடனடியாக பகுப்பாய்கிறது.',
    step3_title: 'முடிவுகள் பெறுங்கள்', step3_desc: 'நோய் பெயர், நம்பகத்தன்மை, அறிகுறிகள் மற்றும் பரிந்துரைகளை பெறுங்கள்.',

    // Result
    result_title: 'நோய் கண்டறிதல் முடிவு',
    result_crop: 'பயிர்', result_disease: 'நோய்', result_confidence: 'நம்பகத்தன்மை',
    tab_original: 'அசல்', tab_gradcam: 'AI கவனம் (Grad-CAM)',
    gradcam_note: 'சிவப்பு/வெப்ப பகுதிகள் AI எங்கே கவனம் செலுத்தியது என்பதை காட்டுகின்றன.',
    rec_symptoms: 'அறிகுறிகள்', rec_prevention: 'தடுப்பு',
    rec_management: 'மேலாண்மை', rec_monitoring: 'கண்காணிப்பு',
    no_data: 'தரவு இல்லை.',
    chemical_disclaimer: 'எந்த இரசாயன சிகிச்சையும் பயன்படுத்துவதற்கு முன்பு எப்போதும் உள்ளூரில் அங்கீகரிக்கப்பட்ட பூச்சிக்கொல்லி லேபிள்களை பின்பற்றவும் மற்றும் வேளாண் நீட்டிப்பு அதிகாரியை அணுகவும்.',
    healthy_msg: 'நல்ல செய்தி! உங்கள் பயிர் ஆரோக்கியமாக தெரிகிறது. தொடர்ந்து கண்காணிப்பு மற்றும் நல்ல வேளாண் நடைமுறைகளை தொடருங்கள்.',
    btn_scan_another: 'மற்றொரு இலையை ஸ்கேன் செய்', btn_history: 'வரலாறு பார்', btn_print: 'அச்சிடு',

    // Disease Report
    report_title: 'நோய் அறிக்கை',
    healthy_report_title: 'பயிர் ஆரோக்கிய அறிக்கை',
    healthy_observations: 'ஆரோக்கிய அவதானிப்புகள்',
    healthy_care: 'பராமரிப்பு மற்றும் தடுப்பு வழிகாட்டுதல்கள்',
    steps_title: 'இந்த நோயை எவ்வாறு அகற்றுவது',
    healthy_steps_title: 'ஆரோக்கியமான பயிர் பராமரிப்புக்கான 6 படிகள்',
    steps_subtitle: 'உங்கள் பயிரில் இருந்து நோயை சிகிச்சை செய்து அகற்ற இந்த 6 படிகளை பின்பற்றுங்கள்',
    healthy_steps_subtitle: 'சிறந்த வளர்ச்சியை பராமரிக்கவும் நோய்த்தொற்றுகளைத் தடுக்கவும் இந்த 6 படிகளைப் பின்பற்றுங்கள்',
    step_label_1: 'தனிமைப்படுத்தி மதிப்பிடுங்கள்',
    step_label_2: 'பாதிக்கப்பட்ட பகுதிகளை அகற்றுங்கள்',
    step_label_3: 'சிகிச்சை பயன்படுத்துங்கள்',
    step_label_4: 'சுத்தப்படுத்துங்கள்',
    step_label_5: 'முன்னேற்றத்தை கண்காணிக்கவும்',
    step_label_6: 'மீண்டும் வருவதை தடுக்கவும்',
    step_desc_1: 'பாதிக்கப்பட்ட அனைத்து தாவரங்களையும் கண்டறிந்து, அருகிலுள்ள ஆரோக்கியமான தாவரங்களுக்கு பரவாமல் தடுக்க தனிமைப்படுத்துங்கள்.',
    step_desc_2: 'பாதிக்கப்பட்ட இலைகள், தண்டுகள் அல்லது பழங்களை கவனமாக அகற்றி பையில் வையுங்கள். பாதிக்கப்பட்ட பொருட்களை உரமாக்காதீர்கள்.',
    step_desc_3: 'உங்கள் உள்ளூர் வேளாண் நீட்டிப்பு அதிகாரியின் ஆலோசனையின்படி பூஞ்சைக்கொல்லி அல்லது பாக்டீரியாக்கொல்லி பயன்படுத்துங்கள்.',
    step_desc_4: 'பயன்படுத்திய அனைத்து கருவிகளையும் 70% ஆல்கஹால் அல்லது ப்ளீச் கரைசலால் கிருமி நாசினி செய்யுங்கள்.',
    step_desc_5: 'ஒவ்வொரு 3-5 நாட்களுக்கும் ஒரு முறை தாவரத்தை சரிபார்க்கவும். புதிய அறிகுறிகள் தெரிந்தால் 7-10 நாட்களுக்கு பிறகு சிகிச்சையை மீண்டும் செய்யுங்கள்.',
    step_desc_6: 'வடிகால், காற்று சுழற்சியை மேம்படுத்துங்கள் மற்றும் மேல்நோக்கிய நீர்ப்பாசனத்தைத் தவிர்க்கவும். அடுத்த சீசனில் நோய் எதிர்ப்பு ரகங்களை பயன்படுத்துங்கள்.'

    // Auth
    login_title: 'மீண்டும் வரவேற்கிறோம்', login_sub: 'உங்கள் டாஷ்போர்டு மற்றும் வரலாற்றை அணுக உள்நுழையுங்கள்',
    register_title: 'உங்கள் கணக்கை உருவாக்கவும்', register_sub: 'CropCare AI இல் சேரவும் மற்றும் உங்கள் பயிர்களை பாதுகாக்க தொடங்குங்கள்',
    label_email: 'மின்னஞ்சல் முகவரி', label_password: 'கடவுச்சொல்', label_confirm: 'கடவுச்சொல் உறுதிப்படுத்தவும்',
    label_name: 'முழு பெயர்', label_remember: 'என்னை நினைவில் வைக்கவும்', label_lang: 'விரும்பிய மொழி',
    btn_login: 'உள்நுழைவு', btn_register: 'கணக்கை உருவாக்கவும்',
    no_account: 'கணக்கு இல்லையா?', link_signup: 'ஒன்றை உருவாக்கவும்',
    have_account: 'ஏற்கனவே கணக்கு உள்ளதா?', link_login: 'உள்நுழைவு',

    // Dashboard
    dash_title: 'டாஷ்போர்டு', btn_new_scan: 'புதிய ஸ்கேன்',
    stat_total: 'மொத்த ஸ்கேன்கள்', stat_detected: 'கண்டறியப்பட்ட நோய்கள்',
    stat_healthy: 'ஆரோக்கியமான இலைகள்', stat_avg_conf: 'சராசரி நம்பகத்தன்மை',
    chart_confidence: 'காலப்போக்கில் முன்கணிப்பு நம்பகத்தன்மை',
    chart_breakdown: 'நோய் பிரிவு',
    top_diseases: 'அதிகமாக கண்டறியப்பட்ட நோய்கள்',
    recent_preds: 'சமீபத்திய முன்கணிப்புகள்', view_all: 'அனைத்தும் பார்',
    th_crop: 'பயிர்', th_disease: 'நோய்', th_confidence: 'நம்பகத்தன்மை',
    th_status: 'நிலை', th_date: 'தேதி', th_image: 'படம்', th_action: 'செயல்',
    no_scans: 'இன்னும் ஸ்கேன் இல்லை. உங்கள் முதல் இலையை ஸ்கேன் செய்யுங்கள்!',

    // History
    history_title: 'முன்கணிப்பு வரலாறு',
    no_history: 'இன்னும் முன்கணிப்பு வரலாறு இல்லை.', btn_start: 'ஸ்கேன் தொடங்கவும்',

    // Community
    comm_title: 'சமூகம்',
    comm_subtitle: 'நமது வயல்களைப் பாதுகாப்பாக வைத்திருக்க ஒன்றிணைந்து செயல்படுவோம்.',
    comm_tab_alerts: 'வட்டார எச்சரிக்கைகள்',
    comm_tab_schemes: 'அரசு திட்டங்கள் & மானியங்கள்',
    comm_stat_farmers: 'அருகிலுள்ள விவசாயிகள்',
    comm_stat_reports: 'இன்றைய பதிவுகள்',
    comm_stat_hotspots: 'நோய் பாதிப்பு பகுதிகள்',
    comm_alerts_heading: 'சமூக பயிர் நோய் எச்சரிக்கைகள்',
    comm_view_guidance: 'வழிகாட்டுதலைப் பார்',
    comm_reports_nearby: 'அருகிலுள்ள பதிவுகள்',
    comm_support_heading: 'விவசாயிகள் ஆதரவு மன்றம்',
    comm_reply: 'பதிலளி',
    comm_post_placeholder: 'உங்கள் கள அவதானிப்பைப் பகிரவும் அல்லது விவசாயக் குழுவிடம் கேட்கவும்...',
    comm_btn_post: 'சமூகத்தில் பதிவிடுங்கள்',
    comm_forecast_heading: 'விளைச்சல் முன்னறிவிப்பு',
    comm_forecast_insight: 'சாதகமான வானிலை மற்றும் தெற்கு பகுதிகளில் நோய் தாக்கம் குறைவாக உள்ளதால், இந்த பருவத்தில் நெல் விளைச்சல் 15% அதிகரிக்கும் என தரவுகள் தெரிவிக்கின்றன.',
    comm_conf_score: 'நம்பகத்தன்மை மதிப்பீடு',
    comm_schemes_heading: 'அரசு திட்டங்கள் & மானியங்கள்',
    comm_btn_apply: 'விண்ணப்பிக்கவும்',
  }
};

/**
 * Apply translations to all [data-i18n] elements on the page.
 * Called on page load and after language switch.
 */
function applyTranslations(lang) {
  const t = TRANSLATIONS[lang] || TRANSLATIONS['en'];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });
}

// Export for use in app.js
if (typeof window !== 'undefined') {
  window.TRANSLATIONS = TRANSLATIONS;
  window.applyTranslations = applyTranslations;
}
