// src/components/SampleFilter.jsx
import React, { useState } from 'react';

const TIPO_PERTURBACION_OPTIONS = [
    { value: '', label: 'Cualquier Tipo' },
    { value: 'sobretension', label: 'Sobretensión' },
    { value: 'caida_tension', label: 'Caída de Tensión' },
    { value: 'harmonicos', label: 'Armónicos' },
    { value: 'transitorio', label: 'Transitorio' },
    { value: 'falla_sistema', label: 'Falla del Sistema' },
    { value: 'normal', label: 'Normal' },
    { value: 'otros', label: 'Otros' },
];

function SampleFilter({ onFilterChange }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [perturbationFilter, setPerturbationFilter] = useState('');

    const handleApplyFilters = () => {
        const filters = {};
        if (searchTerm) filters.search = searchTerm;
        if (statusFilter) filters.estado_procesamiento = statusFilter;
        // Para el filtro de perturbación, necesitamos un endpoint especial en el backend
        // Por ahora, solo lo pasamos, pero el backend aún no lo soporta directamente en MuestraViewSet
        if (perturbationFilter) filters.tipo_perturbacion = perturbationFilter; 

        onFilterChange(filters);
    };

    const handleClearFilters = () => {
        setSearchTerm('');
        setStatusFilter('');
        setPerturbationFilter('');
        onFilterChange({}); // Envía un objeto vacío para limpiar todos los filtros
    };

    return (
        <div style={{ marginBottom: '22px', padding: '20px', border: '1px solid #444', borderRadius: '8px', backgroundColor: '#2a2a2a', color: '#eee' }}>
            <h3 style={{ marginTop: '0', marginBottom: '15px', color: '#eee' }}>Filtrar Muestras</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '15px' }}>

                {/* Búsqueda por Event ID */}
                <div>
                    <label htmlFor="search-term" style={{ display: 'block', marginBottom: '5px' }}>Buscar por Event ID:</label>
                    <input
                        id="search-term"
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Ej: 1760123..."
                        style={{ width: '100%', padding: '8px', border: '1px solid #555', borderRadius: '4px', backgroundColor: '#333', color: '#eee' }}
                    />
                </div>

                {/* Filtro por Estado de Procesamiento */}
                <div>
                    <label htmlFor="status-filter" style={{ display: 'block', marginBottom: '5px' }}>Estado:</label>
                    <select
                        id="status-filter"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        style={{ width: '100%', padding: '8px', border: '1px solid #555', borderRadius: '4px', backgroundColor: '#333', color: '#eee' }}
                    >
                        <option value="">Todos</option>
                        <option value="pendiente">Pendiente</option>
                        <option value="procesado">Procesado</option>
                        <option value="error">Error</option>
                    </select>
                </div>

                {/* Filtro por Tipo de Perturbación (Requiere mejora en el Backend) */}
                <div>
                    <label htmlFor="perturbation-filter" style={{ display: 'block', marginBottom: '5px' }}>Tipo de Perturbación:</label>
                    <select
                        id="perturbation-filter"
                        value={perturbationFilter}
                        onChange={(e) => setPerturbationFilter(e.target.value)}
                        style={{ width: '100%', padding: '8px', border: '1px solid #555', borderRadius: '4px', backgroundColor: '#333', color: '#eee' }}
                    >
                        {TIPO_PERTURBACION_OPTIONS.map(option => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                    </select>
                </div>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
                <button 
                    onClick={handleApplyFilters} 
                    style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                >
                    Aplicar Filtros
                </button>
                <button 
                    onClick={handleClearFilters} 
                    style={{ padding: '10px 15px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                >
                    Limpiar Filtros
                </button>
            </div>
        </div>
    );
}

export default SampleFilter;