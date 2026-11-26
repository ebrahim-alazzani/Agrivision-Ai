import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../theme/agri_colors.dart';

class AnalysisTipsBanner extends StatelessWidget {
  const AnalysisTipsBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriTile(
      flowColors: const [AgriColors.cyan, AgriColors.emerald],
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(11),
            decoration: BoxDecoration(
              color: AgriColors.emerald.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Iconsax.info_circle, color: AgriColors.emerald, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'إرشادات الفحص الدقيق',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: isDark ? AgriColors.darkText : AgriColors.lightText,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'وجّه الكاميرا مباشرة نحو ورقة النبات في إضاءة واضحة، أو التقط صورة ثابتة لحفظ التقرير.',
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
    );
  }
}
