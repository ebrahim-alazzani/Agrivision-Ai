import 'dart:io';
import 'package:dartz/dartz.dart';
import 'package:image/image.dart' as img;
import '../../../core/error/failures.dart';
import '../entities/plant_analysis_entity.dart';

abstract class PlantAnalysisRepository {
  Future<Either<Failure, PlantAnalysisEntity>> classifyImage(File imageFile);
  Future<Either<Failure, PlantAnalysisEntity>> classifyLiveFrame(img.Image frame);
  Future<Either<Failure, PlantAnalysisEntity>> saveAnalysis(PlantAnalysisEntity analysis);
  Future<Either<Failure, List<PlantAnalysisEntity>>> getHistory();
}
