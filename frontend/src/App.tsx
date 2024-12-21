import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Chatbot from './components/Chatbot';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import TableVisualizer from './pages/TableVisualizer';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useState } from 'react';
import LoadingOverlayWrapper from 'react-loading-overlay-ts';
import { BarLoader } from 'react-spinners';


type TableWithSummaryItem = {
  plot: string;
  summary: string;
  table: string;
};

type TableWithSummary = TableWithSummaryItem[] | null;
function App() {
  const [tableWithSummary, setTableWithSummary] = useState<TableWithSummary>(null);
  const [isActive,setIsActive]=useState<boolean>(false);
  return (
    <LoadingOverlayWrapper active={isActive} spinner={<BarLoader/>} text="Parsing Response ...">
      <Router>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <Routes>
            <Route
              path="/"
              element={
                <Home
                  tableWithSummary={tableWithSummary}
                  setTableWithSummary={setTableWithSummary}
                  setIsActive={setIsActive}
                />
              }
            />
            <Route
              path="/dashboard"
              element={<Dashboard tableWithSummary={tableWithSummary} />}
            />
            <Route
              path="/table"
              element={<TableVisualizer tableWithSummary={tableWithSummary} />}
            />
          </Routes>
          <Chatbot tableWithSummary={tableWithSummary} />
          <ToastContainer />
        </div>
      </Router>
    </LoadingOverlayWrapper>
  );
}

export default App;
