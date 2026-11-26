import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/monitoring_controller.dart';
import '../widgets/monitoring_health_item.dart';

class MonitoringView extends GetView<MonitoringController> {
  const MonitoringView({super.key});

  @override
  Widget build(BuildContext context) {
    if (!Get.isRegistered<MonitoringController>()) {
      Get.put(MonitoringController());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('مراقبة صحة المحصول والغطاء النباتي'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Overall Status Card
            AgriCard(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'مؤشر صحة الحقل (VARI)',
                            style: TextStyle(fontSize: 14, color: TColors.textSecondary),
                          ),
                          const SizedBox(height: 4),
                          Obx(
                            () => Text(
                              '${(controller.currentHealthScore.value * 100).toInt()}% ممتاز',
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.w900,
                                color: TColors.primary,
                              ),
                            ),
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: TColors.primary.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Obx(
                          () => Text(
                            controller.weeklyChange.value,
                            style: const TextStyle(
                              color: TColors.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 12),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      MonitoringHealthItem(label: 'كلوروفيل الورق', value: '88%'),
                      MonitoringHealthItem(label: 'رطوبة الحقل', value: '62%'),
                      MonitoringHealthItem(label: 'كثافة النمو', value: 'طبيعي'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Time comparison action button
            AgriButton(
              text: 'مقارنة صور الحقل زمنياً (قبل / بعد)',
              icon: Iconsax.image,
              isOutlined: true,
              onPressed: () {
                Get.snackbar('مقارنة الصور', 'جاري معالجة خوارزمية التغير اللوني للغطاء النباتي');
              },
            ),
            const SizedBox(height: 24),

            const Text(
              'الجدول الزمني لتطور المحصول',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            Obx(
              () => ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: controller.timeline.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final point = controller.timeline[index];
                  return AgriCard(
                    padding: const EdgeInsets.all(14),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: TColors.primary.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: const Icon(Iconsax.calendar, color: TColors.primary, size: 20),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    point.date,
                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                  ),
                                  Text(
                                    'مؤشر: ${(point.healthIndex * 100).toInt()}%',
                                    style: const TextStyle(
                                      color: TColors.primary,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 2),
                              Text(
                                point.stage,
                                style: const TextStyle(color: TColors.secondary, fontSize: 13, fontWeight: FontWeight.w600),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                point.note,
                                style: const TextStyle(color: TColors.textSecondary, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
