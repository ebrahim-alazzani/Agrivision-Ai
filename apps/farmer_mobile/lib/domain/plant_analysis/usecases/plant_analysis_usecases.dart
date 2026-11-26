import 'dart:io';
import 'package:dartz/dartz.dart';
import 'package:image/image.dart' as img;
import '../../../core/error/failures.dart';
import '../../../core/usecases/usecase.dart';
import '../entities/plant_analysis_entity.dart';
import '../repositories/plant_analysis_repository.dart';

class ClassifyPlantImageUseCase implements UseCase<PlantAnalysisEntity, File> {
  final PlantAnalysisRepository repository;
  ClassifyPlantImageUseCase(this.repository);

  @override
  Future<Either<Failure, PlantAnalysisEntity>> call(File params) {
    return repository.classifyImage(params);
  }
}

class ClassifyLiveFrameUseCase implements UseCase<PlantAnalysisEntity, img.Image> {
  final PlantAnalysisRepository repository;
  ClassifyLiveFrameUseCase(this.repository);

  @override
  Future<Either<Failure, PlantAnalysisEntity>> call(img.Image params) {
    return repository.classifyLiveFrame(params);
  }
}

class SavePlantAnalysisUseCase implements UseCase<PlantAnalysisEntity, PlantAnalysisEntity> {
  final PlantAnalysisRepository repository;
  SavePlantAnalysisUseCase(this.repository);

  @override
  Future<Either<Failure, PlantAnalysisEntity>> call(PlantAnalysisEntity params) {
    return repository.saveAnalysis(params);
  }
}

class GetPlantAnalysisHistoryUseCase implements UseCase<List<PlantAnalysisEntity>, NoParams> {
  final PlantAnalysisRepository repository;
  GetPlantAnalysisHistoryUseCase(this.repository);

  @override
  Future<Either<Failure, List<PlantAnalysisEntity>>> call(NoParams params) {
    return repository.getHistory();
  }
}
