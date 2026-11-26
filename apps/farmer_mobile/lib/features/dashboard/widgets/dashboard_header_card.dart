import 'package:flutter/material.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../theme/agri_colors.dart';

class DashboardHeaderCard extends StatelessWidget {
  final int farmsCount;
  final int analysesCount;

  const DashboardHeaderCard({
    super.key,
    required this.farmsCount,
    required this.analysesCount,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriTile(
      flowColors: const [AgriColors.cyan, AgriColors.emerald],
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              gradient: AgriColors.primaryGradient,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AgriColors.emerald.withValues(alpha: 0.35),
                  blurRadius: 14,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Icon(Icons.spa_rounded, color: AgriColors.darkBg, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'المراقب الزراعي الذكي',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: isDark ? AgriColors.darkText : AgriColors.lightText,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  farmsCount > 0
                      ? 'لديك $farmsCount مزارع مسجلة • $analysesCount فحص محفوظ'
                      : 'ابدأ بإضافة مزرعتك أو فحص أول نبات محلياً',
                  style: TextStyle(
                    fontSize: 12,
                    color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: AgriColors.emerald.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(
                color: AgriColors.emerald.withValues(alpha: 0.35),
              ),
            ),
            child: const Text(
              'ONNX محلي',
              style: TextStyle(
                fontSize: 10,
                color: AgriColors.emerald,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
