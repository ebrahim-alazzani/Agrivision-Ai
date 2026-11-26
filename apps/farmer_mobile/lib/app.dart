import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:get/get.dart';
import 'bindings/general_bindings.dart';
import 'routers/app_routes.dart';
import 'theme/agri_theme.dart';

class AgriVisionApp extends StatelessWidget {
  const AgriVisionApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.isRegistered<AgriThemeController>()
        ? AgriThemeController.to
        : Get.put<AgriThemeController>(AgriThemeController(), permanent: true);

    return Obx(
      () => GetMaterialApp(
        title: 'AgriVision AI - المراقب الزراعي',
        debugShowCheckedModeBanner: false,
        themeMode: themeController.isDarkMode.value ? ThemeMode.dark : ThemeMode.light,
        theme: AgriTheme.lightTheme,
        darkTheme: AgriTheme.darkTheme,

        initialRoute: AppPages.initial,
        getPages: AppPages.routes,
        initialBinding: GeneralBindings(),

        // اللغة الافتراضية العربية والاتجاه من اليمين لليسار (RTL)
        locale: const Locale('ar', 'YE'),
        fallbackLocale: const Locale('ar', 'SA'),
        supportedLocales: const [
          Locale('ar', 'YE'),
          Locale('ar', 'SA'),
          Locale('en', 'US'),
        ],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],

        builder: (context, child) {
          return Directionality(
            textDirection: TextDirection.rtl,
            child: child ?? const SizedBox.shrink(),
          );
        },
      ),
    );
  }
}
