import 'package:get/get.dart';
import '../domain/plant_analysis/usecases/plant_analysis_usecases.dart';
import '../features/plant_analysis/controllers/plant_analysis_controller.dart';

class PlantAnalysisBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<PlantAnalysisController>(
      () => PlantAnalysisController(
        classifyPlantImageUseCase: Get.find<ClassifyPlantImageUseCase>(),
        classifyLiveFrameUseCase: Get.find<ClassifyLiveFrameUseCase>(),
        savePlantAnalysisUseCase: Get.find<SavePlantAnalysisUseCase>(),
        getHistoryUseCase: Get.find<GetPlantAnalysisHistoryUseCase>(),
      ),
      fenix: true,
    );
  }
}
