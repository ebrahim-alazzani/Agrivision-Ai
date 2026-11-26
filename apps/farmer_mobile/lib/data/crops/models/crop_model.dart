import '../../../domain/crops/entities/crop_entity.dart';

class CropModel extends CropEntity {
  const CropModel({
    required super.id,
    required super.farmId,
    required super.name,
    required super.cropType,
    required super.plantingDate,
    required super.status,
  });

  factory CropModel.fromMap(Map<String, dynamic> map) {
    return CropModel(
      id: map['id']?.toString() ?? '',
      farmId: map['farm_id']?.toString() ?? '',
      name: map['name']?.toString() ?? '',
      cropType: map['crop_type']?.toString() ?? '',
      plantingDate: map['planting_date']?.toString() ?? '',
      status: map['status']?.toString() ?? '',
    );
  }

  factory CropModel.fromEntity(CropEntity entity) {
    return CropModel(
      id: entity.id,
      farmId: entity.farmId,
      name: entity.name,
      cropType: entity.cropType,
      plantingDate: entity.plantingDate,
      status: entity.status,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'farm_id': farmId,
      'name': name,
      'crop_type': cropType,
      'planting_date': plantingDate,
      'status': status,
      'is_synced': 0,
    };
  }
}
