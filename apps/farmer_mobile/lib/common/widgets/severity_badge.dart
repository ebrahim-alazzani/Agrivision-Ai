import 'package:flutter/material.dart';
import '../../theme/agri_colors.dart';
import '../../utils/constants/app_constants.dart';

/// شارة درجة الإصابة بنظام HALVO Glow Pill Badge
class SeverityBadge extends StatelessWidget {
  final String? severity;
  final String? level;

  const SeverityBadge({super.key, this.severity, this.level});

  String get _activeSeverity => severity ?? level ?? 'healthy';

  Color _getColor() {
    switch (_activeSeverity.toLowerCase()) {
      case AppConstants.severityCritical:
        return AgriColors.severityCritical;
      case AppConstants.severityHigh:
        return AgriColors.severityHigh;
      case AppConstants.severityModerate:
        return AgriColors.severityModerate;
      case AppConstants.severityMild:
        return AgriColors.severityMild;
      case AppConstants.severityHealthy:
      default:
        return AgriColors.severityHealthy;
    }
  }

  String _getText() {
    switch (_activeSeverity.toLowerCase()) {
      case AppConstants.severityCritical:
        return 'إصابة حرجة';
      case AppConstants.severityHigh:
        return 'إصابة شديدة';
      case AppConstants.severityModerate:
        return 'إصابة متوسطة';
      case AppConstants.severityMild:
        return 'إصابة خفيفة';
      case AppConstants.severityHealthy:
      default:
        return 'سليم ومعافى';
    }
  }

  IconData _getIcon() {
    switch (_activeSeverity.toLowerCase()) {
      case AppConstants.severityCritical:
      case AppConstants.severityHigh:
        return Icons.warning_amber_rounded;
      case AppConstants.severityModerate:
      case AppConstants.severityMild:
        return Icons.info_outline;
      case AppConstants.severityHealthy:
      default:
        return Icons.check_circle_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.35), width: 1.1),
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.18),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getIcon(), size: 14, color: color),
          const SizedBox(width: 5),
          Text(
            _getText(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w800,
              fontSize: 11,
              fontFamily: 'Cairo',
            ),
          ),
        ],
      ),
    );
  }
}
