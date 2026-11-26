import 'package:flutter/material.dart';
import '../constants/colors.dart';

class TAppTheme {
  TAppTheme._();

  static const String fontFamily = 'Cairo';

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    fontFamily: fontFamily,
    disabledColor: TColors.grey,
    brightness: Brightness.light,
    primaryColor: TColors.primary,
    scaffoldBackgroundColor: TColors.light,
    colorScheme: const ColorScheme.light(
      primary: TColors.primary,
      secondary: TColors.secondary,
      surface: TColors.white,
      error: TColors.error,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: TColors.textPrimary,
      onError: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      scrolledUnderElevation: 0,
      backgroundColor: TColors.primary,
      surfaceTintColor: Colors.transparent,
      iconTheme: IconThemeData(color: TColors.white, size: 24),
      actionsIconTheme: IconThemeData(color: TColors.white, size: 24),
      titleTextStyle: TextStyle(
        fontSize: 18.0,
        fontWeight: FontWeight.bold,
        color: TColors.white,
        fontFamily: fontFamily,
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 1,
        foregroundColor: TColors.white,
        backgroundColor: TColors.primary,
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
        textStyle: const TextStyle(
          fontSize: 16,
          color: TColors.white,
          fontWeight: FontWeight.bold,
          fontFamily: fontFamily,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    cardTheme: CardThemeData(
      color: TColors.white,
      elevation: 1.5,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: TColors.grey, width: 0.8),
      ),
    ),
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    fontFamily: fontFamily,
    brightness: Brightness.dark,
    primaryColor: TColors.accent,
    scaffoldBackgroundColor: TColors.dark,
    colorScheme: const ColorScheme.dark(
      primary: TColors.accent,
      secondary: TColors.secondary,
      surface: TColors.darkContainer,
      error: TColors.error,
      onPrimary: Colors.black,
      onSecondary: Colors.white,
      onSurface: Colors.white,
      onError: Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: TColors.darkContainer,
      iconTheme: IconThemeData(color: Colors.white),
      titleTextStyle: TextStyle(
        fontSize: 18.0,
        fontWeight: FontWeight.bold,
        color: Colors.white,
        fontFamily: fontFamily,
      ),
    ),
  );
}
