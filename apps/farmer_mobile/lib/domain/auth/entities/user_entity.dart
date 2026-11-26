import 'package:equatable/equatable.dart';

class UserEntity extends Equatable {
  final String id;
  final String fullName;
  final String phoneNumber;
  final String? email;
  final String? region;
  final String role;
  final String? token;

  const UserEntity({
    required this.id,
    required this.fullName,
    required this.phoneNumber,
    this.email,
    this.region,
    this.role = 'farmer',
    this.token,
  });

  @override
  List<Object?> get props => [id, fullName, phoneNumber, email, region, role, token];
}
