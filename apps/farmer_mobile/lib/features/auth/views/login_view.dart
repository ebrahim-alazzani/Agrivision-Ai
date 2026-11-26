import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_text_field.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../common/widgets/agri_wave_scaffold.dart';
import '../../../routers/routes.dart';
import '../../../theme/agri_colors.dart';
import '../../../theme/agri_theme.dart';
import '../../../utils/constants/app_constants.dart';
import '../controllers/authentication_controller.dart';

class LoginView extends GetView<AuthenticationController> {
  const LoginView({super.key});

  @override
  Widget build(BuildContext context) {
    final themeController = Get.isRegistered<AgriThemeController>()
        ? AgriThemeController.to
        : Get.put(AgriThemeController());

    final isDark = Theme.of(context).brightness == Brightness.dark;

    return AgriWaveScaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            tooltip: 'تبديل المظهر',
            icon: Obx(
              () => Icon(
                themeController.isDarkMode.value ? Iconsax.sun_1 : Iconsax.moon,
                color: AgriColors.amber,
              ),
            ),
            onPressed: () => themeController.toggleTheme(),
          ),
          IconButton(
            tooltip: 'تبديل حركة الأمواج',
            icon: Obx(
              () => Icon(
                themeController.wavesEnabled.value ? Iconsax.activity : Iconsax.stop,
                color: themeController.wavesEnabled.value ? AgriColors.emerald : AgriColors.darkMuted,
              ),
            ),
            onPressed: () => themeController.toggleWaves(),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo with Specular HALVO Glow
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: AgriColors.primaryGradient,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AgriColors.emerald.withValues(alpha: 0.45),
                      blurRadius: 28,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.eco_rounded,
                  size: 50,
                  color: AgriColors.darkBg,
                ),
              ),
              const SizedBox(height: 18),

              // App Name & Subtitle
              Text(
                AppConstants.appNameAr,
                style: TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                  color: isDark ? AgriColors.darkText : AgriColors.lightText,
                  fontFamily: 'Cairo',
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'الذكاء الاصطناعي في خدمة المزارع اليمني',
                style: TextStyle(
                  fontSize: 13,
                  color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                  fontFamily: 'Cairo',
                ),
              ),
              const SizedBox(height: 28),

              // Glass Card Login Form
              HalvoTile(
                flowColors: const [AgriColors.cyan, AgriColors.emerald],
                padding: const EdgeInsets.all(22),
                child: Form(
                  key: controller.loginFormKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'تسجيل الدخول إلى الحقل',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: isDark ? AgriColors.darkText : AgriColors.lightText,
                          fontFamily: 'Cairo',
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 20),

                      // Phone Input
                      AgriTextField(
                        controller: controller.phoneController,
                        label: 'رقم الهاتف',
                        hint: '77X XXX XXX',
                        prefixIcon: Iconsax.mobile,
                        keyboardType: TextInputType.phone,
                        validator: (val) {
                          if (val == null || val.isEmpty) return 'يرجى إدخال رقم الهاتف';
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      // Password Input
                      Obx(
                        () => AgriTextField(
                          controller: controller.passwordController,
                          label: 'كلمة المرور',
                          hint: '••••••••',
                          prefixIcon: Iconsax.lock,
                          obscureText: controller.hidePassword.value,
                          suffixIcon: IconButton(
                            icon: Icon(
                              controller.hidePassword.value ? Iconsax.eye_slash : Iconsax.eye,
                              color: AgriColors.emerald,
                              size: 20,
                            ),
                            onPressed: () => controller.hidePassword.toggle(),
                          ),
                          validator: (val) {
                            if (val == null || val.length < 4) return 'كلمة المرور قصيرة';
                            return null;
                          },
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Submit Button
                      Obx(
                        () => AgriButton(
                          text: 'دخول الحقل الذكي',
                          isLoading: controller.isLoading.value,
                          icon: Iconsax.login,
                          onPressed: () => controller.login(),
                        ),
                      ),
                      const SizedBox(height: 18),

                      // Register Navigation
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'ليس لديك حساب مزارع؟',
                            style: TextStyle(
                              fontSize: 13,
                              color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                              fontFamily: 'Cairo',
                            ),
                          ),
                          TextButton(
                            onPressed: () => Get.toNamed(AppRoutes.register),
                            child: const Text(
                              'أنشئ حساباً جديداً',
                              style: TextStyle(
                                color: AgriColors.emerald,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Cairo',
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
