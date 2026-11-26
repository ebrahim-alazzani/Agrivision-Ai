import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:onnxruntime/onnxruntime.dart';

class PlantDiagnosisResult {
  final String rawClassName;
  final String cropNameArabic;
  final String diseaseNameArabic;
  final bool isHealthy;
  final double confidence;
  final String severity;
  final String symptoms;
  final List<String> recommendations;
  final Map<String, double> topClasses;

  PlantDiagnosisResult({
    required this.rawClassName,
    required this.cropNameArabic,
    required this.diseaseNameArabic,
    required this.isHealthy,
    required this.confidence,
    required this.severity,
    required this.symptoms,
    required this.recommendations,
    required this.topClasses,
  });
}

class PlantDiseaseClassifierService {
  static final PlantDiseaseClassifierService instance =
      PlantDiseaseClassifierService._internal();
  PlantDiseaseClassifierService._internal();

  OrtSession? _session;
  Map<int, String> _idxToClass = {};
  bool _isInitialized = false;

  bool get isReady => _isInitialized && _session != null;

  Future<void> initialize() async {
    if (_isInitialized && _session != null) return;

    OrtEnv.instance.init();

    final jsonString =
        await rootBundle.loadString('assets/models/class_indices.json');
    final Map<String, dynamic> parsed = json.decode(jsonString);
    final idxMap = parsed['idx_to_class'] as Map<String, dynamic>;
    _idxToClass = idxMap.map((k, v) => MapEntry(int.parse(k), v.toString()));

    final modelData =
        await rootBundle.load('assets/models/agrivision_plant_model.onnx');
    final bytes = modelData.buffer.asUint8List();

    final sessionOptions = OrtSessionOptions();
    _session = OrtSession.fromBuffer(bytes, sessionOptions);
    _isInitialized = true;
  }

  Future<PlantDiagnosisResult> classifyImage(File imageFile) async {
    await initialize();
    final bytes = await imageFile.readAsBytes();
    final decodedImage = img.decodeImage(bytes);
    if (decodedImage == null) {
      throw Exception('فشل في قراءة ومعالجة ملف الصورة');
    }
    return _runOnnxInference(decodedImage);
  }

  /// تصنيف مباشر لإطار صورة من بث الكاميرا الحي أو الفيديو
  Future<PlantDiagnosisResult> classifyRgbImage(img.Image frameImage) async {
    await initialize();
    return _runOnnxInference(frameImage);
  }

