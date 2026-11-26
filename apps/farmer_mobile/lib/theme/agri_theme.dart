import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'package:google_fonts/google_fonts.dart';
import 'agri_colors.dart';

class AgriThemeController extends GetxController {
  static AgriThemeController get to => Get.find();

  final _box = GetStorage();
  final _keyTheme = 'isDarkMode';
  final _keyWaves = 'wavesEnabled';

  final isDarkMode = true.obs;
  final wavesEnabled = true.obs;

  @override
  void onInit() {
    super.onInit();
    isDarkMode.value = _box.read<bool>(_keyTheme) ?? true;
    wavesEnabled.value = _box.read<bool>(_keyWaves) ?? true;
  }

  void toggleTheme() {
    isDarkMode.value = !isDarkMode.value;
    _box.write(_keyTheme, isDarkMode.value);
    Get.changeThemeMode(isDarkMode.value ? ThemeMode.dark : ThemeMode.light);
  }

  void setDarkMode(bool val) {
    isDarkMode.value = val;
    _box.write(_keyTheme, val);
    Get.changeThemeMode(val ? ThemeMode.dark : ThemeMode.light);
  }

  void toggleWaves() {
    wavesEnabled.value = !wavesEnabled.value;
    _box.write(_keyWaves, wavesEnabled.value);
  }

  void setWavesEnabled(bool val) {
    wavesEnabled.value = val;
    _box.write(_keyWaves, val);
  }
}

typedef HalvoThemeController = AgriThemeController;

class AgriTheme {
  AgriTheme._();

  static ThemeData get darkTheme {
    final base = ThemeData.dark(useMaterial3: true);
    final cairoTextTheme = GoogleFonts.cairoTextTheme(base.textTheme).apply(
      bodyColor: AgriColors.darkText,
      displayColor: AgriColors.darkText,
    );

    return base.copyWith(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AgriColors.darkBg,
      primaryColor: AgriColors.emerald,
      textTheme: cairoTextTheme,
      colorScheme: const ColorScheme.dark(
        primary: AgriColors.emerald,
        secondary: AgriColors.cyan,
        surface: AgriColors.darkSurface,
        error: AgriColors.rose,
        onPrimary: AgriColors.darkBg,
        onSecondary: AgriColors.darkBg,
        onSurface: AgriColors.darkText,
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        backgroundColor: Colors.transparent,
        centerTitle: true,
        titleTextStyle: GoogleFonts.cairo(
          color: AgriColors.darkText,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
        iconTheme: const IconThemeData(color: AgriColors.darkText),
      ),
    );
  }

  static ThemeData get lightTheme {
    final base = ThemeData.light(useMaterial3: true);
    final cairoTextTheme = GoogleFonts.cairoTextTheme(base.textTheme).apply(
      bodyColor: AgriColors.lightText,
      displayColor: AgriColors.lightText,
    );

    return base.copyWith(
      brightness: Brightness.light,
      scaffoldBackgroundColor: AgriColors.lightBg,
      primaryColor: AgriColors.emerald,
      textTheme: cairoTextTheme,
      colorScheme: const ColorScheme.light(
        primary: AgriColors.emerald,
        secondary: AgriColors.cyanDeep,
        surface: AgriColors.lightSurface,
        error: AgriColors.rose,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: AgriColors.lightText,
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        backgroundColor: Colors.transparent,
        centerTitle: true,
        titleTextStyle: GoogleFonts.cairo(
          color: AgriColors.lightText,
          fontSize: 18,
          fontWeight: FontWeight.w800,
        ),
        iconTheme: const IconThemeData(color: AgriColors.lightText),
      ),
    );
  }
}
