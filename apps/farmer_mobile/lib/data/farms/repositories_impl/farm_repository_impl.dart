import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../../../domain/farms/entities/farm_entity.dart';
import '../../../domain/farms/repositories/farm_repository.dart';
import '../datasources/farm_local_datasource.dart';
import '../models/farm_model.dart';

class FarmRepositoryImpl implements FarmRepository {
  final FarmLocalDataSource localDataSource;

  FarmRepositoryImpl({required this.localDataSource});

  @override
  Future<Either<Failure, List<FarmEntity>>> getFarms() async {
    try {
      final farms = await localDataSource.getFarms();
      return Right(farms);
    } catch (e) {
      return Left(CacheFailure('تعذر تحميل بيانات المزارع: $e'));
    }
  }

  @override
  Future<Either<Failure, FarmEntity>> addFarm(FarmEntity farm) async {
    try {
      final saved = await localDataSource.addFarm(FarmModel.fromEntity(farm));
      return Right(saved);
    } catch (e) {
      return Left(CacheFailure('تعذر حفظ المزرعة: $e'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteFarm(String id) async {
    try {
      await localDataSource.deleteFarm(id);
      return const Right(null);
    } catch (e) {
      return Left(CacheFailure('تعذر حذف المزرعة: $e'));
    }
  }
}
