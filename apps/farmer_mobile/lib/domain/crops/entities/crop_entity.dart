import 'package:equatable/equatable.dart';

class CropEntity extends Equatable {
  final String id;
  final String farmId;
  final String name;
  final String cropType;
  final String plantingDate;
  final String status;

  const CropEntity({
    required this.id,
    required this.farmId,
    required this.name,
    required this.cropType,
    required this.plantingDate,
    required this.status,
  });

  @override
  List<Object?> get props => [id, farmId, name, cropType, plantingDate, status];
}
