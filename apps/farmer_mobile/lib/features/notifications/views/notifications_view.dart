import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../controllers/notifications_controller.dart';
import '../widgets/alert_card.dart';

class NotificationsView extends GetView<NotificationsController> {
  const NotificationsView({super.key});

  @override
  Widget build(BuildContext context) {
    if (!Get.isRegistered<NotificationsController>()) {
      Get.put(NotificationsController());
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('التنبيهات والإشعارات الزراعية'),
      ),
      body: Obx(
        () => ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: controller.notifications.length,
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemBuilder: (context, index) {
            final item = controller.notifications[index];
            return AlertCard(
              title: item.title,
              message: item.message,
              time: item.time,
              severity: item.severity,
            );
          },
        ),
      ),
    );
  }
}
