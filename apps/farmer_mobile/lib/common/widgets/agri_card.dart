import 'package:flutter/material.dart';
import 'agri_tile.dart';

/// بطاقة زجاجية عاكسة متوافقة مع AgriCard وتطبق نظام HALVO Glassmorphism
class AgriCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;
  final VoidCallback? onTap;
  final Color? backgroundColor;
  final Color? color;
  final Color? borderColor;
  final double borderRadius;
  final double elevation;
  final bool showFlowLine;

  const AgriCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.margin = const EdgeInsets.symmetric(vertical: 6, horizontal: 0),
    this.onTap,
    this.backgroundColor,
    this.color,
    this.borderColor,
    this.borderRadius = 20,
    this.elevation = 0,
    this.showFlowLine = false,
  });

  @override
  Widget build(BuildContext context) {
    return AgriTile(
      margin: margin,
      padding: padding,
      borderRadius: borderRadius,
      customBorderColor: borderColor,
      onTap: onTap,
      showFlowLine: showFlowLine,
      child: child,
    );
  }
}
