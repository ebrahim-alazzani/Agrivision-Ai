import 'package:get/get.dart';
import '../core/network/api_service.dart';
import '../data/auth/datasources/auth_local_datasource.dart';
import '../data/auth/datasources/auth_remote_datasource.dart';
import '../data/auth/repositories_impl/auth_repository_impl.dart';
import '../domain/auth/usecases/auth_usecases.dart';
import '../features/auth/controllers/authentication_controller.dart';

class AuthBinding extends Bindings {
  @override
  void dependencies() {
    final remoteDataSource = AuthRemoteDataSourceImpl(Get.find<ApiService>());
    final localDataSource = AuthLocalDataSourceImpl();
    final repository = AuthRepositoryImpl(
      remoteDataSource: remoteDataSource,
      localDataSource: localDataSource,
    );

    Get.lazyPut(() => LoginUseCase(repository));
    Get.lazyPut(() => RegisterUseCase(repository));
    Get.lazyPut(() => GetCurrentUserUseCase(repository));
    Get.lazyPut(() => LogoutUseCase(repository));

    Get.lazyPut<AuthenticationController>(
      () => AuthenticationController(
        loginUseCase: Get.find(),
        registerUseCase: Get.find(),
        getCurrentUserUseCase: Get.find(),
      ),
      fenix: true,
    );
  }
}
