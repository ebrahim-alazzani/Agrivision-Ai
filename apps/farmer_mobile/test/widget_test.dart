import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'package:agrivision_farmer/app.dart';
import 'package:agrivision_farmer/theme/agri_theme.dart';

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
    const pathProvider = MethodChannel('plugins.flutter.io/path_provider');
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(pathProvider, (call) async {
      if (call.method == 'getApplicationDocumentsDirectory') {
        return Directory.systemTemp.path;
      }
      return null;
    });
    Get.testMode = true;
    await GetStorage.init();
    if (!Get.isRegistered<AgriThemeController>()) {
      final ctrl = Get.put<AgriThemeController>(AgriThemeController(), permanent: true);
      ctrl.setWavesEnabled(false); // disable repeating wave timer during widget test
    }
  });

  tearDownAll(() {
    Get.reset();
  });

  testWidgets('AgriVisionApp smoke test', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1280, 1200);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const AgriVisionApp());
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.byType(AgriVisionApp), findsOneWidget);
  });
}
