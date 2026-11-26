import 'dart:io';
import 'package:camera/camera.dart';
import 'package:get/get.dart';
import '../../../core/usecases/usecase.dart';
import '../../../domain/plant_analysis/entities/plant_analysis_entity.dart';
import '../../../domain/plant_analysis/usecases/plant_analysis_usecases.dart';
import '../../../routers/routes.dart';
import '../../../utils/helpers/image_utils.dart';

class PlantAnalysisController extends GetxController {
  static PlantAnalysisController get instance => Get.find();

  final ClassifyPlantImageUseCase classifyPlantImageUseCase;
  final ClassifyLiveFrameUseCase classifyLiveFrameUseCase;
  final SavePlantAnalysisUseCase savePlantAnalysisUseCase;
  final GetPlantAnalysisHistoryUseCase getHistoryUseCase;

  PlantAnalysisController({
    required this.classifyPlantImageUseCase,
    required this.classifyLiveFrameUseCase,
    required this.savePlantAnalysisUseCase,
    required this.getHistoryUseCase,
  });

  final selectedImage = Rxn<File>();
  final capturedImagePath = ''.obs;
  final isAnalyzing = false.obs;
  final currentResult = Rxn<PlantAnalysisEntity>();
  final historyList = <PlantAnalysisEntity>[].obs;

  // Live Camera Stream state
  CameraController? cameraController;
  final isLiveCameraActive = false.obs;
  final isCameraInitialized = false.obs;
  final liveResult = Rxn<PlantAnalysisEntity>();
  bool _isProcessingFrame = false;
  DateTime _lastFrameTime = DateTime.fromMillisecondsSinceEpoch(0);

  @override
  void onInit() {
    super.onInit();
    loadHistory();
  }

  @override
  void onClose() {
    stopLiveCamera();
    super.onClose();
  }

  Future<void> loadHistory() async {
    final res = await getHistoryUseCase(const NoParams());
    res.fold((_) {}, (list) => historyList.assignAll(list.reversed.toList()));
  }

  Future<void> captureFromCamera() async {
    await stopLiveCamera();
    try {
      final file = await ImageUtils.pickFromCamera();
      if (file != null) {
        selectedImage.value = file;
        capturedImagePath.value = file.path;
      }
    } catch (e) {
      Get.snackbar('تنبيه', 'تعذر التقاط الصورة: $e');
    }
  }

  Future<void> pickFromGallery() async {
    await stopLiveCamera();
    try {
      final file = await ImageUtils.pickFromGallery();
      if (file != null) {
        selectedImage.value = file;
        capturedImagePath.value = file.path;
      }
    } catch (e) {
      Get.snackbar('تنبيه', 'تعذر اختيار الصورة: $e');
    }
  }

  Future<void> startLiveCamera() async {
    if (isLiveCameraActive.value) return;
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        Get.snackbar('تنبيه', 'لم يتم العثور على كاميرا في الجهاز');
        return;
      }

      cameraController = CameraController(
        cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );

      await cameraController!.initialize();
      isCameraInitialized.value = true;
      isLiveCameraActive.value = true;

      await cameraController!.startImageStream((CameraImage frame) async {
        final now = DateTime.now();
        if (_isProcessingFrame ||
            now.difference(_lastFrameTime).inMilliseconds < 900) {
          return;
        }
        _isProcessingFrame = true;
        _lastFrameTime = now;

        try {
          final rgbImg = ImageUtils.convertCameraImageToRgb(frame);
          if (rgbImg != null) {
            final res = await classifyLiveFrameUseCase(rgbImg);
            res.fold((_) {}, (entity) {
              liveResult.value = entity;
            });
          }
        } finally {
          _isProcessingFrame = false;
        }
      });
    } catch (e) {
      isLiveCameraActive.value = false;
      isCameraInitialized.value = false;
      Get.snackbar('تنبيه', 'تعذر تشغيل البث المباشر للكاميرا: $e');
    }
  }

  Future<void> stopLiveCamera() async {
    isLiveCameraActive.value = false;
    isCameraInitialized.value = false;
    final ctrl = cameraController;
    cameraController = null;
    if (ctrl != null) {
      try {
        if (ctrl.value.isStreamingImages) {
          await ctrl.stopImageStream();
        }
        await ctrl.dispose();
      } catch (_) {}
    }
  }

  Future<void> submitAnalysis() async {
    if (selectedImage.value == null) {
      Get.snackbar('تنبيه', 'يرجى التقاط صورة للنبات أولاً');
      return;
    }

    isAnalyzing.value = true;
    final res = await classifyPlantImageUseCase(selectedImage.value!);
    isAnalyzing.value = false;

    res.fold(
      (failure) => Get.snackbar('خطأ أثناء الفحص', failure.message),
      (entity) async {
        currentResult.value = entity;
        await savePlantAnalysisUseCase(entity);
        await loadHistory();
        Get.toNamed(AppRoutes.plantResult);
      },
    );
  }
}
