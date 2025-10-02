CREATE TABLE espectrogramas (
    id SERIAL PRIMARY KEY,
    muestra_id INTEGER UNIQUE REFERENCES muestras(id) ON DELETE CASCADE, -- Enlace a la tabla muestras
    data_espectrograma BYTEA NOT NULL, -- Almacena la matriz 2D de la ST como un array de bytes
    metadata_json JSONB,              -- Metadatos adicionales (ej. dimensiones de la matriz, rango de freqs)
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices útiles
CREATE INDEX idx_espectrogramas_muestra_id ON espectrogramas (muestra_id);