import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';
import 'package:get_storage/get_storage.dart';
import 'package:agrivision_farmer/app.dart';
import 'package:agrivision_farmer/theme/agri_theme.dart';

void main() {
  setUpAll(() async {
    TestWidgetsFlutterBinding.ensureInitialized();
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
    await tester.pumpWidget(const AgriVisionApp());
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.byType(AgriVisionApp), findsOneWidget);
  });
}
