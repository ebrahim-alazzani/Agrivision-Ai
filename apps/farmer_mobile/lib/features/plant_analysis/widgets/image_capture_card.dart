import 'dart:io';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/plant_analysis_controller.dart';

class ImageCaptureCard extends StatelessWidget {
  final PlantAnalysisController controller;

  const ImageCaptureCard({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Obx(() {
      final imagePath = controller.capturedImagePath.value;
      final hasImage = imagePath.isNotEmpty && File(imagePath).existsSync();

      return AgriTile(
        padding: const EdgeInsets.all(14),
        flowColors: const [AgriColors.emerald, AgriColors.cyanDeep],
        child: Column(
          children: [
            Container(
              height: 240,
              width: double.infinity,
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF12171F) : const Color(0xFFEDF2F7),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isDark
                      ? Colors.white.withValues(alpha: 0.08)
                      : Colors.black.withValues(alpha: 0.05),
                ),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: hasImage
                    ? Image.file(
                        File(imagePath),
                        fit: BoxFit.cover,
                        width: double.infinity,
                      )
                    : Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AgriColors.emerald.withValues(alpha: 0.12),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Iconsax.camera,
                                size: 38,
                                color: AgriColors.emerald,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              'التقط صورة أو اختر من الاستوديو',
                              style: TextStyle(
                                fontSize: 13,
                                color: isDark
                                    ? AgriColors.darkMuted
                                    : AgriColors.lightMuted,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: AgriButton(
                    text: 'التقاط صورة',
                    icon: Iconsax.camera,
                    onPressed: () => controller.captureFromCamera(),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: AgriButton(
                    text: 'الاستوديو',
                    icon: Iconsax.gallery,
                    isOutlined: true,
                    color: AgriColors.cyan,
                    onPressed: () => controller.pickFromGallery(),
                  ),
                ),
              ],
            ),
          ],
        ),
      );
    });
  }
}
