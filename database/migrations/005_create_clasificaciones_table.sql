CREATE TABLE clasificaciones (
    id SERIAL PRIMARY KEY,
    muestra_id INTEGER UNIQUE REFERENCES muestras(id) ON DELETE CASCADE,
    clase_manual VARCHAR(50),              -- La clase "verdad" asignada por el experto (humano)
    clase_modelo VARCHAR(50),              -- La clase predicha por el modelo de RN
    confianza_modelo DECIMAL(5, 4),        -- Confianza de la predicción del modelo (0.0000 - 1.0000)
    estado_clasificacion VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_clasificacion IN ('pendiente', 'validada', 'rechazada', 'modelo_aplicado')),
    usuario_validador_id INTEGER REFERENCES usuarios(id), -- Quién validó la clase manual
    fecha_clasificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version_modelo VARCHAR(20)             -- Versión del modelo de RN que hizo la predicción
);

-- Índices útiles
CREATE INDEX idx_clasificaciones_muestra_id ON clasificaciones (muestra_id);
CREATE INDEX idx_clasificaciones_clase_manual ON clasificaciones (clase_manual);
CREATE INDEX idx_clasificaciones_clase_modelo ON clasificaciones (clase_modelo);