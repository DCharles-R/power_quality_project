import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';
import AnnotationPanel from './AnnotationPanel';

function MuestraDetail() {
  const { id } = useParams();

  // Estados para los datos de los gráficos y la información de la muestra
  const [muestra, setMuestra] = useState(null);
  const [signalData, setSignalData] = useState(null);
  // const [spectrogramData, setSpectrogramData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [anotaciones, setAnotaciones] = useState([]);
  
  // Función para recargar las anotaciones (útil después de guardar o eliminar)
  const fetchAnotations = async () => {
    try {
      // Filtramos las anotaciones por el ID de la muestra
      const response = await axios.get(`/api/anotaciones/?muestra=${id}`);
      setAnotaciones(response.data);
    } catch (err) {
      console.error("Error al cargar anotaciones:", err);
      // Puedes manejar el error de anotaciones de forma separada si no quieres que bloquee toda la página.
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
		setError(null);

		// Obtener detalles y señal en paralelo
        const [muestraRes, signalRes] = await Promise.all([
          axios.get(`/api/muestras/${id}/`),
          axios.get(`/api/muestras/${id}/signal-raw-data/`)
        ]);

        setMuestra(muestraRes.data);
        setSignalData({
          x: signalRes.data.x_data.map(ts => new Date(ts)),
          y: signalRes.data.y_data,
        });
		
		// Llamar a la nueva función para obtener anotaciones
        await fetchAnotations(); // <-- Obtener anotaciones al cargar

      } catch (err) {
        setError('Error al cargar los detalles de la muestra.');
        console.error("Error detallado:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]); // El efecto se vuelve a ejecutar si el 'id' de la URL cambia

  if (loading) {
    return <p>Cargando detalles y gráficos...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div>
      <h2>Detalle de la Muestra ID: {id}</h2>
      {muestra && (
        <div style={{ marginBottom: '20px' }}>
          <strong>Event ID:</strong> {muestra.event_id} <br />
          <strong>Estado:</strong> {muestra.estado_procesamiento} <br />
          <strong>Fecha de captura:</strong> {new Date(muestra.timestamp_inicio).toLocaleString()}
        </div>
      )}

      {/* --- Gráfico de la Señal en el Tiempo --- */}
	  {signalData && (
        <div style={{ marginBottom: '40px' }}>
          <h3>Señal en el Dominio del Tiempo</h3>
          <Plot
            data={[
              {
                x: signalData.x,
                y: signalData.y,
                // --- ¡CAMBIO CLAVE AQUÍ! ---
                type: 'scattergl', // Cambia 'scatter' por 'scattergl' para usar WebGL
                // -------------------------
                mode: 'lines',
                marker: { color: 'blue' },
                name: 'Voltaje',
                // Opcional: Para forzar que no se simplifique la línea
                line: { simplify: false }
              },
            ]}
            layout={{
              title: 'Forma de Onda de la Señal',
              xaxis: { title: 'Tiempo' },
              yaxis: { title: 'Amplitud' },
              autosize: true,
            }}
            style={{ width: '100%', height: '400px' }}
            config={{ responsive: true }}
          />
        </div>
      )}

      {/* --- Gráfico del Espectrograma (Heatmap) --- */}
	  {muestra.estado_procesamiento === 'procesado' && (
        <div>
          <h3>Espectrograma (Transformada de Stockwell)</h3>
          <img 
            src={`/api/muestras/${id}/espectrograma-image/`} 
            alt={`Espectrograma para la muestra ${id}`}
            style={{ maxWidth: '100%', height: 'auto' }}
          />
        </div>
      )}
	  
	  {/* --- Añadir el Panel de Anotación y pasarle las anotaciones --- */}
	  {muestra && (
        <AnnotationPanel 
          muestraId={muestra.id} 
          anotacionesExistentes={anotaciones} // <-- Pasar las anotaciones
          onAnnotationSaved={fetchAnotations} // <-- Recargar anotaciones cuando se guarde una nueva
        />
      )}

	<br />
      <Link to="/" style={{ marginTop: '20px', display: 'inline-block' }}>Volver a la lista</Link>
    </div>
  );
}

export default MuestraDetail;