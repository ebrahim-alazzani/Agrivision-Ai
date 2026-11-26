import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../../../core/usecases/usecase.dart';
import '../../../domain/farms/entities/farm_entity.dart';
import '../../../domain/farms/usecases/farm_usecases.dart';

class FarmsController extends GetxController {
  static FarmsController get instance => Get.find();

  final GetFarmsUseCase getFarmsUseCase;
  final AddFarmUseCase addFarmUseCase;
  final DeleteFarmUseCase deleteFarmUseCase;

  FarmsController({
    required this.getFarmsUseCase,
    required this.addFarmUseCase,
    required this.deleteFarmUseCase,
  });

  final farmsList = <FarmEntity>[].obs;
  final isLoading = false.obs;
  final errorMessage = ''.obs;

  @override
  void onInit() {
    super.onInit();
    loadFarms();
  }

  Future<void> loadFarms() async {
    isLoading.value = true;
    errorMessage.value = '';
    final result = await getFarmsUseCase(const NoParams());
    result.fold(
      (failure) => errorMessage.value = failure.message,
      (farms) => farmsList.assignAll(farms),
    );
    isLoading.value = false;
  }

  Future<void> createFarm({
    required String name,
    required String region,
    required double area,
  }) async {
    final farm = FarmEntity(
      id: const Uuid().v4(),
      name: name.trim(),
      region: region.trim(),
      area: area,
      createdAt: DateTime.now().toIso8601String(),
    );
    final result = await addFarmUseCase(farm);
    result.fold(
      (failure) => Get.snackbar('خطأ', failure.message),
      (saved) {
        farmsList.insert(0, saved);
        Get.snackbar('تم الحفظ', 'تمت إضافة المزرعة بنجاح');
      },
    );
  }

  Future<void> removeFarm(String id) async {
    final result = await deleteFarmUseCase(id);
    result.fold(
      (failure) => Get.snackbar('خطأ', failure.message),
      (_) => farmsList.removeWhere((f) => f.id == id),
    );
  }
}
