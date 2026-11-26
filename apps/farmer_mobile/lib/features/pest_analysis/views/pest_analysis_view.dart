import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import 'package:image_picker/image_picker.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../common/widgets/confidence_indicator.dart';
import '../../../common/widgets/image_preview_widget.dart';
import '../../../common/widgets/loading_overlay.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/pest_analysis_controller.dart';

class PestAnalysisView extends GetView<PestAnalysisController> {
  const PestAnalysisView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('كشف الآفات الحشرية والعد الآلي'),
      ),
      body: Obx(
        () => LoadingOverlay(
          isLoading: controller.isAnalyzing.value,
          message: 'جاري تشغيل نموذج كشف الآفات (YOLO Engine)...',
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                AgriCard(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        Obx(() {
                          if (controller.selectedImage.value != null) {
                            return ImagePreviewWidget(
                              imageFile: controller.selectedImage.value,
                              onRemove: () => controller.selectedImage.value = null,
                            );
                          }
                          return Container(
                            height: 180,
                            decoration: BoxDecoration(
                              color: AgriColors.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: AgriColors.border),
                            ),
                            child: const Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Iconsax.radar, size: 44, color: AgriColors.warning),
                                  SizedBox(height: 8),
                                  Text('التقط صورة للآفة أو أثر الإصابة الحشرية',
                                      style: TextStyle(color: AgriColors.textSecondary, fontSize: 12)),
                                ],
                              ),
                            ),
                          );
                        }),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: AgriButton(
                                text: 'الكاميرا',
                                icon: Iconsax.camera,
                                onPressed: () => controller.pickImage(ImageSource.camera),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: AgriButton(
                                text: 'المعرض',
                                icon: Iconsax.gallery,
                                isOutlined: true,
                                onPressed: () => controller.pickImage(ImageSource.gallery),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                AgriButton(
                  text: 'كشف الآفات وعدّها',
                  icon: Iconsax.scan,
                  onPressed: () => controller.detectPests(),
                ),
                const SizedBox(height: 16),
                Obx(() {
                  if (controller.detectedPest.value.isEmpty) return const SizedBox.shrink();
                  return AgriCard(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('نتيجة الكشف الآلي:',
                              style: TextStyle(color: AgriColors.textSecondary, fontSize: 12)),
                          const SizedBox(height: 6),
                          Text(controller.detectedPest.value,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(height: 8),
                          Text('عدد الحشرات المرصودة بالصورة: ${controller.pestCount.value}',
                              style: const TextStyle(fontSize: 14, color: AgriColors.warning)),
                          const SizedBox(height: 12),
                          ConfidenceIndicator(confidence: controller.confidence.value),
                        ],
                      ),
                    ),
                  );
                }),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
