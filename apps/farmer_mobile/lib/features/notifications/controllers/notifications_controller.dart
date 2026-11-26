import 'package:get/get.dart';
import '../widgets/alert_card.dart';

class NotificationItem {
  final String title;
  final String message;
  final String time;
  final AlertSeverity severity;

  NotificationItem({
    required this.title,
    required this.message,
    required this.time,
    required this.severity,
  });
}

class NotificationsController extends GetxController {
  static NotificationsController get instance => Get.find();

  final notifications = <NotificationItem>[
    NotificationItem(
      title: 'تحذير صقيع (ضريب) قادم',
      message: 'يتوقع هبوط درجات الحرارة إلى 2°C فجر غد في قاع جهران - ذمار. قم بتشغيل الري الرذاذي فوراً لحماية الشتلات.',
      time: 'منذ 25 دقيقة',
      severity: AlertSeverity.warning,
    ),
    NotificationItem(
      title: 'انتهاء فترة الأمان (PHI)',
      message: 'محصول الطماطم في حقل وادي ظهر أصبح آمناً للحصاد اليوم بعد انقضاء 7 أيام على رش المبيد.',
      time: 'منذ ساعتين',
      severity: AlertSeverity.info,
    ),
    NotificationItem(
      title: 'تنبيه تفشي دودة الحشد',
      message: 'تم الإبلاغ عن بؤر إصابة بدودة الحشد الخريفية في الحقول المجاورة بسهل تهامة. يرجى فحص أوراق الذرة بعناية.',
      time: 'أمس',
      severity: AlertSeverity.critical,
    ),
  ].obs;
}
