import 'package:get/get.dart';

class CropHealthTimelinePoint {
  final String date;
  final double healthIndex; // 0.0 to 1.0 (VARI index)
  final String stage;
  final String note;

  CropHealthTimelinePoint({
    required this.date,
    required this.healthIndex,
    required this.stage,
    required this.note,
  });
}

class MonitoringController extends GetxController {
  static MonitoringController get instance => Get.find();

  final selectedCrop = 'البن اليمني (حقل بني مطر)'.obs;
  final currentHealthScore = 0.88.obs;
  final weeklyChange = '+4.2%'.obs;

  final timeline = <CropHealthTimelinePoint>[
    CropHealthTimelinePoint(
      date: '10 نوفمبر',
      healthIndex: 0.88,
      stage: 'نمو خضري ممتاز',
      note: 'مؤشر الكلوروفيل مرتفع ونسبة الرطوبة ملائمة',
    ),
    CropHealthTimelinePoint(
      date: '03 نوفمبر',
      healthIndex: 0.84,
      stage: 'نمو مستقر',
      note: 'تعافي الأوراق بعد التسميد الورقي',
    ),
    CropHealthTimelinePoint(
      date: '27 أكتوبر',
      healthIndex: 0.79,
      stage: 'بداية تفرعات جانبية',
      note: 'ملاحظة اصفرار طفيف تم علاجه بالحديد المخلبي',
    ),
  ].obs;
}
