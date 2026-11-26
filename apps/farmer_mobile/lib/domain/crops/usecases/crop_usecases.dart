import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../../../core/usecases/usecase.dart';
import '../entities/crop_entity.dart';
import '../repositories/crop_repository.dart';

class GetCropsUseCase implements UseCase<List<CropEntity>, NoParams> {
  final CropRepository repository;
  GetCropsUseCase(this.repository);

  @override
  Future<Either<Failure, List<CropEntity>>> call(NoParams params) {
    return repository.getCrops();
  }
}

class AddCropUseCase implements UseCase<CropEntity, CropEntity> {
  final CropRepository repository;
  AddCropUseCase(this.repository);

  @override
  Future<Either<Failure, CropEntity>> call(CropEntity params) {
    return repository.addCrop(params);
  }
}

class DeleteCropUseCase implements UseCase<void, String> {
  final CropRepository repository;
  DeleteCropUseCase(this.repository);

  @override
  Future<Either<Failure, void>> call(String id) {
    return repository.deleteCrop(id);
  }
}
