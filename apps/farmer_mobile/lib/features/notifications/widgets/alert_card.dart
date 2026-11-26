import 'package:flutter/material.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../utils/constants/colors.dart';

enum AlertSeverity { critical, warning, info }

class AlertCard extends StatelessWidget {
  final String title;
  final String message;
  final String time;
  final AlertSeverity severity;
  final VoidCallback? onTap;

  const AlertCard({
    super.key,
    required this.title,
    required this.message,
    required this.time,
    this.severity = AlertSeverity.info,
    this.onTap,
  });

  Color _getColor() {
    switch (severity) {
      case AlertSeverity.critical:
        return TColors.error;
      case AlertSeverity.warning:
        return TColors.warning;
      case AlertSeverity.info:
        return TColors.info;
    }
  }

  IconData _getIcon() {
    switch (severity) {
      case AlertSeverity.critical:
        return Icons.warning_rounded;
      case AlertSeverity.warning:
        return Icons.ac_unit_rounded;
      case AlertSeverity.info:
        return Icons.info_outline_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor();

    return AgriCard(
      onTap: onTap,
      borderColor: color.withValues(alpha: 0.5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
            child: Icon(_getIcon(), color: color, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        color: color,
                      ),
                    ),
                    Text(
                      time,
                      style: const TextStyle(fontSize: 11, color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  message,
                  style: const TextStyle(fontSize: 13, color: TColors.textPrimary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
