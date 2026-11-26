import 'package:flutter/material.dart';
import '../../theme/agri_colors.dart';

/// مؤشر نسبة الثقة بالذكاء الاصطناعي بنظام HALVO Gauge
class ConfidenceIndicator extends StatelessWidget {
  final double confidence; // 0.0 to 1.0
  final bool showLabel;

  const ConfidenceIndicator({
    super.key,
    required this.confidence,
    this.showLabel = true,
  });

  Color _getConfidenceColor() {
    if (confidence >= 0.85) return AgriColors.emerald;
    if (confidence >= 0.65) return AgriColors.amber;
    return AgriColors.rose;
  }

  String _getConfidenceText() {
    if (confidence >= 0.85) return 'ثقة عالية جداً';
    if (confidence >= 0.65) return 'ثقة جيدة';
    return 'ثقة منخفضة (تحتاج مراجعة)';
  }

  @override
  Widget build(BuildContext context) {
    final percentage = (confidence * 100).toInt();
    final color = _getConfidenceColor();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            if (showLabel)
              Text(
                _getConfidenceText(),
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                  fontFamily: 'Cairo',
                ),
              ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.16),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: color.withValues(alpha: 0.35), width: 1.0),
              ),
              child: Text(
                '$percentage%',
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w900,
                  fontSize: 12,
                  fontFamily: 'Cairo',
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Container(
          height: 8,
          decoration: BoxDecoration(
            color: isDark
                ? Colors.white.withValues(alpha: 0.08)
                : Colors.black.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(999),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              return Stack(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 600),
                    curve: Curves.easeOutCubic,
                    width: constraints.maxWidth * confidence.clamp(0.0, 1.0),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          color.withValues(alpha: 0.7),
                          color,
                        ],
                      ),
                      borderRadius: BorderRadius.circular(999),
                      boxShadow: [
                        BoxShadow(
                          color: color.withValues(alpha: 0.4),
                          blurRadius: 8,
                          offset: const Offset(0, 1),
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }
}
