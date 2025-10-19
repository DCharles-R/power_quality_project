// src/components/AnnotationPanel.jsx
import React, { useState, useEffect } from 'react'; // Importar useEffect
import axios from 'axios';

const TIPO_DISPLAY_MAP = {
  sobretension: 'Sobretensión',
  caida_tension: 'Caída de Tensión',
  harmonicos: 'Armónicos',
  transitorio: 'Transitorio',
  falla_sistema: 'Falla del Sistema',
  normal: 'Normal',
  otros: 'Otros',
};

// Recibimos las anotaciones existentes y la función para recargarlas
function AnnotationPanel({ muestraId, anotacionesExistentes, onAnnotationSaved }) {
  const [tipoPerturbacion, setTipoPerturbacion] = useState('sobretension');
  const [comentarios, setComentarios] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editingAnnotationId, setEditingAnnotationId] = useState(null); // Para saber qué anotación se edita

  // Usamos useEffect para pre-llenar el formulario si estamos editando
  useEffect(() => {
    if (editingAnnotationId) {
      const annotationToEdit = anotacionesExistentes.find(
        (ann) => ann.id === editingAnnotationId
      );
      if (annotationToEdit) {
        setTipoPerturbacion(annotationToEdit.tipo_perturbacion);
        setComentarios(annotationToEdit.comentarios);
        setError(null);
        setSuccess(null);
      }
    } else {
      // Si no estamos editando, limpiamos el formulario
      setTipoPerturbacion('sobretension');
      setComentarios('');
      setError(null);
      setSuccess(null);
    }
  }, [editingAnnotationId, anotacionesExistentes]); // Dependencias del efecto

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const payload = {
        muestra: muestraId,
        tipo_perturbacion: tipoPerturbacion,
        comentarios: comentarios,
      };

      if (editingAnnotationId) {
        // Si estamos editando, hacemos una petición PUT/PATCH
        await axios.put(`/api/anotaciones/${editingAnnotationId}/`, payload);
        setSuccess('¡Anotación actualizada exitosamente!');
      } else {
        // Si no, creamos una nueva
        await axios.post('/api/anotaciones/', payload);
        setSuccess('¡Anotación guardada exitosamente!');
      }

      // Limpiar el formulario y resetear el estado de edición
      setComentarios('');
      setEditingAnnotationId(null); 

      // Recargar las anotaciones en el componente padre
      if (onAnnotationSaved) {
        onAnnotationSaved();
      }

    } catch (err) {
      setError('Error al guardar/actualizar la anotación.');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (annotationId) => {
    setEditingAnnotationId(annotationId); // Establece la anotación que se va a editar
  };

  const handleCancelEdit = () => {
    setEditingAnnotationId(null); // Cancela la edición
  };

  const handleDelete = async (annotationId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta anotación?')) {
      try {
        await axios.delete(`/api/anotaciones/${annotationId}/`);
        setSuccess('¡Anotación eliminada exitosamente!');
        if (onAnnotationSaved) {
          onAnnotationSaved(); // Recargar anotaciones
        }
      } catch (err) {
        setError('Error al eliminar la anotación.');
        console.error(err);
      }
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px', marginTop: '40px', backgroundColor: '#333' }}>
      <h3>{editingAnnotationId ? 'Editar Anotación' : 'Anotar Muestra'}</h3>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="tipo-perturbacion" style={{ display: 'block', marginBottom: '5px', color: '#eee' }}>
            Tipo de Perturbación:
          </label>
          <select
            id="tipo-perturbacion"
            value={tipoPerturbacion}
            onChange={(e) => setTipoPerturbacion(e.target.value)}
            style={{ width: '100%', padding: '8px', backgroundColor: '#555', color: '#eee', border: '1px solid #777' }}
          >
            <option value="sobretension">Sobretensión</option>
            <option value="caida_tension">Caída de Tensión</option>
            <option value="harmonicos">Armónicos</option>
            <option value="transitorio">Transitorio</option>
            <option value="falla_sistema">Falla del Sistema</option>
            <option value="normal">Normal</option>
            <option value="otros">Otros</option>
          </select>
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="comentarios" style={{ display: 'block', marginBottom: '5px', color: '#eee' }}>
            Comentarios:
          </label>
          <textarea
            id="comentarios"
            value={comentarios}
            onChange={(e) => setComentarios(e.target.value)}
            rows="4"
            style={{ width: '100%', padding: '8px', backgroundColor: '#555', color: '#eee', border: '1px solid #777' }}
            placeholder="Añade detalles adicionales sobre la perturbación..."
          />
        </div>
        <button type="submit" disabled={isSubmitting} style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', marginRight: '10px' }}>
          {isSubmitting ? 'Guardando...' : (editingAnnotationId ? 'Actualizar Anotación' : 'Guardar Anotación')}
        </button>
        {editingAnnotationId && (
          <button type="button" onClick={handleCancelEdit} style={{ padding: '10px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
            Cancelar Edición
          </button>
        )}
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
        {success && <p style={{ color: 'green', marginTop: '10px' }}>{success}</p>}
      </form>

      {/* --- Lista de Anotaciones Existentes --- */}
      {anotacionesExistentes && anotacionesExistentes.length > 0 && (
        <div style={{ marginTop: '40px', paddingTop: '20px', borderTop: '1px solid #555' }}>
          <h3>Anotaciones Existentes ({anotacionesExistentes.length})</h3>
          {anotacionesExistentes.map((anotacion) => (
            <div key={anotacion.id} style={{ border: '1px solid #777', borderRadius: '5px', padding: '15px', marginBottom: '15px', backgroundColor: '#444', color: '#eee' }}>
              <p><strong>Tipo:</strong> {TIPO_DISPLAY_MAP[anotacion.tipo_perturbacion] || anotacion.tipo_perturbacion}</p>
              <p><strong>Comentarios:</strong> {anotacion.comentarios}</p>
              <p><strong>Fecha:</strong> {new Date(anotacion.fecha_anotacion).toLocaleString()}</p>
              {/* Si el backend devuelve el nombre de usuario, lo mostramos */}
              {anotacion.usuario_creacion_nombre && <p><strong>Por:</strong> {anotacion.usuario_creacion_nombre}</p>}

              <div style={{ marginTop: '10px' }}>
                <button onClick={() => handleEdit(anotacion.id)} style={{ padding: '8px 12px', backgroundColor: '#ffc107', color: 'black', border: 'none', borderRadius: '5px', cursor: 'pointer', marginRight: '10px' }}>
                  Editar
                </button>
                <button onClick={() => handleDelete(anotacion.id)} style={{ padding: '8px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AnnotationPanel;