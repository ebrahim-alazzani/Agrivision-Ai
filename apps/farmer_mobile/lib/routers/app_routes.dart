import 'package:get/get.dart';
import '../bindings/auth_binding.dart';
import '../bindings/dashboard_binding.dart';
import '../bindings/plant_analysis_binding.dart';
import '../features/auth/views/login_view.dart';
import '../features/auth/views/register_view.dart';
import '../features/crops/controllers/crops_controller.dart';
import '../features/crops/views/crops_view.dart';
import '../features/dashboard/views/dashboard_view.dart';
import '../features/farms/controllers/farms_controller.dart';
import '../features/farms/views/farms_view.dart';
import '../features/monitoring/controllers/monitoring_controller.dart';
import '../features/monitoring/views/monitoring_view.dart';
import '../features/notifications/controllers/notifications_controller.dart';
import '../features/notifications/views/notifications_view.dart';
import '../features/pest_analysis/controllers/pest_analysis_controller.dart';
import '../features/pest_analysis/views/pest_analysis_view.dart';
import '../features/pesticides/controllers/pesticide_controller.dart';
import '../features/pesticides/views/pesticide_calculator_view.dart';
import '../features/plant_analysis/views/plant_analysis_view.dart';
import '../features/plant_analysis/views/plant_result_view.dart';
import '../features/weather/controllers/weather_controller.dart';
import '../features/weather/views/weather_view.dart';
import 'routes.dart';

class AppPages {
  AppPages._();

  static const initial = AppRoutes.dashboard;

  static final routes = [
    GetPage(
      name: AppRoutes.login,
      page: () => const LoginView(),
      binding: AuthBinding(),
    ),
    GetPage(
      name: AppRoutes.register,
      page: () => const RegisterView(),
      binding: AuthBinding(),
    ),
    GetPage(
      name: AppRoutes.dashboard,
      page: () => const DashboardView(),
      binding: DashboardBinding(),
    ),
    GetPage(
      name: AppRoutes.plantAnalysis,
      page: () => const PlantAnalysisView(),
      binding: PlantAnalysisBinding(),
    ),
    GetPage(
      name: AppRoutes.plantResult,
      page: () => const PlantResultView(),
      binding: PlantAnalysisBinding(),
    ),
    GetPage(
      name: AppRoutes.weather,
      page: () => const WeatherView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(() => WeatherController(), fenix: true);
      }),
    ),
    GetPage(
      name: AppRoutes.dosageCalculator,
      page: () => const PesticideCalculatorView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(() => PesticideController(), fenix: true);
      }),
    ),
    GetPage(
      name: AppRoutes.farms,
      page: () => const FarmsView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(
          () => FarmsController(
            getFarmsUseCase: Get.find(),
            addFarmUseCase: Get.find(),
            deleteFarmUseCase: Get.find(),
          ),
          fenix: true,
        );
      }),
    ),
    GetPage(
      name: AppRoutes.crops,
      page: () => const CropsView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(
          () => CropsController(
            getCropsUseCase: Get.find(),
            addCropUseCase: Get.find(),
            deleteCropUseCase: Get.find(),
          ),
          fenix: true,
        );
      }),
    ),
    GetPage(
      name: AppRoutes.pestAnalysis,
      page: () => const PestAnalysisView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(() => PestAnalysisController(), fenix: true);
      }),
    ),
    GetPage(
      name: AppRoutes.monitoring,
      page: () => const MonitoringView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(() => MonitoringController(), fenix: true);
      }),
    ),
    GetPage(
      name: AppRoutes.notifications,
      page: () => const NotificationsView(),
      binding: BindingsBuilder(() {
        Get.lazyPut(() => NotificationsController(), fenix: true);
      }),
    ),
  ];
}
