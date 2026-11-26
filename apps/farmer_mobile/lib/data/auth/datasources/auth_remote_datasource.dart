import '../../../core/network/api_service.dart';
import '../../../utils/constants/api_constants.dart';
import '../models/user_model.dart';

abstract class AuthRemoteDataSource {
  Future<UserModel> login(String phoneNumber, String password);
  Future<UserModel> register({
    required String fullName,
    required String phoneNumber,
    required String password,
    required String region,
  });
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final ApiService apiService;
  AuthRemoteDataSourceImpl(this.apiService);

  @override
  Future<UserModel> login(String phoneNumber, String password) async {
    final response = await apiService.post(
      ApiConstants.login,
      data: {
        'phone_number': phoneNumber,
        'password': password,
      },
    );
    return UserModel.fromJson(response);
  }

  @override
  Future<UserModel> register({
    required String fullName,
    required String phoneNumber,
    required String password,
    required String region,
  }) async {
    final response = await apiService.post(
      ApiConstants.register,
      data: {
        'full_name': fullName,
        'phone_number': phoneNumber,
        'password': password,
        'region': region,
        'role': 'farmer',
      },
    );
    return UserModel.fromJson(response);
  }
}
