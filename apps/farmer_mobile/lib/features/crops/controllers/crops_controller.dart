import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../../../core/usecases/usecase.dart';
import '../../../domain/crops/entities/crop_entity.dart';
import '../../../domain/crops/usecases/crop_usecases.dart';

class CropsController extends GetxController {
  static CropsController get instance => Get.find();

  final GetCropsUseCase getCropsUseCase;
  final AddCropUseCase addCropUseCase;
  final DeleteCropUseCase deleteCropUseCase;

  CropsController({
    required this.getCropsUseCase,
    required this.addCropUseCase,
    required this.deleteCropUseCase,
  });

  final cropsList = <CropEntity>[].obs;
  final isLoading = false.obs;
  final errorMessage = ''.obs;

  @override
  void onInit() {
    super.onInit();
    loadCrops();
  }

  Future<void> loadCrops() async {
    isLoading.value = true;
    errorMessage.value = '';
    final result = await getCropsUseCase(const NoParams());
    result.fold(
      (failure) => errorMessage.value = failure.message,
      (crops) => cropsList.assignAll(crops),
    );
    isLoading.value = false;
  }

  Future<void> createCrop({
    required String farmId,
    required String name,
    required String cropType,
    required String status,
  }) async {
    final crop = CropEntity(
      id: const Uuid().v4(),
      farmId: farmId,
      name: name.trim(),
      cropType: cropType.trim(),
      plantingDate: DateTime.now().toIso8601String().split('T').first,
      status: status.trim(),
    );
    final result = await addCropUseCase(crop);
    result.fold(
      (failure) => Get.snackbar('خطأ', failure.message),
      (saved) {
        cropsList.insert(0, saved);
        Get.snackbar('تم الحفظ', 'تمت إضافة المحصول بنجاح');
      },
    );
  }

  Future<void> removeCrop(String id) async {
    final result = await deleteCropUseCase(id);
    result.fold(
      (failure) => Get.snackbar('خطأ', failure.message),
      (_) => cropsList.removeWhere((c) => c.id == id),
    );
  }
}
