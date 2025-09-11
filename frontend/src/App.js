import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import UploadCV from './pages/UploadCV';
import CandidateProfile from './pages/CandidateProfile';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadCV />} />
            <Route path="/candidate/:id" element={<CandidateProfile />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
