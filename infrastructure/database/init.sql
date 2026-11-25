-- AgriVision AI Database Initialization Script
-- Target Database: agrivision

\connect agrivision;

-- Enable PostGIS Spatial Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create Domain Schemas
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS knowledge;
CREATE SCHEMA IF NOT EXISTS studio;

-- Schema Comments
COMMENT ON SCHEMA public IS 'Standard application core tables (users, farms, fields, auth, notifications)';
COMMENT ON SCHEMA ai IS 'AI inference runs, model registry, image feature vectors, diagnostic logs';
COMMENT ON SCHEMA knowledge IS 'Agricultural agronomy knowledge base, pesticide active ingredients, crop disease catalogs';
COMMENT ON SCHEMA studio IS 'AI Studio research datasets, annotation tasks, ground truth evaluations, benchmarks';

-- Basic Tables in public schema
CREATE TABLE IF NOT EXISTS public.roles (
    id VARCHAR(50) PRIMARY KEY,
    name_en VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.governorates (
    id VARCHAR(50) PRIMARY KEY,
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(Point, 4326),
    major_agricultural_areas TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role_id VARCHAR(50) REFERENCES public.roles(id),
    governorate_id VARCHAR(50) REFERENCES public.governorates(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    governorate_id VARCHAR(50) REFERENCES public.governorates(id),
    district_name VARCHAR(150),
    total_area_hectares DOUBLE PRECISION,
    location_point GEOMETRY(Point, 4326),
    boundary_polygon GEOMETRY(Polygon, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Basic Tables in knowledge schema
CREATE TABLE IF NOT EXISTS knowledge.crops (
    id VARCHAR(50) PRIMARY KEY,
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    growing_seasons TEXT[],
    common_regions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge.growth_stages (
    id VARCHAR(50) PRIMARY KEY,
    crop_id VARCHAR(50) REFERENCES knowledge.crops(id) ON DELETE CASCADE,
    stage_order INT NOT NULL,
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    description TEXT,
    typical_duration_days INT
);

CREATE TABLE IF NOT EXISTS knowledge.diseases (
    id VARCHAR(50) PRIMARY KEY,
    name_ar VARCHAR(150) NOT NULL,
    name_en VARCHAR(150) NOT NULL,
    scientific_name VARCHAR(200),
    pathogen_type VARCHAR(50), -- Fungal, Bacterial, Viral, Oomycete, Physiological
    symptoms_description_ar TEXT,
    symptoms_description_en TEXT,
    severity_levels TEXT[],
    treatment_reference TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge.pests (
    id VARCHAR(50) PRIMARY KEY,
    name_ar VARCHAR(150) NOT NULL,
    name_en VARCHAR(150) NOT NULL,
    scientific_name VARCHAR(200),
    pest_family VARCHAR(100),
    visual_features_ar TEXT,
    visual_features_en TEXT,
    seasonal_patterns TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge.crop_disease_map (
    crop_id VARCHAR(50) REFERENCES knowledge.crops(id) ON DELETE CASCADE,
    disease_id VARCHAR(50) REFERENCES knowledge.diseases(id) ON DELETE CASCADE,
    prevalence VARCHAR(50) DEFAULT 'medium',
    PRIMARY KEY (crop_id, disease_id)
);

CREATE TABLE IF NOT EXISTS knowledge.crop_pest_map (
    crop_id VARCHAR(50) REFERENCES knowledge.crops(id) ON DELETE CASCADE,
    pest_id VARCHAR(50) REFERENCES knowledge.pests(id) ON DELETE CASCADE,
    prevalence VARCHAR(50) DEFAULT 'medium',
    PRIMARY KEY (crop_id, pest_id)
);

-- Basic Tables in ai schema
CREATE TABLE IF NOT EXISTS ai.models (
    id VARCHAR(100) PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- classification, object_detection, ocr, segmentation
    framework VARCHAR(50) DEFAULT 'PyTorch',
    artifact_url TEXT NOT NULL,
    input_shape INT[],
    metrics JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai.inferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id),
    crop_id VARCHAR(50) REFERENCES knowledge.crops(id),
    image_url TEXT NOT NULL,
    device_mode VARCHAR(50) DEFAULT 'server', -- phone, server, hybrid
    model_id VARCHAR(100) REFERENCES ai.models(id),
    predictions JSONB NOT NULL,
    confidence_score DOUBLE PRECISION,
    latency_ms INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Basic Tables in studio schema
CREATE TABLE IF NOT EXISTS studio.datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    license VARCHAR(100),
    num_samples INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS studio.samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID REFERENCES studio.datasets(id) ON DELETE CASCADE,
    sample_id VARCHAR(100) UNIQUE NOT NULL,
    crop_id VARCHAR(50) REFERENCES knowledge.crops(id),
    disease_id VARCHAR(50) REFERENCES knowledge.diseases(id),
    pest_id VARCHAR(50) REFERENCES knowledge.pests(id),
    image_path TEXT NOT NULL,
    capture_date DATE,
    governorate_id VARCHAR(50) REFERENCES public.governorates(id),
    growth_stage VARCHAR(50),
    severity_label VARCHAR(50),
    annotation_status VARCHAR(50) DEFAULT 'unverified',
    annotator_id UUID REFERENCES public.users(id),
    reviewer_id UUID REFERENCES public.users(id),
    source VARCHAR(100),
    license VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Spatial Indexes
CREATE INDEX IF NOT EXISTS idx_governorates_geom ON public.governorates USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_farms_location_point ON public.farms USING GIST (location_point);
CREATE INDEX IF NOT EXISTS idx_farms_boundary_polygon ON public.farms USING GIST (boundary_polygon);
CREATE INDEX IF NOT EXISTS idx_inferences_user_id ON ai.inferences (user_id);
CREATE INDEX IF NOT EXISTS idx_samples_crop_disease ON studio.samples (crop_id, disease_id);
