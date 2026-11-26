import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'app.dart';
import 'theme/agri_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // GetStorage initialization (DevArchitect.IDE pattern)
  await GetStorage.init();
  Get.put<AgriThemeController>(AgriThemeController(), permanent: true);

  runApp(const AgriVisionApp());
}
