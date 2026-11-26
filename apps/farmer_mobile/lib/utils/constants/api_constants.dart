class ApiConstants {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

  // Authentication endpoints
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String profile = '/auth/me';

  // Farms endpoints
  static const String farms = '/farms';

  // Crops endpoints
  static const String crops = '/crops';

  // AI Inference & Analysis endpoints
  static const String plantAnalysis = '/analysis/plant-disease';
  static const String pestDetection = '/analysis/pest-detection';
  static const String analysisHistory = '/analysis/history';

  // Weather & Frost
  static const String weather = '/weather/current';
  static const String weatherForecast = '/weather/forecast';
  static const String frostAlerts = '/weather/frost-alerts';

  // Pesticide Knowledge & Calculator
  static const String pesticides = '/pesticides';
  static const String pesticideCalculate = '/pesticides/calculate-dosage';

  // Monitoring
  static const String monitoringRecords = '/monitoring/records';
  static const String monitoringCompare = '/monitoring/compare';
}
