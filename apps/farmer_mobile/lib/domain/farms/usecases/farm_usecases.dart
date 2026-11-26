import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../../../core/usecases/usecase.dart';
import '../entities/farm_entity.dart';
import '../repositories/farm_repository.dart';

class GetFarmsUseCase implements UseCase<List<FarmEntity>, NoParams> {
  final FarmRepository repository;
  GetFarmsUseCase(this.repository);

  @override
  Future<Either<Failure, List<FarmEntity>>> call(NoParams params) {
    return repository.getFarms();
  }
}

class AddFarmUseCase implements UseCase<FarmEntity, FarmEntity> {
  final FarmRepository repository;
  AddFarmUseCase(this.repository);

  @override
  Future<Either<Failure, FarmEntity>> call(FarmEntity params) {
    return repository.addFarm(params);
  }
}

class DeleteFarmUseCase implements UseCase<void, String> {
  final FarmRepository repository;
  DeleteFarmUseCase(this.repository);

  @override
  Future<Either<Failure, void>> call(String id) {
    return repository.deleteFarm(id);
  }
}
