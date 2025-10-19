import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom'; // <-- 1. Importar Link
import SampleFilter from './SampleFilter';

function MuestraList() {
  // Estado para almacenar la lista de muestras
  const [muestras, setMuestras] = useState([]);
  // Estado para manejar la carga
  const [loading, setLoading] = useState(true);
  // Estado para manejar errores
  const [error, setError] = useState(null);
  // Estado para manejar los filtros
  const [filters, setFilters] = useState({});

  // useEffect se ejecuta después de que el componente se monta en el DOM
  useEffect(() => {
    // Definimos una función asíncrona para obtener los datos
    const fetchMuestras = async () => {
      try {
        // Hacemos la petición GET a nuestra API.
        // Gracias al proxy en vite.config.js, '/api/muestras/' se redirigirá a 'http://127.0.0.1:8000/api/muestras/'
        const response = await axios.get('/api/muestras/');
        
        // Actualizamos el estado con los datos recibidos
        setMuestras(response.data);
        setError(null);
      } catch (err) {
        // Si hay un error, lo guardamos en el estado
        setError('Error al cargar los datos de las muestras.');
        console.error(err);
      } finally {
        // Indicamos que la carga ha terminado (ya sea con éxito o con error)
        setLoading(false);
      }
    };

    // Llamamos a la función para que se ejecute
    fetchMuestras();
  }, [filters]); // El array vacío [] significa que este efecto se ejecuta solo una vez, cuando el componente se monta.

  // --- Renderizado del componente ---

  if (loading) {
    return <p>Cargando muestras...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div>
	  {/* <h1 style={{ color: '#eee' }}>Monitor de Calidad de Energía</h1> */}
      <h2 style={{ color: '#eee' }}>Lista de Muestras</h2>

      {/* --- Renderiza el componente de filtro --- */}
      <SampleFilter onFilterChange={setFilters} />

      {muestras.length === 0 ? (
        <p style={{ color: '#ccc' }}>No hay muestras disponibles con los filtros actuales.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr style={{ backgroundColor: '#444' }}>
              <th style={tableHeaderStyle}>ID</th>
              <th style={tableHeaderStyle}>Event ID</th>
              <th style={tableHeaderStyle}>Fecha Captura</th>
              <th style={tableHeaderStyle}>Estado</th>
              <th style={tableHeaderStyle}>Fecha Procesamiento</th>
              <th style={tableHeaderStyle}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {muestras.map((muestra) => (
              <tr key={muestra.id} style={{ borderBottom: '1px solid #444' }}>
                <td style={tableCellStyle}>{muestra.id}</td>
                <td style={tableCellStyle}>{muestra.event_id}</td>
                <td style={tableCellStyle}>{new Date(muestra.timestamp_inicio).toLocaleString()}</td>
                <td style={{ ...tableCellStyle, color: getStatusColor(muestra.estado_procesamiento) }}>
                  {muestra.estado_procesamiento}
                </td>
                <td style={tableCellStyle}>
                  {muestra.fecha_procesamiento ? new Date(muestra.fecha_procesamiento).toLocaleString() : 'N/A'}
                </td>
                <td style={tableCellStyle}>
                  <Link to={`/muestras/${muestra.id}`} style={linkButtonStyle}>Ver Detalle</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// Estilos de tabla
const tableHeaderStyle = {
  padding: '12px 15px',
  textAlign: 'left',
  color: '#eee',
  fontSize: '0.9em',
  borderBottom: '2px solid #555'
};

const tableCellStyle = {
  padding: '10px 15px',
  textAlign: 'left',
  color: '#ccc',
  fontSize: '0.9em',
  borderBottom: '1px solid #333'
};

const linkButtonStyle = {
  backgroundColor: '#007bff',
  color: 'white',
  padding: '6px 10px',
  borderRadius: '4px',
  textDecoration: 'none',
  fontSize: '0.85em'
};

const getStatusColor = (status) => {
  switch (status) {
    case 'procesado':
      return 'lightgreen';
    case 'pendiente':
      return 'orange';
    case 'error':
      return 'red';
    default:
      return 'white';
  }
};

export default MuestraList;