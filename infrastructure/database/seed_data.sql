-- AgriVision AI Seed Data
-- Seed Roles, Yemeni Governorates, Crops, Growth Stages, Diseases, Pests, and Relations

\connect agrivision;

-- 1. Default Roles
INSERT INTO public.roles (id, name_en, name_ar, description) VALUES
('admin', 'Administrator', 'مدير النظام', 'Full platform management and security permissions'),
('researcher', 'Agricultural Researcher', 'باحث زراعي', 'Access to AI Studio, datasets, model benchmarking, and training pipelines'),
('agronomist', 'Agronomist / Extension Agent', 'مرشد / خبير زراعي', 'Field validation, annotation review, and pest/pesticide consultation'),
('farmer', 'Farmer', 'مزارع', 'Mobile app user, farm diagnostic inference, weather alerts, and crop records')
ON CONFLICT (id) DO UPDATE SET
    name_en = EXCLUDED.name_en,
    name_ar = EXCLUDED.name_ar,
    description = EXCLUDED.description;

-- 2. Yemeni Governorates (22 Governorates)
INSERT INTO public.governorates (id, name_ar, name_en, latitude, longitude, geom, major_agricultural_areas) VALUES
('ye-sn', 'أمانة العاصمة', 'Sana''a City', 15.3694, 44.1910, ST_SetSRID(ST_MakePoint(44.1910, 15.3694), 4326), ARRAY['بني الحارث', 'الروضة', 'شعوب']),
('ye-sa', 'صنعاء', 'Sana''a Governorate', 15.3547, 44.2066, ST_SetSRID(ST_MakePoint(44.2066, 15.3547), 4326), ARRAY['بني حشيش', 'بني مطر', 'الحيمة', 'خولان', 'همدان', 'أرحب']),
('ye-ad', 'عدن', 'Aden', 12.7855, 45.0187, ST_SetSRID(ST_MakePoint(45.0187, 12.7855), 4326), ARRAY['دار سعد', 'البريقة']),
('ye-ta', 'تعز', 'Taiz', 13.5795, 44.0209, ST_SetSRID(ST_MakePoint(44.0209, 13.5795), 4326), ARRAY['المواسط', 'المعافر', 'موزع', 'المخا', 'صبر الموادم', 'شرعب']),
('ye-hd', 'الحديدة', 'Al Hudaydah', 14.7978, 42.9545, ST_SetSRID(ST_MakePoint(42.9545, 14.7978), 4326), ARRAY['سهل تهامة', 'وادي زبيد', 'وادي سهام', 'وادي سردد', 'بيت الفقيه', 'باجل']),
('ye-ib', 'إب', 'Ibb', 13.9667, 44.1833, ST_SetSRID(ST_MakePoint(44.1833, 13.9667), 4326), ARRAY['وادي السحول', 'ميتم', 'يريم', 'العدين', 'جبلة', 'المشنة']),
('ye-dh', 'ذمار', 'Dhamar', 14.5427, 44.4051, ST_SetSRID(ST_MakePoint(44.4051, 14.5427), 4326), ARRAY['قاع جهران', 'عنس', 'ميفعة عنس', 'الحداء', 'وصابين']),
('ye-hm', 'حضرموت', 'Hadhramaut', 15.9333, 49.1667, ST_SetSRID(ST_MakePoint(49.1667, 15.9333), 4326), ARRAY['وادي حضرموت', 'تريم', 'سيئون', 'القطن', 'غيل باوزير', 'وادي دوعن']),
('ye-hj', 'حجة', 'Hajjah', 15.6961, 43.6067, ST_SetSRID(ST_MakePoint(43.6067, 15.6961), 4326), ARRAY['عبس', 'حرض', 'وادي مور', 'المحابشة', 'ميدي']),
('ye-sd', 'صعدة', 'Sa''ada', 16.9400, 43.7639, ST_SetSRID(ST_MakePoint(43.7639, 16.9400), 4326), ARRAY['سحار', 'الصفراء', 'حيدان', 'رازح', 'مجز', 'باقم']),
('ye-am', 'عمران', 'Amran', 15.6586, 43.9439, ST_SetSRID(ST_MakePoint(43.9439, 15.6586), 4326), ARRAY['قاع البون', 'خمر', 'ريدة', 'حوث', 'عيال سريح']),
('ye-mw', 'المحويت', 'Al Mahwit', 15.4703, 43.5453, ST_SetSRID(ST_MakePoint(43.5453, 15.4703), 4326), ARRAY['ملحان', 'حفاش', 'شبام كوكبان', 'الرجم']),
('ye-ry', 'ريمة', 'Raymah', 14.6292, 43.7144, ST_SetSRID(ST_MakePoint(43.7144, 14.6292), 4326), ARRAY['بلاد الطعام', 'الجبين', 'كسمة', 'السلفية']),
('ye-ba', 'البيضاء', 'Al Bayda', 13.9852, 45.5727, ST_SetSRID(ST_MakePoint(45.5727, 13.9852), 4326), ARRAY['رداع', 'مكيراس', 'السوادية', 'ولد ربيع']),
('ye-mr', 'مأرب', 'Marib', 15.4542, 45.3267, ST_SetSRID(ST_MakePoint(45.3267, 15.4542), 4326), ARRAY['وادي عبيدة', 'صرواح', 'حريب', 'الجوبة']),
('ye-jw', 'الجوف', 'Al Jawf', 16.5000, 45.5000, ST_SetSRID(ST_MakePoint(45.5000, 16.5000), 4326), ARRAY['خب والشعف', 'الحزم', 'المتون', 'برط العنان']),
('ye-sh', 'شبوة', 'Shabwah', 14.5333, 46.8333, ST_SetSRID(ST_MakePoint(46.8333, 14.5333), 4326), ARRAY['وادي بيحان', 'عتق', 'ميفعة', 'حبان', 'نصاب']),
('ye-ab', 'أبين', 'Abyan', 13.5833, 45.7500, ST_SetSRID(ST_MakePoint(45.7500, 13.5833), 4326), ARRAY['دلتا أبين', 'خنفر', 'زنجبار', 'لودر', 'مودية', 'أحور']),
('ye-la', 'لحج', 'Lahij', 13.1667, 44.8833, ST_SetSRID(ST_MakePoint(44.8833, 13.1667), 4326), ARRAY['دلتا تبن', 'الحوطة', 'طور الباحة', 'يافع', 'القبيطة']),
('ye-mh', 'المهرة', 'Al Mahrah', 16.5000, 51.5000, ST_SetSRID(ST_MakePoint(51.5000, 16.5000), 4326), ARRAY['الغيضة', 'حوف', 'سيحوت', 'قشن']),
('ye-sc', 'أرخبيل سقطرى', 'Socotra Archipelago', 12.4634, 53.8237, ST_SetSRID(ST_MakePoint(53.8237, 12.4634), 4326), ARRAY['حديبو', 'قلنسية']),
('ye-da', 'الضالع', 'Ad Dali''', 13.6958, 44.7314, ST_SetSRID(ST_MakePoint(44.7314, 13.6958), 4326), ARRAY['دمت', 'قعطبة', 'الحصين', 'جبن'])
ON CONFLICT (id) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    geom = EXCLUDED.geom,
    major_agricultural_areas = EXCLUDED.major_agricultural_areas;

