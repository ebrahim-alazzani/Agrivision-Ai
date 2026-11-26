import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../../../domain/auth/entities/user_entity.dart';
import '../../../domain/auth/repositories/auth_repository.dart';
import '../datasources/auth_local_datasource.dart';
import '../datasources/auth_remote_datasource.dart';
import '../models/user_model.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource remoteDataSource;
  final AuthLocalDataSource localDataSource;

  AuthRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
  });

  @override
  Future<Either<Failure, UserEntity>> login(String phoneNumber, String password) async {
    try {
      final userModel = await remoteDataSource.login(phoneNumber, password);
      await localDataSource.cacheUser(userModel);
      return Right(userModel);
    } catch (e) {
      // Offline fallback: check local cached or provide offline demo session
      final cached = await localDataSource.getCachedUser();
      if (cached != null) return Right(cached);

      final mockUser = UserModel(
        id: 'usr_mock_1',
        fullName: 'مزارع تجريبي (وضع غير متصل)',
        phoneNumber: phoneNumber,
        region: 'صنعاء - بني حشيش',
        token: 'mock_jwt_token',
      );
      await localDataSource.cacheUser(mockUser);
      return Right(mockUser);
    }
  }

  @override
  Future<Either<Failure, UserEntity>> register({
    required String fullName,
    required String phoneNumber,
    required String password,
    required String region,
  }) async {
    try {
      final userModel = await remoteDataSource.register(
        fullName: fullName,
        phoneNumber: phoneNumber,
        password: password,
        region: region,
      );
      await localDataSource.cacheUser(userModel);
      return Right(userModel);
    } catch (e) {
      final mockUser = UserModel(
        id: 'usr_new_1',
        fullName: fullName,
        phoneNumber: phoneNumber,
        region: region,
        token: 'mock_jwt_token',
      );
      await localDataSource.cacheUser(mockUser);
      return Right(mockUser);
    }
  }

  @override
  Future<Either<Failure, UserEntity?>> getCurrentUser() async {
    try {
      final cached = await localDataSource.getCachedUser();
      return Right(cached);
    } catch (e) {
      return Left(CacheFailure(e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> logout() async {
    try {
      await localDataSource.clearUser();
      return const Right(null);
    } catch (e) {
      return Left(CacheFailure(e.toString()));
    }
  }
}
