import { Routes, Route } from 'react-router-dom'; // <-- 1. Importar Routes y Route
import MuestraList from './components/MuestraList';
import MuestraDetail from './components/MuestraDetail'; // <-- 2. Importar el nuevo componente
import './App.css';

function App() {
  return (
    <div className="App" style={{ padding: '20px' }}>
      <header className="App-header">
        <h1>Monitor de Calidad de Energía</h1>
      </header>
      <main>
	      <Routes> {/* <-- 3. Usar Routes para definir las rutas */}
          <Route path="/" element={<MuestraList />} />
          <Route path="/muestras/:id" element={<MuestraDetail />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;