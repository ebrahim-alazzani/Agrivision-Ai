import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_glass_app_bar.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../common/widgets/confidence_indicator.dart';
import '../../../common/widgets/severity_badge.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/plant_analysis_controller.dart';

class PlantResultView extends GetView<PlantAnalysisController> {
  const PlantResultView({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriWaveScaffold(
      appBar: const AgriGlassAppBar(
        title: 'تقرير التشخيص الذكي',
        subtitle: 'نتيجة الفحص المخبري المحلي',
        showBack: true,
      ),
      body: Obx(() {
        final res = controller.currentResult.value;
        if (res == null) {
          return const Center(child: Text('لا توجد نتيجة فحص حالياً'));
        }

        final accentColor = res.isHealthy ? AgriColors.emerald : AgriColors.amber;

        return SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 40),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AgriTile(
                flowColors: res.isHealthy
                    ? [AgriColors.emerald, AgriColors.cyan]
                    : [AgriColors.amber, AgriColors.rose],
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: accentColor.withValues(alpha: 0.16),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: accentColor.withValues(alpha: 0.4),
                          width: 1.5,
                        ),
                      ),
                      child: Icon(
                        res.isHealthy
                            ? Icons.check_circle_rounded
                            : Icons.warning_amber_rounded,
                        color: accentColor,
                        size: 36,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      res.isHealthy ? 'نبات معافى وسليم 🌿' : 'تم رصد إصابة مرضية ⚠️',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        color: res.isHealthy ? AgriColors.emerald : AgriColors.rose,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'المحصول: ${res.cropNameArabic}',
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              AgriTile(
                showFlowLine: false,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'التشخيص المصنّف:',
                          style: TextStyle(
                            color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        SeverityBadge(level: res.severity),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      res.diseaseNameArabic,
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                        color: isDark ? AgriColors.darkText : AgriColors.lightText,
                      ),
                    ),
                    const SizedBox(height: 14),
                    ConfidenceIndicator(confidence: res.confidence),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              AgriTile(
                showFlowLine: false,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Iconsax.info_circle, color: AgriColors.cyan, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'الأعراض والتحليل',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(res.symptoms, style: const TextStyle(fontSize: 13, height: 1.6)),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              AgriTile(
                showFlowLine: false,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Iconsax.tick_circle, color: AgriColors.emerald, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'التوصيات الزراعية',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    ...res.recommendations.map(
                      (rec) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.arrow_left_rounded,
                                size: 18, color: AgriColors.emerald),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(rec, style: const TextStyle(fontSize: 12.5, height: 1.5)),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              AgriButton(
                text: 'تم الحفظ في السجل المحلي • العودة',
                icon: Iconsax.tick_circle,
                gradient: AgriColors.primaryGradient,
                onPressed: () => Get.back(),
              ),
            ],
          ),
        );
      }),
    );
  }
}
