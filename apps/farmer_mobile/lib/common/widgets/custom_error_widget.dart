import 'package:flutter/material.dart';
import '../../utils/constants/colors.dart';
import 'agri_button.dart';

class CustomErrorWidget extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const CustomErrorWidget({
    super.key,
    required this.message,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: TColors.error.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.error_outline_rounded,
                size: 54,
                color: TColors.error,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'حدث خطأ غير متوقع',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: TColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                color: TColors.textSecondary,
              ),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              AgriButton(
                text: 'إعادة المحاولة',
                icon: Icons.refresh_rounded,
                width: 160,
                onPressed: onRetry,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
