import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class DatabaseHelper {
  static const String dbName = 'agrivision_farmer.db';
  static const int dbVersion = 1;

  static Database? _database;

  static Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  static Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, dbName);

    return await openDatabase(
      path,
      version: dbVersion,
      onCreate: _onCreate,
    );
  }

  static Future<void> _onCreate(Database db, int version) async {
    // Farms Table
    await db.execute('''
      CREATE TABLE farms (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        area REAL NOT NULL,
        latitude REAL,
        longitude REAL,
        created_at TEXT NOT NULL,
        is_synced INTEGER NOT NULL DEFAULT 1
      )
    ''');

    // Crops Table
    await db.execute('''
      CREATE TABLE crops (
        id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        name TEXT NOT NULL,
        crop_type TEXT NOT NULL,
        variety TEXT,
        planting_date TEXT NOT NULL,
        status TEXT NOT NULL,
        is_synced INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE CASCADE
      )
    ''');

    // Plant Analyses Table
    await db.execute('''
      CREATE TABLE plant_analyses (
        id TEXT PRIMARY KEY,
        crop_id TEXT,
        image_path TEXT NOT NULL,
        disease_name_ar TEXT NOT NULL,
        disease_name_en TEXT NOT NULL,
        confidence REAL NOT NULL,
        severity TEXT NOT NULL,
        symptoms_ar TEXT,
        recommendations_ar TEXT,
        preventive_measures_ar TEXT,
        chemical_treatment_ar TEXT,
        organic_treatment_ar TEXT,
        created_at TEXT NOT NULL,
        is_synced INTEGER NOT NULL DEFAULT 1
      )
    ''');

    // Pest Detections Table
    await db.execute('''
      CREATE TABLE pest_detections (
        id TEXT PRIMARY KEY,
        crop_id TEXT,
        image_path TEXT NOT NULL,
        pest_name_ar TEXT NOT NULL,
        pest_name_en TEXT NOT NULL,
        count INTEGER NOT NULL,
        confidence REAL NOT NULL,
        treatment_ar TEXT,
        bounding_boxes TEXT,
        created_at TEXT NOT NULL,
        is_synced INTEGER NOT NULL DEFAULT 1
      )
    ''');

    // Offline Sync Queue Table
    await db.execute('''
      CREATE TABLE offline_queue (
        id TEXT PRIMARY KEY,
        action_type TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        payload TEXT,
        file_path TEXT,
        created_at TEXT NOT NULL,
        retry_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending'
      )
    ''');

    // Pesticide Usage Log Table
    await db.execute('''
      CREATE TABLE pesticide_usage_logs (
        id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        crop_name TEXT NOT NULL,
        active_ingredient TEXT,
        dosage_ml_per_liter REAL NOT NULL,
        total_volume_liters REAL NOT NULL,
        application_date TEXT NOT NULL,
        phi_days INTEGER NOT NULL,
        harvest_safe_date TEXT NOT NULL,
        notes TEXT
      )
    ''');
  }

  static Future<int> insert(String table, Map<String, dynamic> data) async {
    final db = await database;
    return await db.insert(table, data, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  static Future<List<Map<String, dynamic>>> query(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
    String? orderBy,
  }) async {
    final db = await database;
    return await db.query(table, where: where, whereArgs: whereArgs, orderBy: orderBy);
  }

  static Future<int> update(
    String table,
    Map<String, dynamic> data, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.update(table, data, where: where, whereArgs: whereArgs);
  }

  static Future<int> delete(
    String table, {
    String? where,
    List<dynamic>? whereArgs,
  }) async {
    final db = await database;
    return await db.delete(table, where: where, whereArgs: whereArgs);
  }
}
