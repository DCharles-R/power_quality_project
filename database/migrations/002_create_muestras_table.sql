CREATE TABLE muestras (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE NOT NULL, -- El ID que ya usas en InfluxDB
    timestamp_inicio TIMESTAMP NOT NULL,  -- Marca de tiempo del primer punto de la muestra
    duracion_ms INTEGER NOT NULL,         -- Duración total de la muestra en milisegundos
    frecuencia_muestreo_hz DECIMAL(10, 2) NOT NULL, -- Ej. 510 muestras/ciclo * 60 Hz = 30600 Hz
    num_puntos INTEGER NOT NULL DEFAULT 5120, -- Número de puntos capturados (ej. 5120)
    origen_hardware VARCHAR(50),          -- Ej. 'NUCLEO-H7S3L8 via ESP32'
    estado_procesamiento VARCHAR(20) DEFAULT 'pendiente' NOT NULL CHECK (estado_procesamiento IN ('pendiente', 'procesado', 'error')),
    fecha_procesamiento TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion_id INTEGER REFERENCES usuarios(id)
);

-- Índices útiles
CREATE INDEX idx_muestras_event_id ON muestras (event_id);
CREATE INDEX idx_muestras_timestamp_inicio ON muestras (timestamp_inicio);
CREATE INDEX idx_muestras_estado_procesamiento ON muestras (estado_procesamiento);