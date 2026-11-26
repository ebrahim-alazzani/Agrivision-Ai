import 'dart:convert';
import '../../../domain/plant_analysis/entities/plant_analysis_entity.dart';

class PlantAnalysisModel extends PlantAnalysisEntity {
  const PlantAnalysisModel({
    required super.id,
    super.cropId,
    required super.imagePath,
    required super.cropNameArabic,
    required super.diseaseNameArabic,
    required super.diseaseNameEnglish,
    required super.isHealthy,
    required super.confidence,
    required super.severity,
    required super.symptoms,
    required super.recommendations,
    required super.createdAt,
  });

  factory PlantAnalysisModel.fromMap(Map<String, dynamic> map) {
    final rawRecs = map['recommendations_ar']?.toString() ?? '[]';
    List<String> parsedRecs = [];
    try {
      parsedRecs = List<String>.from(json.decode(rawRecs) as List);
    } catch (_) {
      if (rawRecs.isNotEmpty) parsedRecs = [rawRecs];
    }

    final diseaseEn = map['disease_name_en']?.toString() ?? '';
    return PlantAnalysisModel(
      id: map['id']?.toString() ?? '',
      cropId: map['crop_id']?.toString(),
      imagePath: map['image_path']?.toString() ?? '',
      cropNameArabic: diseaseEn.split('___').first,
      diseaseNameArabic: map['disease_name_ar']?.toString() ?? '',
      diseaseNameEnglish: diseaseEn,
      isHealthy: diseaseEn.toLowerCase().endsWith('healthy') ||
          (map['severity']?.toString().toLowerCase() == 'healthy'),
      confidence: (map['confidence'] as num?)?.toDouble() ?? 0.0,
      severity: map['severity']?.toString() ?? 'healthy',
      symptoms: map['symptoms_ar']?.toString() ?? '',
      recommendations: parsedRecs,
      createdAt: map['created_at']?.toString() ?? '',
    );
  }

  factory PlantAnalysisModel.fromEntity(PlantAnalysisEntity entity) {
    return PlantAnalysisModel(
      id: entity.id,
      cropId: entity.cropId,
      imagePath: entity.imagePath,
      cropNameArabic: entity.cropNameArabic,
      diseaseNameArabic: entity.diseaseNameArabic,
      diseaseNameEnglish: entity.diseaseNameEnglish,
      isHealthy: entity.isHealthy,
      confidence: entity.confidence,
      severity: entity.severity,
      symptoms: entity.symptoms,
      recommendations: entity.recommendations,
      createdAt: entity.createdAt,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'crop_id': cropId,
      'image_path': imagePath,
      'disease_name_ar': diseaseNameArabic,
      'disease_name_en': diseaseNameEnglish,
      'confidence': confidence,
      'severity': severity,
      'symptoms_ar': symptoms,
      'recommendations_ar': json.encode(recommendations),
      'created_at': createdAt,
      'is_synced': 0,
    };
  }
}
