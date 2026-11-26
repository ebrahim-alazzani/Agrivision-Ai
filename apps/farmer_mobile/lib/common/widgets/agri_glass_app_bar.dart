import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../theme/agri_colors.dart';
import 'agri_tile.dart';

/// شريط عنوان زجاجي موحد بنمط HALVO
class AgriGlassAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final String? subtitle;
  final IconData leadingIcon;
  final List<Widget>? actions;
  final bool showBack;

  const AgriGlassAppBar({
    super.key,
    required this.title,
    this.subtitle,
    this.leadingIcon = Icons.eco_rounded,
    this.actions,
    this.showBack = false,
  });

  @override
  Size get preferredSize => const Size.fromHeight(88);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
        child: AgriTile(
          borderRadius: 18,
          showFlowLine: false,
          margin: EdgeInsets.zero,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: Row(
            children: [
              if (showBack)
                IconButton(
                  onPressed: () => Get.back(),
                  icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
                  tooltip: 'رجوع',
                )
              else
                Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    gradient: AgriColors.primaryGradient,
                    boxShadow: [
                      BoxShadow(
                        color: AgriColors.emerald.withValues(alpha: 0.30),
                        blurRadius: 12,
                      ),
                    ],
                  ),
                  child: Icon(leadingIcon, color: AgriColors.darkBg, size: 20),
                ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: isDark ? Colors.white : AgriColors.lightText,
                      ),
                    ),
                    if (subtitle != null && subtitle!.isNotEmpty)
                      Text(
                        subtitle!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: AgriColors.emerald,
                        ),
                      ),
                  ],
                ),
              ),
              if (actions != null) ...actions!,
            ],
          ),
        ),
      ),
    );
  }
}
