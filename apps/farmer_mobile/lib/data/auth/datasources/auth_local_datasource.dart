import 'dart:convert';
import '../../../core/storage/get_storage_helper.dart';
import '../models/user_model.dart';

abstract class AuthLocalDataSource {
  Future<void> cacheUser(UserModel user);
  Future<UserModel?> getCachedUser();
  Future<void> clearUser();
}

class AuthLocalDataSourceImpl implements AuthLocalDataSource {
  @override
  Future<void> cacheUser(UserModel user) async {
    if (user.token != null) {
      await GetStorageHelper.write(GetStorageHelper.tokenKey, user.token!);
    }
    await GetStorageHelper.write(GetStorageHelper.userKey, jsonEncode(user.toJson()));
  }

  @override
  Future<UserModel?> getCachedUser() async {
    final jsonStr = GetStorageHelper.read<String>(GetStorageHelper.userKey);
    if (jsonStr == null) return null;
    return UserModel.fromJson(jsonDecode(jsonStr));
  }

  @override
  Future<void> clearUser() async {
    await GetStorageHelper.remove(GetStorageHelper.tokenKey);
    await GetStorageHelper.remove(GetStorageHelper.userKey);
  }
}
