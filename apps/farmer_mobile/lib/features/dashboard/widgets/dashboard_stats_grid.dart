import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_stat_card.dart';
import '../../../routers/routes.dart';
import '../../../theme/agri_colors.dart';

class DashboardStatsGrid extends StatelessWidget {
  final int farmsCount;
  final double totalArea;
  final int cropsCount;
  final int analysesCount;
  final int healthyPercentage;

  const DashboardStatsGrid({
    super.key,
    required this.farmsCount,
    required this.totalArea,
    required this.cropsCount,
    required this.analysesCount,
    required this.healthyPercentage,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: AgriStatCard(
                title: 'المزارع المسجلة',
                value: '$farmsCount',
                subtitle: '${totalArea.toStringAsFixed(0)} م² إجمالي',
                icon: Iconsax.tree,
                accentColor: AgriColors.emerald,
                badgeText: farmsCount > 0 ? 'SQLite' : 'أضف مزرعة',
                onTap: () => Get.toNamed(AppRoutes.farms),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: AgriStatCard(
                title: 'سلامة الفحوصات',
                value: analysesCount > 0 ? '$healthyPercentage%' : '—',
                subtitle: analysesCount > 0 ? 'من إجمالي الفحوصات' : 'لا توجد فحوصات بعد',
                icon: Iconsax.heart,
                accentColor: AgriColors.cyan,
                badgeText: analysesCount > 0 ? 'فعلي' : 'جديد',
                onTap: () => Get.toNamed(AppRoutes.plantAnalysis),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: AgriStatCard(
                title: 'المحاصيل النشطة',
                value: '$cropsCount',
                subtitle: 'سجل المحاصيل المحلي',
                icon: Iconsax.lovely,
                accentColor: AgriColors.amber,
                badgeText: 'متابعة',
                onTap: () => Get.toNamed(AppRoutes.crops),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: AgriStatCard(
                title: 'الفحوصات المحفوظة',
                value: '$analysesCount',
                subtitle: 'تشخيص ONNX محلي',
                icon: Iconsax.document_text,
                accentColor: AgriColors.blue,
                badgeText: '13.2 MB',
                onTap: () => Get.toNamed(AppRoutes.plantAnalysis),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
