import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:get/get.dart' as getx;
import '../error/exceptions.dart';
import '../storage/get_storage_helper.dart';

class ApiService extends getx.GetxService {
  static ApiService get instance => getx.Get.find();

  final getx.RxBool isConnected = true.obs;
  final Duration timeoutDuration = const Duration(seconds: 30);
  final String baseUrl = 'http://10.0.2.2:8000/api/v1';

  late final Dio _dio;
  final Connectivity _connectivity = Connectivity();

  @override
  void onInit() {
    super.onInit();
    _initDio();
    _startConnectionMonitor();
  }

  void _initDio() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: timeoutDuration,
        receiveTimeout: timeoutDuration,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          final token = GetStorageHelper.read<String>(GetStorageHelper.tokenKey);
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
      ),
    );
  }

  void _startConnectionMonitor() {
    _connectivity.onConnectivityChanged.listen((results) {
      isConnected.value = results.any((r) => r != ConnectivityResult.none);
    });
  }

  Future<dynamic> get(String endpoint, {Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.get(endpoint, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> post(String endpoint, {dynamic data, Map<String, dynamic>? queryParameters}) async {
    try {
      final response = await _dio.post(endpoint, data: data, queryParameters: queryParameters);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> uploadFile(
    String endpoint, {
    required String filePath,
    required String fileKey,
    Map<String, dynamic>? extraFields,
  }) async {
    try {
      final formData = FormData.fromMap({
        fileKey: await MultipartFile.fromFile(filePath),
        if (extraFields != null) ...extraFields,
      });

      final response = await _dio.post(endpoint, data: formData);
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Exception _handleDioError(DioException error) {
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.connectionError) {
      return const NetworkException('لا يمكن الاتصال بالخادم، يرجى فحص الشبكة');
    }

    final statusCode = error.response?.statusCode;
    final message = error.response?.data is Map
        ? (error.response?.data['detail'] ?? error.response?.data['message'] ?? 'خطأ في الخادم')
        : 'خطأ غير معروف في الخادم';

    return ServerException(message.toString(), statusCode);
  }
}
