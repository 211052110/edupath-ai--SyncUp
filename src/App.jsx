import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import LoanScore from './pages/LoanScore';
import ROICalculator from './pages/ROICalculator';
import VisaChat from './pages/VisaChat';
import CareerInsights from './pages/CareerInsights';
import UniversityQA from './pages/UniversityQA';
import SkillGap from './pages/SkillGap';
import CareerSimulator from './pages/CareerSimulator';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"        element={<Dashboard />} />
          <Route path="loan-score"       element={<LoanScore />} />
          <Route path="roi-calculator"   element={<ROICalculator />} />
          <Route path="visa-chat"        element={<VisaChat />} />
          <Route path="career-insights"  element={<CareerInsights />} />
          <Route path="university-qa"    element={<UniversityQA />} />
          <Route path="skill-gap"        element={<SkillGap />} />
          <Route path="career-simulator" element={<CareerSimulator />} />
        </Route>
      </Routes>
    </Router>
  );
}
export default App;
