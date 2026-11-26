import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../theme/agri_colors.dart';
import '../../theme/agri_theme.dart';

class HalvoWaveScaffold extends StatefulWidget {
  final PreferredSizeWidget? appBar;
  final Widget body;
  final Widget? bottomNavigationBar;
  final Widget? floatingActionButton;
  final bool extendBodyBehindAppBar;
  final bool extendBody;
  final Widget? drawer;

  const HalvoWaveScaffold({
    super.key,
    this.appBar,
    required this.body,
    this.bottomNavigationBar,
    this.floatingActionButton,
    this.extendBodyBehindAppBar = false,
    this.extendBody = false,
    this.drawer,
  });

  @override
  State<HalvoWaveScaffold> createState() => _HalvoWaveScaffoldState();
}

class _HalvoWaveScaffoldState extends State<HalvoWaveScaffold> with SingleTickerProviderStateMixin {
  late final AnimationController _waveController;

  @override
  void initState() {
    super.initState();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void dispose() {
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final themeController = Get.isRegistered<AgriThemeController>()
        ? AgriThemeController.to
        : Get.put(AgriThemeController());

    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      extendBodyBehindAppBar: widget.extendBodyBehindAppBar,
      extendBody: widget.extendBody,
      appBar: widget.appBar,
      drawer: widget.drawer,
      bottomNavigationBar: widget.bottomNavigationBar,
      floatingActionButton: widget.floatingActionButton,
      body: Stack(
        children: [
          // 1. Radial Ambient Background
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: isDark ? AgriColors.darkBg : AgriColors.lightBg,
                gradient: RadialGradient(
                  center: const Alignment(0.4, -0.6),
                  radius: 1.4,
                  colors: isDark
                      ? [
                          AgriColors.emerald.withValues(alpha: 0.12),
                          AgriColors.cyanDeep.withValues(alpha: 0.08),
                          AgriColors.darkBg,
                        ]
                      : [
                          AgriColors.cyan.withValues(alpha: 0.18),
                          AgriColors.emerald.withValues(alpha: 0.10),
                          AgriColors.lightBg,
                        ],
                  stops: const [0.0, 0.45, 1.0],
                ),
              ),
            ),
          ),

          // 2. Ambient Glow Circles (RadialGradient specular highlights)
          Positioned(
            top: -60,
            right: -60,
            child: Container(
              width: 260,
              height: 260,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    (isDark ? AgriColors.emerald : AgriColors.cyan).withValues(alpha: isDark ? 0.15 : 0.22),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 120,
            left: -80,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    (isDark ? AgriColors.cyanDeep : AgriColors.emerald).withValues(alpha: isDark ? 0.12 : 0.18),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),

          // 3. 3-Layer Kinetic Water/Energy Waves
          Obx(() {
            if (!themeController.wavesEnabled.value) return const SizedBox.shrink();
            return Positioned.fill(
              child: AnimatedBuilder(
                animation: _waveController,
                builder: (context, child) {
                  return CustomPaint(
                    painter: _WaterWavePainter(
                      progress: _waveController.value,
                      isDark: isDark,
                    ),
                  );
                },
              ),
            );
          }),

          // 4. Content Body
          SafeArea(
            top: !widget.extendBodyBehindAppBar,
            bottom: !widget.extendBody,
            child: widget.body,
          ),
        ],
      ),
    );
  }
}

class _WaterWavePainter extends CustomPainter {
  final double progress;
  final bool isDark;

  _WaterWavePainter({required this.progress, required this.isDark});

  @override
  void paint(Canvas canvas, Size size) {
    final waveColors = isDark
        ? [
            AgriColors.emerald.withValues(alpha: 0.04),
            AgriColors.cyan.withValues(alpha: 0.05),
            AgriColors.cyanDeep.withValues(alpha: 0.04),
          ]
        : [
            AgriColors.cyan.withValues(alpha: 0.06),
            AgriColors.emerald.withValues(alpha: 0.07),
            AgriColors.cyanDeep.withValues(alpha: 0.05),
          ];

    final heights = [size.height * 0.72, size.height * 0.77, size.height * 0.83];
    final speeds = [1.0, 1.4, 0.7];
    final amplitudes = [16.0, 22.0, 18.0];

    for (int layer = 0; layer < 3; layer++) {
      final paint = Paint()
        ..color = waveColors[layer]
        ..style = PaintingStyle.fill;

      final path = Path();
      final baseHeight = heights[layer];
      final phase = progress * 2 * math.pi * speeds[layer];
      final amplitude = amplitudes[layer];

      path.moveTo(0, size.height);
      path.lineTo(0, baseHeight);

      for (double x = 0; x <= size.width; x += 10) {
        final y = baseHeight + math.sin((x / size.width * 2 * math.pi) + phase) * amplitude;
        path.lineTo(x, y);
      }

      path.lineTo(size.width, size.height);
      path.close();
      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant _WaterWavePainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.isDark != isDark;
  }
}

typedef AgriWaveScaffold = HalvoWaveScaffold;
