import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../entities/farm_entity.dart';

abstract class FarmRepository {
  Future<Either<Failure, List<FarmEntity>>> getFarms();
  Future<Either<Failure, FarmEntity>> addFarm(FarmEntity farm);
  Future<Either<Failure, void>> deleteFarm(String id);
}
