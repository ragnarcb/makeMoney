-- PostgreSQL Database Initialization Script
-- For Video Generator and Voice Cloning Integration

-- Create database if it doesn't exist (run this as superuser)
-- CREATE DATABASE video_voice_integration;

-- Connect to the database
-- \c video_voice_integration;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types for status tracking
CREATE TYPE video_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE voice_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Create voice_mappings table (replaces the JSON config)
CREATE TABLE voice_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    voice_id VARCHAR(50) UNIQUE NOT NULL,
    voice_name VARCHAR(100) NOT NULL,
    voice_file VARCHAR(255) NOT NULL,
    description TEXT,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    language VARCHAR(10) NOT NULL,
    quality VARCHAR(20) CHECK (quality IN ('low', 'medium', 'high')),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255),
    description TEXT,
    background_video_path VARCHAR(500),
    output_video_path VARCHAR(500),
    whatsapp_images_paths TEXT[], -- Array of image paths from whatsapp-clone service
    status video_status DEFAULT 'pending',
    metadata JSONB, -- Store additional video metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create voices table (for voice cloning requests)
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    voice_mapping_id UUID REFERENCES voice_mappings(id),
    character_name VARCHAR(100),
    text_content TEXT NOT NULL,
    output_audio_path VARCHAR(500),
    is_local_storage BOOLEAN DEFAULT TRUE,
    remote_storage_path VARCHAR(500),
    status voice_status DEFAULT 'pending',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create settings table (for global configuration)
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default voice mappings from the JSON config
INSERT INTO voice_mappings (voice_id, voice_name, voice_file, description, gender, language, quality, is_default) VALUES
('aluno', 'Student Voice', 'voices/voz_aluno_lucas.wav', 'Voice for student character', 'male', 'pt-br', 'high', FALSE),
('professora', 'Teacher Voice', 'voices/voz_referencia_convertida_ffmpeg.wav', 'Voice for teacher character', 'female', 'pt-br', 'high', FALSE),
('default', 'Default Voice', 'voices/Vídeo sem título ‐ Feito com o Clipchamp.wav', 'Default voice for any character without specific mapping', 'female', 'pt-br', 'medium', TRUE);

-- Insert default settings
INSERT INTO settings (setting_key, setting_value, description) VALUES
('auto_detect_voices', 'true', 'Automatically detect available voices'),
('default_language', 'pt-br', 'Default language for voice processing'),
('fallback_to_default', 'true', 'Fallback to default voice if specific voice not found'),
('voice_quality_threshold', 'medium', 'Minimum quality threshold for voice processing');

-- Create indexes for better performance
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created_at ON videos(created_at);
CREATE INDEX idx_voices_video_id ON voices(video_id);
CREATE INDEX idx_voices_status ON voices(status);
CREATE INDEX idx_voices_voice_mapping_id ON voices(voice_mapping_id);
CREATE INDEX idx_voice_mappings_voice_id ON voice_mappings(voice_id);
CREATE INDEX idx_voice_mappings_is_default ON voice_mappings(is_default);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voices_updated_at BEFORE UPDATE ON voices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voice_mappings_updated_at BEFORE UPDATE ON voice_mappings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for video processing status
CREATE VIEW video_processing_status AS
SELECT 
    v.id as video_id,
    v.title,
    v.status as video_status,
    v.created_at as video_created_at,
    COUNT(vo.id) as total_voices,
    COUNT(CASE WHEN vo.status = 'completed' THEN 1 END) as completed_voices,
    COUNT(CASE WHEN vo.status = 'failed' THEN 1 END) as failed_voices,
    COUNT(CASE WHEN vo.status IN ('pending', 'processing') THEN 1 END) as pending_voices
FROM videos v
LEFT JOIN voices vo ON v.id = vo.video_id
GROUP BY v.id, v.title, v.status, v.created_at;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres; 