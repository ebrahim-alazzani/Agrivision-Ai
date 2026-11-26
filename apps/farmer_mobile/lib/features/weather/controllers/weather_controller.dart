import 'package:get/get.dart';

class WeatherAlertModel {
  final String title;
  final String description;
  final String severity; // warning, danger, info
  final String date;

  WeatherAlertModel({
    required this.title,
    required this.description,
    required this.severity,
    required this.date,
  });
}

class WeatherController extends GetxController {
  static WeatherController get instance => Get.find();

  final currentTemp = '21°C'.obs;
  final humidity = '48%'.obs;
  final windSpeed = '11 كم/س'.obs;
  final frostRisk = 'منخفض'.obs;
  final locationName = 'صنعاء - بني حشيش (المرتفعات)'.obs;
  final isRefreshing = false.obs;

  final activeAlerts = <WeatherAlertModel>[
    WeatherAlertModel(
      title: 'تحذير صقيع إشعاعي محتمل (ضريب)',
      description: 'انخفاض درجات الحرارة فجر الغد للمناطق الجبلية المكشوفة، يُنصح بالري الخفيف قبل الغروب وتغطية المشاتل.',
      severity: 'warning',
      date: 'الليلة - 3:30 ص',
    ),
    WeatherAlertModel(
      title: 'مؤشر ملاءمة الرش بالمبيدات',
      description: 'سرعة الرياح الحالية (11 كم/س) ممتازة للرش الصباحي دون تطاير للرذاذ.',
      severity: 'info',
      date: 'اليوم - حتى 10:00 ص',
    ),
  ].obs;

  void refreshWeather() {
    isRefreshing.value = true;
    // Calculate realistic variance
    final hour = DateTime.now().hour;
    if (hour >= 11 && hour <= 15) {
      currentTemp.value = '24°C';
      humidity.value = '38%';
    } else if (hour >= 20 || hour <= 6) {
      currentTemp.value = '12°C';
      humidity.value = '65%';
      frostRisk.value = 'متوسط';
    } else {
      currentTemp.value = '19°C';
      humidity.value = '46%';
      frostRisk.value = 'منخفض';
    }
    isRefreshing.value = false;
  }
}
