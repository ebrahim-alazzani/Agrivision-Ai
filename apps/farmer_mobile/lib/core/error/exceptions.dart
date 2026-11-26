class ServerException implements Exception {
  final String message;
  final int? statusCode;
  const ServerException([this.message = 'Server Error', this.statusCode]);

  @override
  String toString() => 'ServerException: $message ($statusCode)';
}

class CacheException implements Exception {
  final String message;
  const CacheException([this.message = 'Cache Error']);

  @override
  String toString() => 'CacheException: $message';
}

class NetworkException implements Exception {
  final String message;
  const NetworkException([this.message = 'Network connection failed']);

  @override
  String toString() => 'NetworkException: $message';
}

class QualityCheckException implements Exception {
  final String message;
  final double score;
  const QualityCheckException(this.message, this.score);

  @override
  String toString() => 'QualityCheckException: $message (score: $score)';
}