-- 3. Supported Crops
INSERT INTO knowledge.crops (id, name_ar, name_en, scientific_name, category, growing_seasons, common_regions) VALUES
('crop-tomato', 'طماطم', 'Tomato', 'Solanum lycopersicum', 'Vegetable', ARRAY['ربيعي', 'خريفي', 'شتوي'], ARRAY['صنعاء', 'ذمار', 'الحديدة', 'مأرب', 'صعدة']),
('crop-potato', 'بطاطس', 'Potato', 'Solanum tuberosum', 'Tuber', ARRAY['صيفي', 'خريفي', 'شتوي'], ARRAY['ذمار', 'صنعاء', 'عمران', 'إب']),
('crop-grape', 'عنب', 'Grape', 'Vitis vinifera', 'Fruit', ARRAY['صيفي'], ARRAY['صنعاء (بني حشيش)', 'صعدة', 'عمران']),
('crop-wheat', 'قمح', 'Wheat', 'Triticum aestivum', 'Cereal', ARRAY['شتوي', 'صيفي'], ARRAY['قاع جهران', 'قاع البون', 'حضرموت', 'الجوف', 'مأرب']),
('crop-coffee', 'بن يمني', 'Yemeni Coffee', 'Coffea arabica', 'Cash Crop', ARRAY['طوال العام'], ARRAY['بني مطر', 'حراز', 'يافع', 'ريمة', 'المحويت', 'الحيمة']),
('crop-qat', 'قات', 'Qat', 'Catha edulis', 'Stimulant Crop', ARRAY['طوال العام'], ARRAY['همدان', 'الحيمة', 'ذمار', 'إب', 'الضالع']),
('crop-mango', 'مانجو', 'Mango', 'Mangifera indica', 'Fruit', ARRAY['صيفي'], ARRAY['الحديدة (تهامة)', 'حجة (عبس)', 'لحج', 'أبين']),
('crop-datepalm', 'نخيل التمر', 'Date Palm', 'Phoenix dactylifera', 'Fruit', ARRAY['صيفي'], ARRAY['حضرموت', 'الحديدة', 'الجوف', 'شبوة', 'المهرة']),
('crop-sorghum', 'ذرة رفيعة', 'Sorghum', 'Sorghum bicolor', 'Cereal', ARRAY['صيفي'], ARRAY['إب', 'تعز', 'الحديدة', 'لحج', 'حجة']),
('crop-onion', 'بصل', 'Onion', 'Allium cepa', 'Vegetable', ARRAY['شتوي', 'ربيعي'], ARRAY['مأرب', 'حضرموت', 'الحديدة', 'صنعاء'])
ON CONFLICT (id) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    scientific_name = EXCLUDED.scientific_name,
    category = EXCLUDED.category,
    growing_seasons = EXCLUDED.growing_seasons,
    common_regions = EXCLUDED.common_regions;

