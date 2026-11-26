import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/weather_controller.dart';

class WeatherView extends GetView<WeatherController> {
  const WeatherView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الطقس ومخاطر الصقيع (الضريب)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Current Weather Card
            AgriCard(
              color: AgriColors.primary,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Iconsax.location, color: Colors.white, size: 18),
                            const SizedBox(width: 6),
                            Obx(() => Text(
                                  controller.locationName.value,
                                  style: const TextStyle(color: Colors.white, fontSize: 13),
                                )),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Text('محدث الآن',
                              style: TextStyle(color: Colors.white, fontSize: 10)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Iconsax.sun_1, color: Colors.amber, size: 56),
                        const SizedBox(width: 16),
                        Obx(() => Text(
                              controller.currentTemp.value,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 44,
                                fontWeight: FontWeight.bold,
                              ),
                            )),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Divider(color: Colors.white.withOpacity(0.2)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _weatherMetric(Iconsax.drop, 'الرطوبة', controller.humidity.value),
                        _weatherMetric(Iconsax.wind, 'الرياح', controller.windSpeed.value),
                        _weatherMetric(Iconsax.danger, 'خطر الصقيع', controller.frostRisk.value),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Agricultural Alerts
            const Text(
              'التنبيهات الزراعية الاستباقية',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
            const SizedBox(height: 12),
            Obx(
              () => Column(
                children: controller.activeAlerts.map((alert) {
                  final isDanger = alert.severity == 'danger';
                  final alertColor = isDanger ? AgriColors.error : AgriColors.warning;

                  return AgriCard(
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: alertColor.withOpacity(0.12),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              isDanger ? Iconsax.warning_2 : Iconsax.info_circle,
                              color: alertColor,
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        alert.title,
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                          color: alertColor,
                                        ),
                                      ),
                                    ),
                                    Text(
                                      alert.date,
                                      style: const TextStyle(
                                        color: AgriColors.textSecondary,
                                        fontSize: 10,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  alert.description,
                                  style: const TextStyle(fontSize: 12, height: 1.4),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _weatherMetric(IconData icon, String label, String value) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 18),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }
}
