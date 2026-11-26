import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_glass_app_bar.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/crops_controller.dart';

class CropsView extends GetView<CropsController> {
  const CropsView({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriWaveScaffold(
      appBar: const AgriGlassAppBar(
        title: 'المحاصيل الزراعية',
        subtitle: 'سجل المحاصيل المحلي (SQLite)',
        showBack: true,
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        if (controller.cropsList.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: AgriTile(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Iconsax.lovely, size: 44, color: AgriColors.amber),
                    const SizedBox(height: 12),
                    const Text(
                      'لا توجد محاصيل مسجلة بعد',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'سيظهر هنا كل محصول تضيفه إلى حقولك المسجلة',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
          itemCount: controller.cropsList.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final crop = controller.cropsList[index];
            return AgriTile(
              showFlowLine: false,
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AgriColors.emerald.withValues(alpha: 0.14),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Iconsax.tree, color: AgriColors.emerald, size: 22),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          crop.name,
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                        const SizedBox(height: 3),
                        Text(
                          'تاريخ الزراعة: ${crop.plantingDate} • الحالة: ${crop.status}',
                          style: TextStyle(
                            fontSize: 12,
                            color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Iconsax.trash, color: AgriColors.rose, size: 18),
                    onPressed: () => controller.removeCrop(crop.id),
                  ),
                ],
              ),
            );
          },
        );
      }),
    );
  }
}
