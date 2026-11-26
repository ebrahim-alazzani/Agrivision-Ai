import 'package:equatable/equatable.dart';

class PlantAnalysisEntity extends Equatable {
  final String id;
  final String? cropId;
  final String imagePath;
  final String cropNameArabic;
  final String diseaseNameArabic;
  final String diseaseNameEnglish;
  final bool isHealthy;
  final double confidence;
  final String severity;
  final String symptoms;
  final List<String> recommendations;
  final String createdAt;

  const PlantAnalysisEntity({
    required this.id,
    this.cropId,
    required this.imagePath,
    required this.cropNameArabic,
    required this.diseaseNameArabic,
    required this.diseaseNameEnglish,
    required this.isHealthy,
    required this.confidence,
    required this.severity,
    required this.symptoms,
    required this.recommendations,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        cropId,
        imagePath,
        cropNameArabic,
        diseaseNameArabic,
        diseaseNameEnglish,
        isHealthy,
        confidence,
        severity,
        symptoms,
        recommendations,
        createdAt,
      ];
}
