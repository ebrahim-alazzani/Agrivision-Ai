import 'package:flutter/material.dart';
import 'package:get/get.dart';

class PesticideController extends GetxController {
  static PesticideController get instance => Get.find();

  final productNameController = TextEditingController(text: 'ريدوميل جولد (Ridomil Gold)');
  final waterVolumeController = TextEditingController(text: '100');
  final areaController = TextEditingController(text: '1000'); // square meters

  final dosePer100L = 250.0.obs; // grams or ml
  final calculatedDose = 250.0.obs;
  final phiDays = 7.obs; // Pre-Harvest Interval
  final activeIngredient = 'ميفينوكسام + مانكوزيب (Mefenoxam + Mancozeb)'.obs;

  void calculate() {
    final water = double.tryParse(waterVolumeController.text) ?? 100.0;
    calculatedDose.value = (water / 100.0) * dosePer100L.value;
  }
}
