import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_glass_app_bar.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/plant_analysis_controller.dart';
import '../widgets/analysis_tips_banner.dart';
import '../widgets/image_capture_card.dart';
import '../widgets/live_camera_scanner_card.dart';

class PlantAnalysisView extends GetView<PlantAnalysisController> {
  const PlantAnalysisView({super.key});

  @override
  Widget build(BuildContext context) {
    return AgriWaveScaffold(
      appBar: const AgriGlassAppBar(
        title: 'تشخيص أمراض النبات',
        subtitle: 'نموذج ONNX محلي (38 فئة)',
        showBack: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 36),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const AnalysisTipsBanner(),
            const SizedBox(height: 12),
            LiveCameraScannerCard(controller: controller),
            const SizedBox(height: 12),
            ImageCaptureCard(controller: controller),
            const SizedBox(height: 18),
            Obx(
              () => AgriButton(
                text: 'تحليل الصورة وحفظ النتيجة',
                icon: Iconsax.scan,
                gradient: AgriColors.primaryGradient,
                isLoading: controller.isAnalyzing.value,
                onPressed: controller.capturedImagePath.value.isNotEmpty
                    ? () => controller.submitAnalysis()
                    : null,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
