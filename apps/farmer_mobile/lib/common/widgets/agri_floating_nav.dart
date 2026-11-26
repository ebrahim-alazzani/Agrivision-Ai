import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../theme/agri_colors.dart';

class HalvoNavItem {
  final IconData icon;
  final String label;

  const HalvoNavItem({required this.icon, required this.label});
}

class HalvoFloatingBottomNav extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<HalvoNavItem> items;

  const HalvoFloatingBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.fromLTRB(20, 0, 20, 20),
      height: 68,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(
            color: isDark ? Colors.black.withValues(alpha: 0.5) : Colors.black.withValues(alpha: 0.1),
            blurRadius: 30,
            offset: const Offset(0, 10),
          ),
          BoxShadow(
            color: (isDark ? AgriColors.emerald : AgriColors.cyan).withValues(alpha: 0.15),
            blurRadius: 20,
            spreadRadius: -2,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(999),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 28, sigmaY: 28),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10),
            decoration: BoxDecoration(
              color: isDark
                  ? const Color(0xFF10151C).withValues(alpha: 0.82)
                  : Colors.white.withValues(alpha: 0.88),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(
                color: isDark
                    ? Colors.white.withValues(alpha: 0.12)
                    : Colors.white.withValues(alpha: 0.95),
                width: 1.2,
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: List.generate(items.length, (index) {
                final item = items[index];
                final isSelected = index == currentIndex;

                return GestureDetector(
                  onTap: () {
                    HapticFeedback.lightImpact();
                    onTap(index);
                  },
                  behavior: HitTestBehavior.opaque,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 250),
                    curve: Curves.easeOutCubic,
                    padding: EdgeInsets.symmetric(
                      horizontal: isSelected ? 16 : 10,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      gradient: isSelected ? AgriColors.primaryGradient : null,
                      borderRadius: BorderRadius.circular(999),
                      boxShadow: isSelected
                          ? [
                              BoxShadow(
                                color: AgriColors.emerald.withValues(alpha: 0.35),
                                blurRadius: 16,
                                offset: const Offset(0, 4),
                              ),
                            ]
                          : null,
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          item.icon,
                          size: 22,
                          color: isSelected
                              ? AgriColors.darkBg
                              : (isDark ? AgriColors.darkMuted : AgriColors.lightMuted),
                        ),
                        if (isSelected) ...[
                          const SizedBox(width: 8),
                          Text(
                            item.label,
                            style: const TextStyle(
                              color: AgriColors.darkBg,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                              fontFamily: 'Cairo',
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
  }
}

typedef AgriFloatingBottomNav = HalvoFloatingBottomNav;