-- 4. Growth Stages
INSERT INTO knowledge.growth_stages (id, crop_id, stage_order, name_ar, name_en, description, typical_duration_days) VALUES
('gs-tom-1', 'crop-tomato', 1, 'إنبات وبادرات', 'Seedling & Emergence', 'مرحلة خروج البادرات وتكوين الأوراق الحقيقية الأولى', 20),
('gs-tom-2', 'crop-tomato', 2, 'نمو خضري', 'Vegetative Growth', 'تفرع السيقان وزيادة المجموع الخضري', 30),
('gs-tom-3', 'crop-tomato', 3, 'تزهير وعقد', 'Flowering & Fruit Set', 'ظهور الأزهار الصفراء وبدء عقد الثمار الصغيرة', 25),
('gs-tom-4', 'crop-tomato', 4, 'نضج وحصاد', 'Ripening & Harvesting', 'تحول لون الثمار من الأخضر إلى الأحمر وجني المحصول', 35),

('gs-pot-1', 'crop-potato', 1, 'بزوغ الدرنات', 'Sprout Development', 'خروج النموات من عيون درنات التقاوي فوق سطح التربة', 18),
('gs-pot-2', 'crop-potato', 2, 'نمو خضري وتفرع', 'Vegetative Canopy', 'تكوين الأوراق والسيقان المورقة', 30),
('gs-pot-3', 'crop-potato', 3, 'تكوين وامتلاء الدرنات', 'Tuber Bulking', 'تضخم الدرنات تحت التربة وتراكم النشا', 40),
('gs-pot-4', 'crop-potato', 4, 'نضج وموت المجموع الخضري', 'Maturation', 'اصفرار المجموع الخضري وجفاف قشرة الدرنات للحصاد', 20),

('gs-cof-1', 'crop-coffee', 1, 'نمو خضري وتوريق', 'Vegetative & Leafing', 'نمو الأفرع الجانبية وظهور الأوراق الخضراء اللامعة', 90),
('gs-cof-2', 'crop-coffee', 2, 'تزهير أبيض', 'White Blossom', 'ظهور الأزهار البيضاء العطرية بعد نزول الأمطار', 15),
('gs-cof-3', 'crop-coffee', 3, 'تطور الحبوب الخضراء', 'Berry Development', 'تكون حبوب البن الخضراء وتصلب النواة', 120),
('gs-cof-4', 'crop-coffee', 4, 'نضج الحبوب الحمراء', 'Berry Ripening', 'تحول حبوب البن إلى اللون الأحمر الياقوتي للحصاد اليدوي', 45)
ON CONFLICT (id) DO NOTHING;

