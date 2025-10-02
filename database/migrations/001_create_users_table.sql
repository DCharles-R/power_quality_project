CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) DEFAULT 'anotador' NOT NULL CHECK (rol IN ('admin', 'anotador', 'visor')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices útiles
CREATE INDEX idx_usuarios_username ON usuarios (username);
CREATE INDEX idx_usuarios_email ON usuarios (email);