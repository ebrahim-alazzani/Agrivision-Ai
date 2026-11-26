import 'package:get_storage/get_storage.dart';

class GetStorageHelper {
  static final GetStorage _box = GetStorage();

  static const String tokenKey = 'auth_token';
  static const String userKey = 'cached_user';
  static const String localeKey = 'app_locale';
  static const String themeKey = 'app_theme';

  static Future<void> init() async {
    await GetStorage.init();
  }

  static Future<void> write(String key, dynamic value) async {
    await _box.write(key, value);
  }

  static T? read<T>(String key) {
    return _box.read<T>(key);
  }

  static bool hasData(String key) {
    return _box.hasData(key);
  }

  static Future<void> remove(String key) async {
    await _box.remove(key);
  }

  static Future<void> erase() async {
    await _box.erase();
  }
}