-- 5. Common Diseases
INSERT INTO knowledge.diseases (id, name_ar, name_en, scientific_name, pathogen_type, symptoms_description_ar, symptoms_description_en, severity_levels, treatment_reference) VALUES
('dis-late-blight', 'اللفحة المتأخرة', 'Late Blight', 'Phytophthora infestans', 'Oomycete', 'بقع مائية داكنة على الأوراق تتحول للبني مع نمو زغبي أبيض على السطح السفلي في الرطوبة العالية', 'Water-soaked irregular lesions turning brown/black with white mold growth under humid conditions', ARRAY['low', 'medium', 'high', 'severe'], 'استخدام مركبات النحاس وقائياً أو ميفينوكسام / دايميثومورف عند بدء الإصابة'),
('dis-early-blight', 'اللفحة المبكرة', 'Early Blight', 'Alternaria solani', 'Fungal', 'بقع بنية إلى سوداء ذات حلقات دائرية متداخلة (تشبه هدف الرماية) على الأوراق السفلية', 'Concentric dark brown target-like rings on mature leaves causing chlorosis and defoliation', ARRAY['low', 'medium', 'high'], 'الرش بمبيدات مانكوزيب أو كلوروثالونيل أو ديفينوكونازول مع تنظيم الري'),
('dis-powdery-mildew', 'البياض الدقيقي', 'Powdery Mildew', 'Leveillula taurica / Erysiphe necator', 'Fungal', 'طبقة دقيقة بيضاء تشبه الطحين على السطح العلوي أو السفلي للأوراق مع تجعد وجفاف', 'White talcum-powder-like patches on leaves causing leaf distortion and premature leaf drop', ARRAY['low', 'medium', 'high'], 'الرش بالكبريت الميكروني وقائياً ومبيدات التريازول مثل هكساكونازول علاجياً'),
('dis-coffee-rust', 'صدأ أوراق البن', 'Coffee Leaf Rust', 'Hemileia vastatrix', 'Fungal', 'بقع برتقالية دائرية مسحوقية مميزة على السطح السفلي لأوراق البن تسبب تساقطها', 'Yellowish-orange powdery powdery spots on the lower leaf surface leading to severe defoliation', ARRAY['low', 'medium', 'high', 'critical'], 'الرش بمركبات هيدروكسيد النحاس وقبل موسم الأمطار واستخدام أصناف مقاومة'),
('dis-tylcv', 'فيروس تجعد واصفرار أوراق الطماطم', 'Tomato Yellow Leaf Curl Virus', 'TYLCV (Begomovirus)', 'Viral', 'تقزم شديد للنبات وتجعد الأوراق للأعلى مع اصفرار الحواف وصغر حجم الثمار', 'Severe stunting, upward leaf curling, yellow leaf margins, and flower abortion transmitted by whitefly', ARRAY['medium', 'high', 'severe'], 'مكافحة الذبابة البيضاء الناقلة واستخدام شباك حماية وأصناف هجينة مقاومة'),
('dis-anthracnose', 'الأنثراكنوز (تبقع الثمار)', 'Anthracnose', 'Colletotrichum gloeosporioides', 'Fungal', 'بقع دائرية غائرة بنية إلى سوداء على الثمار الناضجة والأوراق والأغصان في المانجو والقهوة', 'Depressed circular dark lesions with concentric fungal spore rings on fruits and leaves', ARRAY['low', 'medium', 'high'], 'تقليم الأغصان المصابة والرش بأوكسي كلورور النحاس أو أزوكستروبين')
ON CONFLICT (id) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    scientific_name = EXCLUDED.scientific_name,
    symptoms_description_ar = EXCLUDED.symptoms_description_ar,
    symptoms_description_en = EXCLUDED.symptoms_description_en,
    treatment_reference = EXCLUDED.treatment_reference;

