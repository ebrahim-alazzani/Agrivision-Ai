import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_card.dart';
import '../../../common/widgets/agri_text_field.dart';
import '../../../utils/constants/colors.dart';
import '../controllers/pesticide_controller.dart';

class PesticideCalculatorView extends GetView<PesticideController> {
  const PesticideCalculatorView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('حاسبة المبيدات وفترة الأمان'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Product Info Card
            AgriCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('بيانات المبيد المسجل',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    const SizedBox(height: 8),
                    AgriTextField(
                      controller: controller.productNameController,
                      label: 'اسم المنتج التجاري',
                      prefixIcon: Iconsax.box,
                      readOnly: true,
                    ),
                    const SizedBox(height: 8),
                    Obx(() => Text(
                          'المادة الفعالة: ${controller.activeIngredient.value}',
                          style: const TextStyle(color: AgriColors.textSecondary, fontSize: 11),
                        )),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Calculation inputs
            AgriCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('معطيات الرش',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    const SizedBox(height: 12),
                    AgriTextField(
                      controller: controller.waterVolumeController,
                      label: 'حجم الماء المطلوب للرش (لتر)',
                      prefixIcon: Iconsax.drop,
                      keyboardType: TextInputType.number,
                      onChanged: (_) => controller.calculate(),
                    ),
                    const SizedBox(height: 12),
                    AgriTextField(
                      controller: controller.areaController,
                      label: 'المساحة المراد معالجتها (م² أو قصبة)',
                      prefixIcon: Iconsax.grid_1,
                      keyboardType: TextInputType.number,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Results Card
            AgriCard(
              color: AgriColors.primary.withOpacity(0.05),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text('الكمية الموصى بها وفق ملصق الشركة المسجل',
                        style: TextStyle(color: AgriColors.textSecondary, fontSize: 12)),
                    const SizedBox(height: 8),
                    Obx(() => Text(
                          '${controller.calculatedDose.value.toStringAsFixed(1)} غرام / مل',
                          style: const TextStyle(
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                            color: AgriColors.primary,
                          ),
                        )),
                    const SizedBox(height: 12),
                    Divider(color: AgriColors.border),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        Column(
                          children: [
                            const Text('فترة ما قبل الحصاد (PHI)',
                                style: TextStyle(color: AgriColors.textSecondary, fontSize: 11)),
                            const SizedBox(height: 4),
                            Obx(() => Text('${controller.phiDays.value} أيام',
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 14,
                                    color: AgriColors.error))),
                          ],
                        ),
                        Column(
                          children: [
                            const Text('فترة إعادة الدخول (REI)',
                                style: TextStyle(color: AgriColors.textSecondary, fontSize: 11)),
                            const SizedBox(height: 4),
                            const Text('48 ساعة',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Caution Note
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.shade50,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.amber.shade300),
              ),
              child: const Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Iconsax.info_circle, color: Colors.amber, size: 20),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'تنبيه سلامة: الحساب مبني على تعليمات الملصق المعتمد. يرجى ارتداء معدات الوقاية الشخصية والالتزام بفترة الأمان قبل الحصاد.',
                      style: TextStyle(fontSize: 11, height: 1.4, color: Colors.brown),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
