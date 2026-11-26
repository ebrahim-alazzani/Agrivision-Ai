import 'package:flutter/material.dart';

class AgriColors {
  AgriColors._();

  // HALVO Agricultural Primary & Accent Colors
  static const Color emerald = Color(0xFF77D6A0); // Primary Agricultural Emerald Green
  static const Color cyan = Color(0xFF5FD8C4); // Specular Mint / Cyan
  static const Color cyanDeep = Color(0xFF0EA5E9); // Deep Cyan Water
  static const Color amber = Color(0xFFF2AE4B); // Solar / Pesticide Alert Amber
  static const Color blue = Color(0xFF38BDF8); // Irrigation Blue
  static const Color purple = Color(0xFFA855F7); // Advanced AI Purple
  static const Color rose = Color(0xFFF43F5E); // Critical Disease Alert Rose

  // Dark Obsidian Mode
  static const Color darkBg = Color(0xFF0B0F15);
  static const Color darkSurface = Color(0xFF10151C);
  static const Color darkSurfaceAlt = Color(0xFF12171F);
  static const Color darkText = Color(0xFFF1EFEA);
  static const Color darkMuted = Color(0xFF94A3B8);

  // Light Crisp Pearl Mode
  static const Color lightBg = Color(0xFFF4F7FB);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightText = Color(0xFF0F172A);
  static const Color lightMuted = Color(0xFF64748B);

  // Convenience & backward compatibility aliases
  static const Color primary = emerald;
  static const Color secondary = cyan;
  static const Color accent = cyan;
  static const Color warning = amber;
  static const Color error = rose;
  static const Color info = blue;
  static const Color textPrimary = darkText;
  static const Color textSecondary = darkMuted;

  // Agricultural Diagnostic Severity
  static const Color severityHealthy = emerald;
  static const Color severityMild = Color(0xFFFBC02D);
  static const Color severityModerate = amber;
  static const Color severityHigh = Color(0xFFE65100);
  static const Color severityCritical = rose;

  // Glassmorphism Token Colors
  static Color glassBg(bool isDark) => isDark
      ? darkSurface.withValues(alpha: 0.76)
      : lightSurface.withValues(alpha: 0.84);

  static Color glassBorder(bool isDark) => isDark
      ? Colors.white.withValues(alpha: 0.10)
      : Colors.white.withValues(alpha: 0.92);

  static Color glassGlow(bool isDark) => isDark
      ? emerald.withValues(alpha: 0.25)
      : cyan.withValues(alpha: 0.20);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [cyan, emerald],
  );

  static const LinearGradient energyGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [emerald, cyanDeep],
  );

  static const LinearGradient alertGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [amber, rose],
  );

  static const LinearGradient skyGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [cyanDeep, blue],
  );
}

typedef HalvoColors = AgriColors;
