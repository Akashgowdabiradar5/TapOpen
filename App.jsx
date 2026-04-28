import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AuthPage from './pages/AuthPage'
import SeekerDashboard from './pages/SeekerDashboard'
import CompanyDashboard from './pages/CompanyDashboard'
import './index.css'

function App() {
  const token = localStorage.getItem('access');
  const role = localStorage.getItem('role');

  const ProtectedRoute = ({ children, requiredRole }) => {
    if (!token) return <Navigate to="/auth" />;
    if (requiredRole && role !== requiredRole) return <Navigate to="/" />;
    return children;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route 
          path="/seeker/*" 
          element={
            <ProtectedRoute requiredRole="SEEKER">
              <SeekerDashboard />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/company/*" 
          element={
            <ProtectedRoute requiredRole="COMPANY">
              <CompanyDashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
