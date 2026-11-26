import 'dart:io';
import 'package:image/image.dart' as img;
import 'package:uuid/uuid.dart';
import '../../../core/services/plant_disease_classifier_service.dart';
import '../../../core/storage/database_helper.dart';
import '../models/plant_analysis_model.dart';

abstract class PlantAnalysisLocalDataSource {
  Future<PlantAnalysisModel> classifyImage(File imageFile);
  Future<PlantAnalysisModel> classifyLiveFrame(img.Image frame);
  Future<PlantAnalysisModel> saveAnalysis(PlantAnalysisModel model);
  Future<List<PlantAnalysisModel>> getHistory();
}

class PlantAnalysisLocalDataSourceImpl implements PlantAnalysisLocalDataSource {
  final PlantDiseaseClassifierService classifierService;

  PlantAnalysisLocalDataSourceImpl({required this.classifierService});

  PlantAnalysisModel _mapDiagnosis(PlantDiagnosisResult res, String imagePath) {
    return PlantAnalysisModel(
      id: const Uuid().v4(),
      imagePath: imagePath,
      cropNameArabic: res.cropNameArabic,
      diseaseNameArabic: res.diseaseNameArabic,
      diseaseNameEnglish: res.rawClassName,
      isHealthy: res.isHealthy,
      confidence: res.confidence,
      severity: res.severity,
      symptoms: res.symptoms,
      recommendations: res.recommendations,
      createdAt: DateTime.now().toIso8601String(),
    );
  }

  @override
  Future<PlantAnalysisModel> classifyImage(File imageFile) async {
    final result = await classifierService.classifyImage(imageFile);
    return _mapDiagnosis(result, imageFile.path);
  }

  @override
  Future<PlantAnalysisModel> classifyLiveFrame(img.Image frame) async {
    final result = await classifierService.classifyRgbImage(frame);
    return _mapDiagnosis(result, 'live_camera_frame');
  }

  @override
  Future<PlantAnalysisModel> saveAnalysis(PlantAnalysisModel model) async {
    await DatabaseHelper.insert('plant_analyses', model.toMap());
    return model;
  }

  @override
  Future<List<PlantAnalysisModel>> getHistory() async {
    final rows = await DatabaseHelper.query('plant_analyses');
    return rows.map((row) => PlantAnalysisModel.fromMap(row)).toList();
  }
}
