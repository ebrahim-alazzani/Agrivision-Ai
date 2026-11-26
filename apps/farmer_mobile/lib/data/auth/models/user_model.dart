import '../../../domain/auth/entities/user_entity.dart';

class UserModel extends UserEntity {
  const UserModel({
    required super.id,
    required super.fullName,
    required super.phoneNumber,
    super.email,
    super.region,
    super.role = 'farmer',
    super.token,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      fullName: json['full_name'] ?? json['fullName'] ?? '',
      phoneNumber: json['phone_number'] ?? json['phoneNumber'] ?? '',
      email: json['email'],
      region: json['region'],
      role: json['role'] ?? 'farmer',
      token: json['token'] ?? json['access_token'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'full_name': fullName,
        'phone_number': phoneNumber,
        'email': email,
        'region': region,
        'role': role,
        'token': token,
      };
}
