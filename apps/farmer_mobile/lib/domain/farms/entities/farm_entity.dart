import 'package:equatable/equatable.dart';

class FarmEntity extends Equatable {
  final String id;
  final String name;
  final String region;
  final double area;
  final double? latitude;
  final double? longitude;
  final String createdAt;

  const FarmEntity({
    required this.id,
    required this.name,
    required this.region,
    required this.area,
    this.latitude,
    this.longitude,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [id, name, region, area, latitude, longitude, createdAt];
}
