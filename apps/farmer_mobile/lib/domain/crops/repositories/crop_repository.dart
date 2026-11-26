import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../entities/crop_entity.dart';

abstract class CropRepository {
  Future<Either<Failure, List<CropEntity>>> getCrops();
  Future<Either<Failure, CropEntity>> addCrop(CropEntity crop);
  Future<Either<Failure, void>> deleteCrop(String id);
}
