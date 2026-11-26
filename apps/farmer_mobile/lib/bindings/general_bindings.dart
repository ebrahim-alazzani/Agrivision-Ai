import 'package:get/get.dart';
import '../core/network/api_service.dart';
import '../core/services/plant_disease_classifier_service.dart';
import '../data/crops/datasources/crop_local_datasource.dart';
import '../data/crops/repositories_impl/crop_repository_impl.dart';
import '../data/farms/datasources/farm_local_datasource.dart';
import '../data/farms/repositories_impl/farm_repository_impl.dart';
import '../data/plant_analysis/datasources/plant_analysis_local_datasource.dart';
import '../data/plant_analysis/repositories_impl/plant_analysis_repository_impl.dart';
import '../domain/crops/repositories/crop_repository.dart';
import '../domain/crops/usecases/crop_usecases.dart';
import '../domain/farms/repositories/farm_repository.dart';
import '../domain/farms/usecases/farm_usecases.dart';
import '../domain/plant_analysis/repositories/plant_analysis_repository.dart';
import '../domain/plant_analysis/usecases/plant_analysis_usecases.dart';

class GeneralBindings extends Bindings {
  @override
  void dependencies() {
    Get.put<ApiService>(ApiService(), permanent: true);

    // Farms DI
    Get.lazyPut<FarmLocalDataSource>(() => FarmLocalDataSourceImpl(), fenix: true);
    Get.lazyPut<FarmRepository>(
      () => FarmRepositoryImpl(localDataSource: Get.find()),
      fenix: true,
    );
    Get.lazyPut(() => GetFarmsUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => AddFarmUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => DeleteFarmUseCase(Get.find()), fenix: true);

    // Crops DI
    Get.lazyPut<CropLocalDataSource>(() => CropLocalDataSourceImpl(), fenix: true);
    Get.lazyPut<CropRepository>(
      () => CropRepositoryImpl(localDataSource: Get.find()),
      fenix: true,
    );
    Get.lazyPut(() => GetCropsUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => AddCropUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => DeleteCropUseCase(Get.find()), fenix: true);

    // Plant Analysis DI
    Get.lazyPut<PlantAnalysisLocalDataSource>(
      () => PlantAnalysisLocalDataSourceImpl(
        classifierService: PlantDiseaseClassifierService.instance,
      ),
      fenix: true,
    );
    Get.lazyPut<PlantAnalysisRepository>(
      () => PlantAnalysisRepositoryImpl(localDataSource: Get.find()),
      fenix: true,
    );
    Get.lazyPut(() => ClassifyPlantImageUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => ClassifyLiveFrameUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => SavePlantAnalysisUseCase(Get.find()), fenix: true);
    Get.lazyPut(() => GetPlantAnalysisHistoryUseCase(Get.find()), fenix: true);
  }
}
