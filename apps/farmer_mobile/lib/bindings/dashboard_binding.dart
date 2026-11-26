import 'package:get/get.dart';
import '../domain/crops/usecases/crop_usecases.dart';
import '../domain/farms/usecases/farm_usecases.dart';
import '../domain/plant_analysis/usecases/plant_analysis_usecases.dart';
import '../features/dashboard/controllers/dashboard_controller.dart';

class DashboardBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<DashboardController>(
      () => DashboardController(
        getFarmsUseCase: Get.find<GetFarmsUseCase>(),
        getCropsUseCase: Get.find<GetCropsUseCase>(),
        getHistoryUseCase: Get.find<GetPlantAnalysisHistoryUseCase>(),
      ),
      fenix: true,
    );
  }
}
