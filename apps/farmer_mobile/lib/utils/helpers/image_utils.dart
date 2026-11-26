import 'dart:io';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;
import 'package:image_picker/image_picker.dart';
import '../../core/error/exceptions.dart';

class ImageUtils {
  static final ImagePicker _picker = ImagePicker();

  static Future<File?> pickFromCamera() async {
    final XFile? file = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1600,
      maxHeight: 1600,
      imageQuality: 88,
    );
    if (file == null) return null;
    return File(file.path);
  }

  static Future<File?> pickFromGallery() async {
    final XFile? file = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1600,
      maxHeight: 1600,
      imageQuality: 88,
    );
    if (file == null) return null;
    return File(file.path);
  }

  static Future<bool> validateImageQuality(File imageFile) async {
    if (!await imageFile.exists()) {
      throw const QualityCheckException('الملف غير موجود', 0.0);
    }
    final length = await imageFile.length();
    if (length < 15 * 1024) {
      throw const QualityCheckException(
        'حجم الصورة صغير جداً، يرجى التقاط صورة واضحة ومقربة للورقة المصابة',
        0.1,
      );
    }
    return true;
  }

  /// تحويل إطار الكاميرا المباشر (YUV420 / BGRA8888) إلى صورة RGB بحجم 224x224
  static img.Image? convertCameraImageToRgb(CameraImage cameraImage) {
    if (cameraImage.format.group == ImageFormatGroup.yuv420) {
      return _convertYuv420To224(cameraImage);
    } else if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
      return _convertBgra8888(cameraImage);
    }
    return null;
  }

  static img.Image _convertBgra8888(CameraImage image) {
    final raw = img.Image.fromBytes(
      width: image.width,
      height: image.height,
      bytes: image.planes[0].bytes.buffer,
      order: img.ChannelOrder.bgra,
    );
    return img.copyResize(raw, width: 224, height: 224);
  }

  static img.Image _convertYuv420To224(CameraImage image) {
    const int targetSize = 224;
    final outImg = img.Image(width: targetSize, height: targetSize);

    final int srcW = image.width;
    final int srcH = image.height;
    final yPlane = image.planes[0];
    final uPlane = image.planes[1];
    final vPlane = image.planes[2];

    final int uvRowStride = uPlane.bytesPerRow;
    final int uvPixelStride = uPlane.bytesPerPixel ?? 1;

    for (int ty = 0; ty < targetSize; ty++) {
      final int sy = (ty * srcH) ~/ targetSize;
      final int yRowOffset = sy * yPlane.bytesPerRow;
      final int uvRowOffset = (sy >> 1) * uvRowStride;

      for (int tx = 0; tx < targetSize; tx++) {
        final int sx = (tx * srcW) ~/ targetSize;
        final int yIdx = yRowOffset + sx;
        final int uvIdx = uvRowOffset + (sx >> 1) * uvPixelStride;

        final int y = yPlane.bytes[yIdx];
        final int u = uPlane.bytes[uvIdx];
        final int v = vPlane.bytes[uvIdx];

        final int r = (y + (1.370705 * (v - 128))).round().clamp(0, 255);
        final int g = (y - (0.337633 * (u - 128)) - (0.698001 * (v - 128)))
            .round()
            .clamp(0, 255);
        final int b = (y + (1.732446 * (u - 128))).round().clamp(0, 255);

        outImg.setPixelRgb(tx, ty, r, g, b);
      }
    }
    return outImg;
  }
}
