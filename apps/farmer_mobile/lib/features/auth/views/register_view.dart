import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../common/widgets/agri_text_field.dart';
import '../../../utils/constants/app_constants.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/authentication_controller.dart';

class RegisterView extends GetView<AuthenticationController> {
  const RegisterView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تسجيل حساب مزارع جديد'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: controller.registerFormKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AgriCard(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    AgriTextField(
                      controller: controller.nameController,
                      label: 'الاسم الكامل للمزارع',
                      hint: 'مثال: أحمد عبد الله اليافعي',
                      prefixIcon: Iconsax.user,
                      validator: (val) {
                        if (val == null || val.isEmpty) return 'يرجى إدخال الاسم';
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
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
                    const Text(
                      'المنطقة أو المحافظة الزراعية',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: TColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Obx(
                      () => DropdownButtonFormField<String>(
                        value: controller.selectedRegion.value,
                        decoration: InputDecoration(
                          prefixIcon: const Icon(Iconsax.location, color: TColors.primary),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        items: AppConstants.yemenRegions.map((region) {
                          return DropdownMenuItem<String>(
                            value: region['nameAr'],
                            child: Text(region['nameAr'] ?? ''),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) controller.selectedRegion.value = val;
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    AgriTextField(
                      controller: controller.passwordController,
                      label: 'كلمة المرور',
                      hint: '••••••••',
                      prefixIcon: Iconsax.lock,
                      obscureText: true,
                      validator: (val) {
                        if (val == null || val.length < 4) return 'كلمة المرور قصيرة';
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    Obx(
                      () => AgriButton(
                        text: 'إنشاء الحساب والبدء',
                        icon: Iconsax.tick_circle,
                        isLoading: controller.isLoading.value,
                        onPressed: () => controller.register(),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
