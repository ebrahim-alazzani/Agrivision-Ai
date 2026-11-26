import 'package:flutter/material.dart';

class TColors {
  TColors._();

  // App Basic Colors
  static const Color primary = Color(0xFF2E7D32); // Agricultural Green
  static const Color secondary = Color(0xFF8D6E63); // Soil Brown
  static const Color accent = Color(0xFF4CAF50); // Vibrant Green

  // Gradient Colors
  static const Gradient primaryGradient = LinearGradient(
    begin: Alignment(0.0, 0.0),
    end: Alignment(0.707, -0.707),
    colors: [
      Color(0xFF2E7D32),
      Color(0xFF1B5E20),
    ],
  );

  // Text Colors
  static const Color textPrimary = Color(0xFF1A261C);
  static const Color textSecondary = Color(0xFF556658);
  static const Color textWhite = Colors.white;

  // Background Colors
  static const Color light = Color(0xFFF7FAF7);
  static const Color dark = Color(0xFF121813);
  static const Color primaryBackground = Color(0xFFF3F5F7);

  // Surface Colors
  static const Color lightContainer = Color(0xFFF7FAF7);
  static const Color darkContainer = Color(0xFF1E2620);
  static const Color primaryContainer = Color(0xFFE8F5E9);

  // Validation / Status Colors
  static const Color error = Color(0xFFD32F2F);
  static const Color success = Color(0xFF388E3C);
  static const Color warning = Color(0xFFF57F17);
  static const Color info = Color(0xFF0288D1);

  // Agricultural Severity Colors
  static const Color severityCritical = Color(0xFFD32F2F);
  static const Color severityHigh = Color(0xFFE65100);
  static const Color severityModerate = Color(0xFFF57F17);
  static const Color severityMild = Color(0xFFFBC02D);
  static const Color severityHealthy = Color(0xFF388E3C);

  // Neutral Shades
  static const Color black = Color(0xFF232323);
  static const Color darkerGrey = Color(0xFF4F4F4F);
  static const Color darkGrey = Color(0xFF939393);
  static const Color grey = Color(0xFFE0E0E0);
  static const Color softGrey = Color(0xFFF4F4F4);
  static const Color lightGrey = Color(0xFFF9F9F9);
  static const Color white = Color(0xFFFFFFFF);
  static const Color borderPrimary = Color(0xFFD9D9D9);
  static const Color border = Color(0xFFD9D9D9);
  static const Color surface = Color(0xFFFFFFFF);
}

typedef AgriColors = TColors;

