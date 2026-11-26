import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/plant_analysis_controller.dart';

class LiveCameraScannerCard extends StatelessWidget {
  final PlantAnalysisController controller;

  const LiveCameraScannerCard({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final isLive = controller.isLiveCameraActive.value;
      final isReady = controller.isCameraInitialized.value;
      final liveRes = controller.liveResult.value;

      return AgriTile(
        flowColors: const [AgriColors.cyan, AgriColors.blue],
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(Iconsax.video, color: AgriColors.cyan, size: 22),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    'الفحص المباشر بالكاميرا (بث حي)',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
                  ),
                ),
                if (isLive)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: AgriColors.rose.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: const Text(
                      'مباشر',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AgriColors.rose,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (isLive && isReady && controller.cameraController != null) ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: SizedBox(
                  height: 260,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      CameraPreview(controller.cameraController!),
                      if (liveRes != null)
                        Positioned(
                          left: 10,
                          right: 10,
                          bottom: 10,
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.black.withValues(alpha: 0.72),
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(
                                color: liveRes.isHealthy
                                    ? AgriColors.emerald
                                    : AgriColors.amber,
                                width: 1.2,
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  liveRes.isHealthy
                                      ? Icons.check_circle_rounded
                                      : Icons.warning_amber_rounded,
                                  color: liveRes.isHealthy
                                      ? AgriColors.emerald
                                      : AgriColors.amber,
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Text(
                                        liveRes.diseaseNameArabic,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.w800,
                                          fontSize: 13,
                                        ),
                                      ),
                                      Text(
                                        '${liveRes.cropNameArabic} • الثقة ${(liveRes.confidence * 100).toStringAsFixed(0)}%',
                                        style: const TextStyle(
                                          color: AgriColors.cyan,
                                          fontSize: 11,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              AgriButton(
                text: 'إيقاف البث المباشر',
                icon: Iconsax.stop,
                isOutlined: true,
                color: AgriColors.rose,
                onPressed: () => controller.stopLiveCamera(),
              ),
            ] else
              AgriButton(
                text: 'تشغيل الكاميرا المباشرة (فحص فوري)',
                icon: Iconsax.video_play,
                isOutlined: true,
                color: AgriColors.cyan,
                onPressed: () => controller.startLiveCamera(),
              ),
          ],
        ),
      );
    });
  }
}
