import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../core/usecases/usecase.dart';
import '../../../domain/auth/entities/user_entity.dart';
import '../../../domain/auth/usecases/auth_usecases.dart';
import '../../../routers/routes.dart';

class AuthenticationController extends GetxController {
  static AuthenticationController get instance => Get.find();

  final LoginUseCase loginUseCase;
  final RegisterUseCase registerUseCase;
  final GetCurrentUserUseCase getCurrentUserUseCase;

  AuthenticationController({
    required this.loginUseCase,
    required this.registerUseCase,
    required this.getCurrentUserUseCase,
  });

  final isLoading = false.obs;
  final hidePassword = true.obs;
  final phoneController = TextEditingController(text: '777123456');
  final passwordController = TextEditingController(text: '123456');
  final nameController = TextEditingController();
  final selectedRegion = 'صنعاء - بني حشيش / بني مطر'.obs;
  final loginFormKey = GlobalKey<FormState>();
  final registerFormKey = GlobalKey<FormState>();

  final Rxn<UserEntity> currentUser = Rxn<UserEntity>();
  final errorMessage = ''.obs;

  @override
  void onInit() {
    super.onInit();
    checkCurrentUser();
  }

  Future<void> checkCurrentUser() async {
    final result = await getCurrentUserUseCase(const NoParams());
    result.fold(
      (failure) => null,
      (user) {
        if (user != null) {
          currentUser.value = user;
        }
      },
    );
  }

  Future<void> login() async {
    if (!loginFormKey.currentState!.validate()) return;

    try {
      isLoading.value = true;
      errorMessage.value = '';

      final result = await loginUseCase(LoginParams(
        phoneNumber: phoneController.text.trim(),
        password: passwordController.text.trim(),
      ));

      result.fold(
        (failure) {
          errorMessage.value = failure.message;
          Get.snackbar('خطأ في الدخول', failure.message, snackPosition: SnackPosition.BOTTOM);
        },
        (user) {
          currentUser.value = user;
          Get.offAllNamed(TRoutes.dashboard);
        },
      );
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> register() async {
    if (!registerFormKey.currentState!.validate()) return;

    try {
      isLoading.value = true;
      errorMessage.value = '';

      final result = await registerUseCase(RegisterParams(
        fullName: nameController.text.trim(),
        phoneNumber: phoneController.text.trim(),
        password: passwordController.text.trim(),
        region: selectedRegion.value,
      ));

      result.fold(
        (failure) {
          errorMessage.value = failure.message;
          Get.snackbar('خطأ في التسجيل', failure.message, snackPosition: SnackPosition.BOTTOM);
        },
        (user) {
          currentUser.value = user;
          Get.offAllNamed(TRoutes.dashboard);
        },
      );
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> logout() async {
    currentUser.value = null;
    Get.offAllNamed(TRoutes.login);
  }
}
