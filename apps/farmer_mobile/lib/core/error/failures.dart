import 'package:equatable/equatable.dart';

abstract class Failure extends Equatable {
  final String message;
  const Failure(this.message);

  @override
  List<Object?> get props => [message];
}

class ServerFailure extends Failure {
  const ServerFailure([super.message = 'حدث خطأ في الخادم، يرجى المحاولة لاحقاً']);
}

class CacheFailure extends Failure {
  const CacheFailure([super.message = 'فشل استرجاع البيانات المحفوظة محلياً']);
}

class NetworkFailure extends Failure {
  const NetworkFailure([super.message = 'لا يوجد اتصال بالإنترنت، يرجى التحقق من الشبكة']);
}

class ValidationFailure extends Failure {
  const ValidationFailure(super.message);
}

class QualityCheckFailure extends Failure {
  final double blurScore;
  const QualityCheckFailure({
    required this.blurScore,
    String message = 'جودة الصورة غير كافية (صورة ضبابية أو غير واضحة). يرجى إعادة الالتقاط.',
  }) : super(message);
}
