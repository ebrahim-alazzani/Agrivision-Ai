import 'dart:io';
import 'package:dartz/dartz.dart';
import 'package:image/image.dart' as img;
import '../../../core/error/failures.dart';
import '../../../domain/plant_analysis/entities/plant_analysis_entity.dart';
import '../../../domain/plant_analysis/repositories/plant_analysis_repository.dart';
import '../datasources/plant_analysis_local_datasource.dart';
import '../models/plant_analysis_model.dart';

class PlantAnalysisRepositoryImpl implements PlantAnalysisRepository {
  final PlantAnalysisLocalDataSource localDataSource;

  PlantAnalysisRepositoryImpl({required this.localDataSource});

  @override
  Future<Either<Failure, PlantAnalysisEntity>> classifyImage(File imageFile) async {
    try {
      final result = await localDataSource.classifyImage(imageFile);
      return Right(result);
    } catch (e) {
      return Left(ServerFailure('تعذر تحليل الصورة عبر نموذج الذكاء الاصطناعي: $e'));
    }
  }

  @override
  Future<Either<Failure, PlantAnalysisEntity>> classifyLiveFrame(img.Image frame) async {
    try {
      final result = await localDataSource.classifyLiveFrame(frame);
      return Right(result);
    } catch (e) {
      return Left(ServerFailure('تعذر تحليل إطار الكاميرا المباشر: $e'));
    }
  }

  @override
  Future<Either<Failure, PlantAnalysisEntity>> saveAnalysis(PlantAnalysisEntity analysis) async {
    try {
      final saved = await localDataSource.saveAnalysis(
        PlantAnalysisModel.fromEntity(analysis),
      );
      return Right(saved);
    } catch (e) {
      return Left(CacheFailure('تعذر حفظ نتيجة الفحص محلياً: $e'));
    }
  }

  @override
  Future<Either<Failure, List<PlantAnalysisEntity>>> getHistory() async {
    try {
      final history = await localDataSource.getHistory();
      return Right(history);
    } catch (e) {
      return Left(CacheFailure('تعذر جلب سجل الفحوصات: $e'));
    }
  }
}
