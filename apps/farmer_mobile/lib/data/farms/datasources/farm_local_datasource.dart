import '../../../core/storage/database_helper.dart';
import '../models/farm_model.dart';

abstract class FarmLocalDataSource {
  Future<List<FarmModel>> getFarms();
  Future<FarmModel> addFarm(FarmModel farm);
  Future<void> deleteFarm(String id);
}

class FarmLocalDataSourceImpl implements FarmLocalDataSource {
  @override
  Future<List<FarmModel>> getFarms() async {
    final rows = await DatabaseHelper.query('farms');
    return rows.map((row) => FarmModel.fromMap(row)).toList();
  }

  @override
  Future<FarmModel> addFarm(FarmModel farm) async {
    await DatabaseHelper.insert('farms', farm.toMap());
    return farm;
  }

  @override
  Future<void> deleteFarm(String id) async {
    await DatabaseHelper.delete('farms', where: 'id = ?', whereArgs: [id]);
  }
}
