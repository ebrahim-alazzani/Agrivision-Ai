import '../../../domain/farms/entities/farm_entity.dart';

class FarmModel extends FarmEntity {
  const FarmModel({
    required super.id,
    required super.name,
    required super.region,
    required super.area,
    super.latitude,
    super.longitude,
    required super.createdAt,
  });

  factory FarmModel.fromMap(Map<String, dynamic> map) {
    return FarmModel(
      id: map['id']?.toString() ?? '',
      name: map['name']?.toString() ?? '',
      region: map['region']?.toString() ?? '',
      area: (map['area'] as num?)?.toDouble() ?? 0.0,
      latitude: (map['latitude'] as num?)?.toDouble(),
      longitude: (map['longitude'] as num?)?.toDouble(),
      createdAt: map['created_at']?.toString() ?? '',
    );
  }

  factory FarmModel.fromEntity(FarmEntity entity) {
    return FarmModel(
      id: entity.id,
      name: entity.name,
      region: entity.region,
      area: entity.area,
      latitude: entity.latitude,
      longitude: entity.longitude,
      createdAt: entity.createdAt,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'region': region,
      'area': area,
      'latitude': latitude,
      'longitude': longitude,
      'created_at': createdAt,
      'is_synced': 0,
    };
  }
}
