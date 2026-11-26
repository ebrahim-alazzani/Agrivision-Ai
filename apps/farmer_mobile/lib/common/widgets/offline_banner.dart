import 'dart:ui';
import 'package:flutter/material.dart';
import '../../theme/agri_colors.dart';

/// شريط حالة عدم الاتصال الزجاجي المطابق لـ HalvoBannerMessage
class OfflineBanner extends StatelessWidget {
  final int pendingCount;
  final VoidCallback? onSyncNow;

  const OfflineBanner({
    super.key,
    this.pendingCount = 0,
    this.onSyncNow,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: AgriColors.amber.withValues(alpha: 0.16),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: AgriColors.amber.withValues(alpha: 0.35),
                width: 1.1,
              ),
              boxShadow: [
                BoxShadow(
                  color: AgriColors.amber.withValues(alpha: 0.15),
                  blurRadius: 14,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: AgriColors.amber.withValues(alpha: 0.20),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.wifi_off_rounded,
                    color: AgriColors.amber,
                    size: 18,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    pendingCount > 0
                        ? 'وضع غير متصل: لديك $pendingCount فحوصات بانتظار المزامنة'
                        : 'أنت في وضع غير متصل، يتم حفظ البيانات محلياً',
                    style: const TextStyle(
                      color: AgriColors.amber,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                      fontFamily: 'Cairo',
                    ),
                  ),
                ),
                if (pendingCount > 0 && onSyncNow != null) ...[
                  const SizedBox(width: 8),
                  TextButton(
                    onPressed: onSyncNow,
                    style: TextButton.styleFrom(
                      foregroundColor: Colors.white,
                      backgroundColor: AgriColors.amber.withValues(alpha: 0.8),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                    child: const Text(
                      'مزامنة',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        fontFamily: 'Cairo',
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
