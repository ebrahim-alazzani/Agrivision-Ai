import '../../../core/storage/database_helper.dart';
import '../models/crop_model.dart';

abstract class CropLocalDataSource {
  Future<List<CropModel>> getCrops();
  Future<CropModel> addCrop(CropModel crop);
  Future<void> deleteCrop(String id);
}

class CropLocalDataSourceImpl implements CropLocalDataSource {
  @override
  Future<List<CropModel>> getCrops() async {
    final rows = await DatabaseHelper.query('crops');
    return rows.map((row) => CropModel.fromMap(row)).toList();
  }

  @override
  Future<CropModel> addCrop(CropModel crop) async {
    await DatabaseHelper.insert('crops', crop.toMap());
    return crop;
  }

  @override
  Future<void> deleteCrop(String id) async {
    await DatabaseHelper.delete('crops', where: 'id = ?', whereArgs: [id]);
  }
}