-- 6. Common Pests
INSERT INTO knowledge.pests (id, name_ar, name_en, scientific_name, pest_family, visual_features_ar, visual_features_en, seasonal_patterns, created_at) VALUES
('pest-tuta-absoluta', 'توتا أبسلوتا (حافرة أنفاق الطماطم)', 'Tomato Leafminer', 'Tuta absoluta', 'Gelechiidae', 'أنفاق وبقع عريضة شفافة بين بشرتي الورقة مع وجود يرقات صغيرة بيضاء/خضراء وبرازها الأسود', 'Mines and transparent blotches in leaves with tiny green/creamy larvae and black frass', 'تنشط في فترات الدفء والجفاف وتتكاثر بسرعة في البيوت المحمية والحقول المكشوفة', CURRENT_TIMESTAMP),
('pest-whitefly', 'الذبابة البيضاء', 'Silverleaf Whitefly', 'Bemisia tabaci', 'Aleyrodidae', 'حشرات بيضاء دقيقة تشبه العث الصغير تتطاير بكثافة عند تحريك النبات، وتفرز ندوة عسلية', 'Tiny white winged insects congregating on leaf undersides, secreting sticky honeydew', 'تنتشر في درجات الحرارة المعتدلة إلى المرتفعة من الربيع إلى الخريف وتعتبر ناقلاً رئيساً للفيروسات', CURRENT_TIMESTAMP),
('pest-aphids', 'حشرات المن', 'Aphids', 'Aphis gossypii / Myzus persicae', 'Aphididae', 'مستعمرات من حشرات صغيرة لينة الجسم خضراء أو سوداء تلتصق بالقمم النامية وبراعم النبات', 'Dense clusters of pear-shaped green, black or yellow sap-sucking nymphs on tender shoots', 'تتكاثر بغزارة في بداية الربيع والنموات الغضة وتفرز الندوة العسلية المسببة للعفن الأسود', CURRENT_TIMESTAMP),
('pest-coffee-borer', 'خنفساء حفار ثمار البن', 'Coffee Berry Borer', 'Hypothenemus hampei', 'Curculionidae', 'خنفساء سوداء دقيقة تثقب قمة حبة البن وتضع بيضها بالداخل مما يسبب تلف الحبة وتساقطها', 'Tiny black beetle boring a circular hole at the tip of the coffee berry causing internal bean rot', 'تنشط مع بدء نضج وتصلب حبوب البن وتختبئ في الحبوب المتبقية بعد الحصاد', CURRENT_TIMESTAMP),
('pest-red-palm-weevil', 'سوسة النخيل الحمراء', 'Red Palm Weevil', 'Rhynchophorus ferrugineus', 'Curculionidae', 'سوسة كبيرة الحجم بنية محمرة مع خرطوم مميز، تفرز يرقاتها سائلاً بنياً ذا رائحة كريهة داخل الجذع', 'Large reddish-brown snout beetle whose grubs hollow out the palm trunk emitting fermented odor', 'تنشط على مدار العام في مزارع النخيل وتهاجم الجروح وأماكن فصل الفسائل', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    scientific_name = EXCLUDED.scientific_name,
    visual_features_ar = EXCLUDED.visual_features_ar,
    visual_features_en = EXCLUDED.visual_features_en;

-- 7. Crop-Disease Mapping
INSERT INTO knowledge.crop_disease_map (crop_id, disease_id, prevalence) VALUES
('crop-tomato', 'dis-late-blight', 'high'),
('crop-tomato', 'dis-early-blight', 'high'),
('crop-tomato', 'dis-tylcv', 'high'),
('crop-tomato', 'dis-powdery-mildew', 'medium'),
('crop-potato', 'dis-late-blight', 'high'),
('crop-potato', 'dis-early-blight', 'high'),
('crop-grape', 'dis-powdery-mildew', 'high'),
('crop-grape', 'dis-anthracnose', 'medium'),
('crop-coffee', 'dis-coffee-rust', 'high'),
('crop-coffee', 'dis-anthracnose', 'medium'),
('crop-mango', 'dis-powdery-mildew', 'high'),
('crop-mango', 'dis-anthracnose', 'high')
ON CONFLICT DO NOTHING;

-- 8. Crop-Pest Mapping
INSERT INTO knowledge.crop_pest_map (crop_id, pest_id, prevalence) VALUES
('crop-tomato', 'pest-tuta-absoluta', 'high'),
('crop-tomato', 'pest-whitefly', 'high'),
('crop-tomato', 'pest-aphids', 'medium'),
('crop-potato', 'pest-aphids', 'medium'),
('crop-coffee', 'pest-coffee-borer', 'high'),
('crop-datepalm', 'pest-red-palm-weevil', 'high'),
('crop-mango', 'pest-whitefly', 'medium')
ON CONFLICT DO NOTHING;
