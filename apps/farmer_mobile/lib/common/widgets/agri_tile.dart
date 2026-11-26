import 'dart:ui';
import 'package:flutter/material.dart';
import '../../theme/agri_colors.dart';

class AgriFlowLine extends StatefulWidget {
  final List<Color> colors;
  final double height;
  final double borderRadius;

  const AgriFlowLine({
    super.key,
    this.colors = const [AgriColors.cyan, AgriColors.emerald, AgriColors.blue],
    this.height = 2.5,
    this.borderRadius = 20,
  });

  @override
  State<AgriFlowLine> createState() => _AgriFlowLineState();
}

class _AgriFlowLineState extends State<AgriFlowLine>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) {
        final shift = _controller.value * 2 - 1;
        return Container(
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.vertical(
              top: Radius.circular(widget.borderRadius),
            ),
            gradient: LinearGradient(
              begin: Alignment(-1.5 + shift * 2, 0),
              end: Alignment(0.5 + shift * 2, 0),
              colors: [
                Colors.transparent,
                ...widget.colors.map((c) => c.withValues(alpha: 0.85)),
                Colors.transparent,
              ],
            ),
          ),
        );
      },
    );
  }
}

class HalvoTile extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;
  final VoidCallback? onTap;
  final double borderRadius;
  final bool showFlowLine;
  final List<Color>? flowColors;
  final Color? customBorderColor;
  final Color? glowColor;

  const HalvoTile({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.margin = const EdgeInsets.symmetric(vertical: 6),
    this.onTap,
    this.borderRadius = 20,
    this.showFlowLine = true,
    this.flowColors,
    this.customBorderColor,
    this.glowColor,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final effectiveGlow = glowColor ??
        (isDark
            ? AgriColors.emerald.withValues(alpha: 0.12)
            : AgriColors.cyan.withValues(alpha: 0.10));

    return Container(
      margin: margin,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: [
          BoxShadow(
            color: isDark
                ? Colors.black.withValues(alpha: 0.40)
                : const Color(0xFF0F172A).withValues(alpha: 0.06),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
          BoxShadow(
            color: effectiveGlow,
            blurRadius: 18,
            spreadRadius: -4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: isDark
                    ? [
                        Colors.white.withValues(alpha: 0.09),
                        AgriColors.darkSurface.withValues(alpha: 0.72),
                        Colors.white.withValues(alpha: 0.03),
                      ]
                    : [
                        Colors.white.withValues(alpha: 0.92),
                        Colors.white.withValues(alpha: 0.76),
                      ],
              ),
              borderRadius: BorderRadius.circular(borderRadius),
              border: Border.all(
                color: customBorderColor ??
                    (isDark
                        ? Colors.white.withValues(alpha: 0.14)
                        : Colors.white.withValues(alpha: 0.95)),
                width: 1.15,
              ),
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onTap,
                borderRadius: BorderRadius.circular(borderRadius),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (showFlowLine)
                      AgriFlowLine(
                        colors: flowColors ??
                            const [AgriColors.cyan, AgriColors.emerald],
                        borderRadius: borderRadius,
                      ),
                    Padding(
                      padding: padding,
                      child: child,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

typedef AgriTile = HalvoTile;