  Future<PlantDiagnosisResult> _runOnnxInference(img.Image image) async {
    if (_session == null) {
      throw Exception('نموذج ONNX غير مهيأ بعد');
    }

    final resized = img.copyResize(image, width: 224, height: 224);

    const mean = [0.485, 0.456, 0.406];
    const std = [0.229, 0.224, 0.225];

    final inputData = Float32List(1 * 3 * 224 * 224);
    const totalPixels = 224 * 224;

    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        final pixel = resized.getPixel(x, y);
        final pixelIndex = y * 224 + x;

        final r = pixel.r / 255.0;
        final g = pixel.g / 255.0;
        final b = pixel.b / 255.0;

        inputData[pixelIndex] = (r - mean[0]) / std[0];
        inputData[totalPixels + pixelIndex] = (g - mean[1]) / std[1];
        inputData[totalPixels * 2 + pixelIndex] = (b - mean[2]) / std[2];
      }
    }

    final inputOrtValue = OrtValueTensor.createTensorWithDataList(
      inputData,
      [1, 3, 224, 224],
    );

    final inputName = _session!.inputNames.first;
    final runOptions = OrtRunOptions();
    final outputs = _session!.run(runOptions, {inputName: inputOrtValue});
    inputOrtValue.release();
    runOptions.release();

    final outputValue = outputs.first?.value as List<dynamic>;
    for (final out in outputs) {
      out?.release();
    }

    final List<double> rawScores = outputValue.first is List
        ? (outputValue.first as List).map((e) => (e as num).toDouble()).toList()
        : outputValue.map((e) => (e as num).toDouble()).toList();

    final maxScore = rawScores.reduce(math.max);
    final expScores = rawScores.map((s) => math.exp(s - maxScore)).toList();
    final sumExp = expScores.reduce((a, b) => a + b);
    final probabilities = expScores.map((e) => e / sumExp).toList();

    int bestIndex = 0;
    double maxProb = probabilities[0];
    for (int i = 1; i < probabilities.length; i++) {
      if (probabilities[i] > maxProb) {
        maxProb = probabilities[i];
        bestIndex = i;
      }
    }

    final rawClassName = _idxToClass[bestIndex] ?? 'Tomato___healthy';
    return _buildDiagnosis(rawClassName, maxProb);
  }

  PlantDiagnosisResult _buildDiagnosis(String rawClassName, double confidence) {
    final parts = rawClassName.split('___');
    final cropEng = parts.first;
    final conditionEng = parts.length > 1 ? parts[1] : 'healthy';

    final isHealthy = conditionEng.toLowerCase() == 'healthy';
    final cropArabic = _cropArabicMap[cropEng] ?? cropEng;

    if (isHealthy) {
      return PlantDiagnosisResult(
        rawClassName: rawClassName,
        cropNameArabic: cropArabic,
        diseaseNameArabic: 'سليم ومعافى (خالٍ من الأمراض)',
        isHealthy: true,
        confidence: confidence,
        severity: 'healthy',
        symptoms:
            'الأنسجة النباتية بحالة صحية جيدة، ولا تظهر مؤشرات بقع فطرية أو بكتيرية أو اصفرار فيروسي.',
        recommendations: const [
          'الاستمرار في جدول الري المنتظم وفق احتياج التربة.',
          'الحفاظ على تهوية جيدة بين النباتات.',
          'الاستمرار في الفحص الدوري للوقاية المبكرة.',
        ],
        topClasses: {rawClassName: confidence},
      );
    }

    final diseaseInfo = _diseaseKnowledge[rawClassName] ??
        _defaultDiseaseInfo(cropArabic, conditionEng);

    return PlantDiagnosisResult(
      rawClassName: rawClassName,
      cropNameArabic: cropArabic,
      diseaseNameArabic: diseaseInfo['name'] as String,
      isHealthy: false,
      confidence: confidence,
      severity: diseaseInfo['severity'] as String,
      symptoms: diseaseInfo['symptoms'] as String,
      recommendations: List<String>.from(diseaseInfo['recommendations'] as List),
      topClasses: {rawClassName: confidence},
    );
  }

  static const Map<String, String> _cropArabicMap = {
    'Apple': 'التفاح',
    'Blueberry': 'التوت الأزرق',
    'Cherry_(including_sour)': 'الكرز',
    'Corn_(maize)': 'الذرة الشامية',
    'Grape': 'العنب',
    'Orange': 'الحمضيات / البرتقال',
    'Peach': 'الخوخ',
    'Pepper,_bell': 'الفلفل الحلو',
    'Potato': 'البطاطس',
    'Raspberry': 'توت العليق',
    'Soybean': 'فول الصويا',
    'Squash': 'الكوسا / القرعيات',
    'Strawberry': 'الفراولة',
    'Tomato': 'الطماطم',
  };

  Map<String, dynamic> _defaultDiseaseInfo(String crop, String condition) {
    return {
      'name': 'إصابة في $crop (${condition.replaceAll('_', ' ')})',
      'severity': 'moderate',
      'symptoms': 'تغيرات لونية أو بقع مرصودة على أنسجة الورقة النباتية.',
      'recommendations': const [
        'عزل الأوراق المصابة ومتابعة انتشار الأعراض.',
        'تجنب الري الرشاش المسائي لتقليل الرطوبة على الأوراق.',
        'استشارة مهندس زراعي لتحديد التدخل العلاجي المناسب.',
      ],
    };
  }

  static const Map<String, Map<String, dynamic>> _diseaseKnowledge = {
    'Tomato___Early_blight': {
      'name': 'اللفحة المبكرة (Alternaria solani)',
      'severity': 'moderate',
      'symptoms':
          'بقع بنية متحدة المركز على الأوراق السفلية مع هالة صفراء محيطة.',
      'recommendations': [
        'إزالة الأوراق السفلية المصابة والتخلص منها خارج الحقل.',
        'الرش الوقائي بمبيد فطري نحاسي أو ديفينوكونازول.',
        'تجنب الري المفرط واستخدام الري بالتنقيط.',
      ],
    },
    'Tomato___Late_blight': {
      'name': 'اللفحة المتأخرة (Phytophthora infestans)',
      'severity': 'critical',
      'symptoms':
          'بقع مائية داكنة على الأوراق مع زغب فطري أبيض على السطح السفلي في الرطوبة العالية.',
      'recommendations': [
        'التدخل الفوري بمبيد جهازي مناسب مثل ميفينوكسام.',
        'إيقاف الري الرشاش وتقليل الرطوبة الحقلية.',
        'التخلص الآمن من النباتات المصابة بشدة.',
      ],
    },
    'Tomato___Bacterial_spot': {
      'name': 'التبقع البكتيري (Xanthomonas spp.)',
      'severity': 'high',
      'symptoms': 'بقع دائرية صغيرة داكنة ذات حواف خشنة وملمس دهني.',
      'recommendations': [
        'الرش بمركبات هيدروكسيد النحاس المعتمدة.',
        'تعقيم أدوات التقليم والمعدات قبل الانتقال بين الخطوط.',
      ],
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
      'name': 'فيروس تجعد واصفرار الأوراق (TYLCV)',
      'severity': 'high',
      'symptoms': 'تقزم النبات واصفرار حواف الأوراق وتجعدها للأعلى.',
      'recommendations': [
        'مكافحة الذبابة البيضاء بالمصائد الصفراء والمبيدات الموصى بها.',
        'إزالة النباتات المصابة مبكراً للحد من انتشار الفيروس.',
      ],
    },
    'Potato___Early_blight': {
      'name': 'اللفحة المبكرة في البطاطس',
      'severity': 'moderate',
      'symptoms': 'بقع بنية جافة متحدة المركز على الأوراق القديمة.',
      'recommendations': [
        'الرش الوقائي بمبيد المانكوزيب أو كلوروثالونيل.',
        'تنظيم الري وتجنب ركود المياه.',
      ],
    },
    'Potato___Late_blight': {
      'name': 'اللفحة المتأخرة في البطاطس',
      'severity': 'critical',
      'symptoms': 'بقع رمادية إلى بنية داكنة تتسع بسرعة وتسبب ذبول المجموع الخضري.',
      'recommendations': [
        'التدخل الفوري بمبيد سيموكسانيل أو ميتالاكسيل.',
        'منع وصول مياه الري الملوثة إلى الدرنات.',
      ],
    },
    'Grape___Black_rot': {
      'name': 'العفن الأسود في العنب',
      'severity': 'high',
      'symptoms': 'بقع بنية مائلة للحمرة على الأوراق وتجعد حبات العنب بلون أسود.',
      'recommendations': [
        'تقليم الأغصان المتشابكة لتحسين التهوية وأشعة الشمس.',
        'الرش بمبيد نحاسي وقائي عند تفتح البراعم.',
      ],
    },
  };
}
