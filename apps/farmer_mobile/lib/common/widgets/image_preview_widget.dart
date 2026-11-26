import 'dart:io';
import 'package:flutter/material.dart';
import '../../utils/constants/colors.dart';

class BoundingBox {
  final double x;
  final double y;
  final double width;
  final double height;
  final String label;
  final double confidence;

  const BoundingBox({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
    required this.label,
    required this.confidence,
  });
}

class ImagePreviewWidget extends StatelessWidget {
  final String? imagePath;
  final File? imageFile;
  final bool isNetwork;
  final List<BoundingBox>? boundingBoxes;
  final VoidCallback? onRemove;

  const ImagePreviewWidget({
    super.key,
    this.imagePath,
    this.imageFile,
    this.isNetwork = false,
    this.boundingBoxes,
    this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    Widget imageWidget;
    if (imageFile != null) {
      imageWidget = Image.file(
        imageFile!,
        fit: BoxFit.cover,
        width: double.infinity,
        height: 280,
      );
    } else if (isNetwork && imagePath != null) {
      imageWidget = Image.network(
        imagePath!,
        fit: BoxFit.cover,
        width: double.infinity,
        height: 280,
        errorBuilder: (ctx, err, stack) => _errorPlaceholder(),
      );
    } else if (imagePath != null && File(imagePath!).existsSync()) {
      imageWidget = Image.file(
        File(imagePath!),
        fit: BoxFit.cover,
        width: double.infinity,
        height: 280,
      );
    } else {
      imageWidget = _errorPlaceholder();
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: Stack(
        alignment: Alignment.center,
        children: [
          imageWidget,
          if (boundingBoxes != null && boundingBoxes!.isNotEmpty)
            Positioned.fill(
              child: CustomPaint(
                painter: BoundingBoxPainter(boxes: boundingBoxes!),
              ),
            ),
          if (onRemove != null)
            Positioned(
              top: 8,
              left: 8,
              child: CircleAvatar(
                backgroundColor: Colors.black54,
                radius: 16,
                child: IconButton(
                  padding: EdgeInsets.zero,
                  icon: const Icon(Icons.close, color: Colors.white, size: 18),
                  onPressed: onRemove,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _errorPlaceholder() {
    return Container(
      width: double.infinity,
      height: 280,
      color: Colors.grey.shade200,
      child: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.broken_image_rounded, size: 48, color: Colors.grey),
            SizedBox(height: 8),
            Text('صورة غير متوفرة', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}

class BoundingBoxPainter extends CustomPainter {
  final List<BoundingBox> boxes;

  BoundingBoxPainter({required this.boxes});

  @override
  void paint(Canvas canvas, Size size) {
    final borderPaint = Paint()
      ..color = TColors.error
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5;

    final fillPaint = Paint()
      ..color = TColors.error.withOpacity(0.2)
      ..style = PaintingStyle.fill;

    for (final box in boxes) {
      final rect = Rect.fromLTWH(
        box.x * size.width,
        box.y * size.height,
        box.width * size.width,
        box.height * size.height,
      );

      canvas.drawRect(rect, fillPaint);
      canvas.drawRect(rect, borderPaint);

      final textSpan = TextSpan(
        text: '${box.label} (${(box.confidence * 100).toInt()}%)',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 11,
          fontWeight: FontWeight.bold,
          backgroundColor: TColors.error,
        ),
      );

      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.rtl,
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(rect.left, (rect.top - 18).clamp(0, size.height)),
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
