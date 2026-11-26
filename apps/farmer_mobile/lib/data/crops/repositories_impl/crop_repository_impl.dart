import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../../../domain/crops/entities/crop_entity.dart';
import '../../../domain/crops/repositories/crop_repository.dart';
import '../datasources/crop_local_datasource.dart';
import '../models/crop_model.dart';

class CropRepositoryImpl implements CropRepository {
  final CropLocalDataSource localDataSource;

  CropRepositoryImpl({required this.localDataSource});

  @override
  Future<Either<Failure, List<CropEntity>>> getCrops() async {
    try {
      final crops = await localDataSource.getCrops();
      return Right(crops);
    } catch (e) {
      return Left(CacheFailure('تعذر تحميل المحاصيل: $e'));
    }
  }

  @override
  Future<Either<Failure, CropEntity>> addCrop(CropEntity crop) async {
    try {
      final saved = await localDataSource.addCrop(CropModel.fromEntity(crop));
      return Right(saved);
    } catch (e) {
      return Left(CacheFailure('تعذر حفظ المحصول: $e'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteCrop(String id) async {
    try {
      await localDataSource.deleteCrop(id);
      return const Right(null);
    } catch (e) {
      return Left(CacheFailure('تعذر حذف المحصول: $e'));
    }
  }
}
