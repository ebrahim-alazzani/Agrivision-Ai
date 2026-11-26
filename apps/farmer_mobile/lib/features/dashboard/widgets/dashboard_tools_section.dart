import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../routers/routes.dart';
import '../../../theme/agri_colors.dart';

class DashboardToolsSection extends StatelessWidget {
  const DashboardToolsSection({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AgriTile(
          flowColors: const [AgriColors.amber, AgriColors.rose],
          onTap: () => Get.toNamed(AppRoutes.dosageCalculator),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(11),
                decoration: BoxDecoration(
                  color: AgriColors.amber.withValues(alpha: 0.14),
                  shape: BoxShape.circle,
                  border: Border.all(color: AgriColors.amber.withValues(alpha: 0.30)),
                ),
                child: const Icon(Iconsax.calculator, color: AgriColors.amber, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'حاسبة جرعات المبيدات وفترة الأمان',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: isDark ? AgriColors.darkText : AgriColors.lightText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'حساب كمية المبيد بدقة وفق حجم خزان الرش',
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios_rounded,
                size: 16,
                color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
              ),
            ],
          ),
        ),
        AgriTile(
          showFlowLine: false,
          onTap: () => Get.toNamed(AppRoutes.weather),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(11),
                decoration: BoxDecoration(
                  color: AgriColors.cyan.withValues(alpha: 0.14),
                  shape: BoxShape.circle,
                  border: Border.all(color: AgriColors.cyan.withValues(alpha: 0.30)),
                ),
                child: const Icon(Iconsax.cloud_sunny, color: AgriColors.cyan, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'الطقس وتنبيهات الصقيع',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                        color: isDark ? AgriColors.darkText : AgriColors.lightText,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'إرشادات أوقات الرش ومخاطر الضريب',
                      style: TextStyle(
                        fontSize: 12,
                        color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios_rounded,
                size: 16,
                color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
