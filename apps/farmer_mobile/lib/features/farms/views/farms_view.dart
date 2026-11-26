import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_glass_app_bar.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/farms_controller.dart';
import '../widgets/add_farm_dialog.dart';

class FarmsView extends GetView<FarmsController> {
  const FarmsView({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriWaveScaffold(
      appBar: const AgriGlassAppBar(
        title: 'المزارع والحقول المسجلة',
        subtitle: 'بيانات محلية حقيقية (SQLite)',
        showBack: true,
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        if (controller.farmsList.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: AgriTile(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Iconsax.tree, size: 44, color: AgriColors.emerald),
                    const SizedBox(height: 12),
                    const Text(
                      'لا توجد مزارع مسجلة بعد',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'اضغط على زر "إضافة حقل" لإدخال بيانات مزرعتك الحقيقية',
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
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 90),
          itemCount: controller.farmsList.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final farm = controller.farmsList[index];
            return AgriTile(
              showFlowLine: false,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AgriColors.emerald.withValues(alpha: 0.14),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Iconsax.tree, color: AgriColors.emerald),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          farm.name,
                          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${farm.region} • ${farm.area.toStringAsFixed(0)} م²',
                          style: TextStyle(
                            color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Iconsax.trash, color: AgriColors.rose, size: 18),
                    onPressed: () => controller.removeFarm(farm.id),
                  ),
                ],
              ),
            );
          },
        );
      }),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Get.dialog(AddFarmDialog(controller: controller)),
        backgroundColor: AgriColors.emerald,
        icon: const Icon(Iconsax.add, color: AgriColors.darkBg),
        label: const Text(
          'إضافة حقل',
          style: TextStyle(color: AgriColors.darkBg, fontWeight: FontWeight.w800),
        ),
      ),
    );
  }
}
