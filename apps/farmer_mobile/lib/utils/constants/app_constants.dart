class AppConstants {
  static const String appName = 'AgriVision';
  static const String appNameAr = 'رؤية زراعية';

  // Supported crops focusing on Yemen & Middle East agriculture
  static const List<Map<String, String>> supportedCrops = [
    {'id': 'coffee', 'nameEn': 'Coffee', 'nameAr': 'البن اليمني', 'icon': '☕'},
    {'id': 'wheat', 'nameEn': 'Wheat', 'nameAr': 'القمح', 'icon': '🌾'},
    {'id': 'corn', 'nameEn': 'Maize / Corn', 'nameAr': 'الذرة الشامية', 'icon': '🌽'},
    {'id': 'sorghum', 'nameEn': 'Sorghum', 'nameAr': 'الذرة الرفيعة', 'icon': '🌾'},
    {'id': 'tomato', 'nameEn': 'Tomato', 'nameAr': 'الطماطم', 'icon': '🍅'},
    {'id': 'potato', 'nameEn': 'Potato', 'nameAr': 'البطاطس', 'icon': '🥔'},
    {'id': 'onion', 'nameEn': 'Onion', 'nameAr': 'البصل', 'icon': '🧅'},
    {'id': 'grape', 'nameEn': 'Grape', 'nameAr': 'العنب الرازقي', 'icon': '🍇'},
    {'id': 'pomegranate', 'nameEn': 'Pomegranate', 'nameAr': 'الرمان الصعدي', 'icon': '🍎'},
    {'id': 'mango', 'nameEn': 'Mango', 'nameAr': 'المانجو التهمي', 'icon': '🥭'},
    {'id': 'date_palm', 'nameEn': 'Date Palm', 'nameAr': 'النخيل', 'icon': '🌴'},
  ];

  // Yemeni Agricultural Regions
  static const List<Map<String, String>> yemenRegions = [
    {'id': 'sanaa', 'nameAr': 'صنعاء - بني حشيش / بني مطر', 'nameEn': 'Sana\'a'},
    {'id': 'dhamar', 'nameAr': 'ذمار - قاع جهران', 'nameEn': 'Dhamar - Jahran Plain'},
    {'id': 'ibb', 'nameAr': 'إب - اللواء الأخضر', 'nameEn': 'Ibb - Green Province'},
    {'id': 'tihama', 'nameAr': 'الحديدة - سهل تهامة', 'nameEn': 'Tihama Plain'},
    {'id': 'saada', 'nameAr': 'صعدة - حوض صعدة', 'nameEn': 'Saada Basin'},
    {'id': 'hadhramaut', 'nameAr': 'حضرموت - وادي حضرموت', 'nameEn': 'Hadhramaut Valley'},
    {'id': 'taiz', 'nameAr': 'تعز - جبل صبر والوازعية', 'nameEn': 'Taiz'},
    {'id': 'lahj', 'nameAr': 'لحج - دلتا تبن', 'nameEn': 'Lahj - Tuban Delta'},
    {'id': 'abyan', 'nameAr': 'أبين - دلتا أبين', 'nameEn': 'Abyan Delta'},
    {'id': 'marib', 'nameAr': 'مأرب - وادي عبيدة', 'nameEn': 'Marib'},
  ];

  // Severity levels
  static const String severityCritical = 'critical';
  static const String severityHigh = 'high';
  static const String severityModerate = 'moderate';
  static const String severityMild = 'mild';
  static const String severityHealthy = 'healthy';
}
