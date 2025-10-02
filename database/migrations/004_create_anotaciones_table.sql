CREATE TABLE anotaciones (
    id SERIAL PRIMARY KEY,
    muestra_id INTEGER REFERENCES muestras(id) ON DELETE CASCADE,
    tipo_perturbacion VARCHAR(50) NOT NULL, -- Ej. 'Sobretensión', 'Caída', 'Armónicos'
    comentarios TEXT,                       -- Texto libre del anotador
    timestamp_inicio_region INTEGER,        -- Opcional: inicio de la perturbación en puntos de la muestra
    timestamp_fin_region INTEGER,           -- Opcional: fin de la perturbación en puntos de la muestra
    usuario_anotador_id INTEGER REFERENCES usuarios(id),
    fecha_anotacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices útiles
CREATE INDEX idx_anotaciones_muestra_id ON anotaciones (muestra_id);
CREATE INDEX idx_anotaciones_tipo_perturbacion ON anotaciones (tipo_perturbacion);