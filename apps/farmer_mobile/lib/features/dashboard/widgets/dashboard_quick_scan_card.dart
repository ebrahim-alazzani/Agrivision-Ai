import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../routers/routes.dart';
import '../../../theme/agri_colors.dart';

class DashboardQuickScanCard extends StatelessWidget {
  const DashboardQuickScanCard({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriTile(
      flowColors: const [AgriColors.emerald, AgriColors.cyanDeep],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(11),
                decoration: BoxDecoration(
                  color: AgriColors.emerald.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: AgriColors.emerald.withValues(alpha: 0.30),
                  ),
                ),
                child: const Icon(Iconsax.scan, color: AgriColors.emerald, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'فحص النبات بالرؤية الحاسوبية',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: isDark ? AgriColors.darkText : AgriColors.lightText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'بث مباشر بالكاميرا أو صورة من الاستوديو — يعمل بدون إنترنت',
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: AgriButton(
                  text: 'فحص مرض نباتي',
                  icon: Iconsax.camera,
                  onPressed: () => Get.toNamed(AppRoutes.plantAnalysis),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: AgriButton(
                  text: 'فحص الآفات',
                  icon: Iconsax.radar,
                  isOutlined: true,
                  color: AgriColors.cyan,
                  onPressed: () => Get.toNamed(AppRoutes.pestAnalysis),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
