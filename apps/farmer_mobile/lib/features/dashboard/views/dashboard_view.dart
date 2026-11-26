import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_floating_nav.dart';
import '../../../common/widgets/agri_glass_app_bar.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../routers/routes.dart';
import '../../../theme/agri_colors.dart';
import '../../../theme/agri_theme.dart';
import '../controllers/dashboard_controller.dart';
import '../widgets/dashboard_header_card.dart';
import '../widgets/dashboard_quick_scan_card.dart';
import '../widgets/dashboard_stats_grid.dart';
import '../widgets/dashboard_tools_section.dart';

class DashboardView extends GetView<DashboardController> {
  const DashboardView({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.isRegistered<AgriThemeController>()
        ? AgriThemeController.to
        : Get.put(AgriThemeController());

    return AgriWaveScaffold(
      extendBody: true,
      appBar: AgriGlassAppBar(
        title: 'رؤية زراعية',
        subtitle: 'تشخيص أمراض النبات محلياً',
        actions: [
          IconButton(
            tooltip: 'تحديث البيانات',
            icon: const Icon(Iconsax.refresh, size: 20),
            onPressed: () => controller.refreshDashboard(),
          ),
          IconButton(
            tooltip: 'تبديل الأمواج',
            icon: Obx(
              () => Icon(
                themeController.wavesEnabled.value ? Iconsax.activity : Iconsax.stop,
                size: 20,
                color: themeController.wavesEnabled.value
                    ? AgriColors.emerald
                    : AgriColors.darkMuted,
              ),
            ),
            onPressed: () => themeController.toggleWaves(),
          ),
          IconButton(
            tooltip: 'تبديل المظهر',
            icon: Obx(
              () => Icon(
                themeController.isDarkMode.value ? Iconsax.sun_1 : Iconsax.moon,
                size: 20,
                color: AgriColors.amber,
              ),
            ),
            onPressed: () => themeController.toggleTheme(),
          ),
        ],
      ),
      bottomNavigationBar: Obx(
        () => AgriFloatingBottomNav(
          currentIndex: controller.selectedIndex.value,
          onTap: (index) {
            controller.changePage(index);
            if (index == 1) {
              Get.toNamed(AppRoutes.plantAnalysis);
            } else if (index == 2) {
              Get.toNamed(AppRoutes.weather);
            } else if (index == 3) {
              Get.toNamed(AppRoutes.farms);
            }
          },
          items: const [
            HalvoNavItem(icon: Iconsax.home_2, label: 'الرئيسية'),
            HalvoNavItem(icon: Iconsax.scan, label: 'فحص'),
            HalvoNavItem(icon: Iconsax.cloud_sunny, label: 'الطقس'),
            HalvoNavItem(icon: Iconsax.tree, label: 'مزارعي'),
          ],
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => controller.refreshDashboard(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Obx(
                () => DashboardHeaderCard(
                  farmsCount: controller.farmsCount.value,
                  analysesCount: controller.analysesCount.value,
                ),
              ),
              const SizedBox(height: 10),
              const DashboardQuickScanCard(),
              const SizedBox(height: 16),
              const Text(
                'إحصائيات المزرعة الفعلية',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 10),
              Obx(
                () => DashboardStatsGrid(
                  farmsCount: controller.farmsCount.value,
                  totalArea: controller.totalArea.value,
                  cropsCount: controller.cropsCount.value,
                  analysesCount: controller.analysesCount.value,
                  healthyPercentage: controller.healthyPercentage.value,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'الأدوات الزراعية',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
              const DashboardToolsSection(),
            ],
          ),
        ),
      ),
    );
  }
}
