import 'package:dartz/dartz.dart';
import '../../../core/error/failures.dart';
import '../entities/user_entity.dart';

abstract class AuthRepository {
  Future<Either<Failure, UserEntity>> login(String phoneNumber, String password);
  Future<Either<Failure, UserEntity>> register({
    required String fullName,
    required String phoneNumber,
    required String password,
    required String region,
  });
  Future<Either<Failure, UserEntity?>> getCurrentUser();
  Future<Either<Failure, void>> logout();
}
