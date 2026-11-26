import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';
import '../../../common/widgets/agri_button.dart';
import '../../../common/widgets/agri_text_field.dart';
import '../../../common/widgets/agri_tile.dart';
import '../../../theme/agri_colors.dart';
import '../controllers/farms_controller.dart';

class AddFarmDialog extends StatefulWidget {
  final FarmsController controller;

  const AddFarmDialog({super.key, required this.controller});

  @override
  State<AddFarmDialog> createState() => _AddFarmDialogState();
}

class _AddFarmDialogState extends State<AddFarmDialog> {
  final _nameCtrl = TextEditingController();
  final _regionCtrl = TextEditingController();
  final _areaCtrl = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _nameCtrl.dispose();
    _regionCtrl.dispose();
    _areaCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: AgriTile(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'إضافة مزرعة جديدة',
                style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 14),
              AgriTextField(
                controller: _nameCtrl,
                label: 'اسم المزرعة / الحقل',
                hint: 'مثال: حقل الطماطم الشمالي',
                prefixIcon: Iconsax.tree,
                validator: (v) => (v == null || v.trim().isEmpty) ? 'مطلوب' : null,
              ),
              const SizedBox(height: 12),
              AgriTextField(
                controller: _regionCtrl,
                label: 'المنطقة / المحافظة',
                hint: 'مثال: صنعاء - بني حشيش',
                prefixIcon: Iconsax.location,
                validator: (v) => (v == null || v.trim().isEmpty) ? 'مطلوب' : null,
              ),
              const SizedBox(height: 12),
              AgriTextField(
                controller: _areaCtrl,
                label: 'المساحة (متر مربع)',
                hint: '1500',
                prefixIcon: Iconsax.ruler,
                keyboardType: TextInputType.number,
                validator: (v) {
                  final parsed = double.tryParse(v ?? '');
                  if (parsed == null || parsed <= 0) return 'أدخل مساحة صحيحة';
                  return null;
                },
              ),
              const SizedBox(height: 18),
              AgriButton(
                text: 'حفظ المزرعة',
                icon: Iconsax.tick_circle,
                gradient: AgriColors.primaryGradient,
                onPressed: () async {
                  if (_formKey.currentState!.validate()) {
                    await widget.controller.createFarm(
                      name: _nameCtrl.text,
                      region: _regionCtrl.text,
                      area: double.parse(_areaCtrl.text.trim()),
                    );
                    Get.back();
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
