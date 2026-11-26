import 'package:get/get.dart';
import '../../../core/usecases/usecase.dart';
import '../../../domain/crops/usecases/crop_usecases.dart';
import '../../../domain/farms/usecases/farm_usecases.dart';
import '../../../domain/plant_analysis/entities/plant_analysis_entity.dart';
import '../../../domain/plant_analysis/usecases/plant_analysis_usecases.dart';

class DashboardController extends GetxController {
  static DashboardController get instance => Get.find();

  final GetFarmsUseCase getFarmsUseCase;
  final GetCropsUseCase getCropsUseCase;
  final GetPlantAnalysisHistoryUseCase getHistoryUseCase;

  DashboardController({
    required this.getFarmsUseCase,
    required this.getCropsUseCase,
    required this.getHistoryUseCase,
  });

  final selectedIndex = 0.obs;
  final farmsCount = 0.obs;
  final totalArea = 0.0.obs;
  final cropsCount = 0.obs;
  final analysesCount = 0.obs;
  final healthyPercentage = 0.obs;
  final recentAnalyses = <PlantAnalysisEntity>[].obs;
  final isLoading = false.obs;

  @override
  void onInit() {
    super.onInit();
    refreshDashboard();
  }

  Future<void> refreshDashboard() async {
    isLoading.value = true;

    final farmsRes = await getFarmsUseCase(const NoParams());
    farmsRes.fold((_) {}, (farms) {
      farmsCount.value = farms.length;
      totalArea.value = farms.fold(0.0, (sum, f) => sum + f.area);
    });

    final cropsRes = await getCropsUseCase(const NoParams());
    cropsRes.fold((_) {}, (crops) {
      cropsCount.value = crops.length;
    });

    final historyRes = await getHistoryUseCase(const NoParams());
    historyRes.fold((_) {}, (history) {
      analysesCount.value = history.length;
      recentAnalyses.assignAll(history.reversed.take(5).toList());
      if (history.isNotEmpty) {
        final healthyCount = history.where((e) => e.isHealthy).length;
        healthyPercentage.value = ((healthyCount / history.length) * 100).round();
      } else {
        healthyPercentage.value = 0;
      }
    });

    isLoading.value = false;
  }

  void changePage(int index) {
    selectedIndex.value = index;
  }
}
