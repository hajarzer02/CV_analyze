import React, { useState } from 'react';
import { FileSearch, Users, TrendingUp, Zap, Star, Shield, Target, Brain, CheckCircle, BarChart3, Clock, Award } from 'lucide-react';

const CVAnalyzerWelcome = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false); // This would come from your auth context

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-700"></div>
        <div className="absolute bottom-20 left-40 w-80 h-80 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
      </div>
      
      {/* Floating particles */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-white rounded-full opacity-60 animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-3 h-3 bg-purple-300 rounded-full opacity-40 animate-float-delayed"></div>
        <div className="absolute top-1/2 left-3/4 w-2 h-2 bg-blue-300 rounded-full opacity-50 animate-float-slow"></div>
        <div className="absolute bottom-1/4 right-1/3 w-1 h-1 bg-indigo-300 rounded-full opacity-70 animate-float"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-6 py-12">
        <div className="glass-effect rounded-3xl overflow-hidden flex flex-col lg:flex-row max-w-7xl w-full shadow-2xl animate-pulse-glow">
          
          {/* Left Panel - Branding & Features */}
          <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 text-white p-12 flex flex-col justify-center items-center lg:w-1/2 relative animate-slide-in-left">
            
            {/* Decorative elements */}
            <div className="absolute top-0 left-0 w-full h-full">
              <div className="absolute top-10 right-10 w-20 h-20 border-2 border-white border-opacity-20 rounded-full animate-float"></div>
              <div className="absolute bottom-20 left-10 w-16 h-16 border-2 border-white border-opacity-20 rounded-full animate-float-delayed"></div>
            </div>
            
            <div className="relative z-10 text-center">
              {/* Enhanced Logo with CV theme */}
              <div className="mb-8 relative">
                <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto animate-float backdrop-blur-sm">
                  <img 
                    src="/LOGapp.svg" 
                    alt="CV Analyzer Logo" 
                    className="w-12 h-12 object-contain filter drop-shadow-lg"
                  />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full animate-pulse flex items-center justify-center shadow-lg">
                  <Brain className="w-4 h-4 text-white" />
                </div>
              </div>
              
              <h1 className="text-5xl font-extrabold mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-blue-200 to-purple-200 drop-shadow-2xl">
                  CV Analyzer Pro
                </span>
              </h1>

              <p className="text-xl text-indigo-100 mb-8">Intelligence artificielle pour le recrutement moderne</p>
              
              {/* Feature highlights with CV analysis theme */}
              <div className="space-y-4 text-left max-w-sm">
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                    <FileSearch className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Analyse automatique des CV</span>
                </div>
                
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <Target className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Matching intelligent des profils</span>
                </div>
                
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Tableaux de bord RH</span>
                </div>
                
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Traitement en temps réel</span>
                </div>
              </div>

              {/* Stats Section */}
              <div className="mt-8 grid grid-cols-2 gap-4 text-center">
                <div className="glass-effect p-4 rounded-lg">
                  <div className="text-2xl font-bold text-white">99.2%</div>
                  <div className="text-xs text-indigo-200">Précision</div>
                </div>
                <div className="glass-effect p-4 rounded-lg">
                  <div className="text-2xl font-bold text-white">3s</div>
                  <div className="text-xs text-indigo-200">Analyse</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Welcome & Actions */}
          <div className="bg-white bg-opacity-95 p-12 flex flex-col justify-center lg:w-1/2 relative animate-slide-in-right">
            
            {/* Decorative gradient */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-400 to-indigo-600 rounded-full opacity-10 -translate-y-16 translate-x-16"></div>
            
            <div className="relative z-10">
              <div className="mb-8">
                <h2 className="text-4xl font-bold text-gray-800 mb-4">
                  Bienvenue dans l'avenir du recrutement
                  <span className="inline-block animate-bounce ml-2">🚀</span>
                </h2>
                <div className="w-20 h-1 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full mb-6"></div>
                <p className="text-gray-600 text-lg leading-relaxed">
                  Transformez votre processus de recrutement avec notre IA avancée. Analysez, comparez et 
                  sélectionnez les meilleurs candidats en quelques secondes avec une précision inégalée.
                </p>
              </div>

              {/* Key Benefits */}
              <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3 p-3 rounded-lg bg-gradient-to-r from-emerald-50 to-blue-50 border border-emerald-200">
                  <CheckCircle className="w-5 h-5 text-emerald-600" />
                  <span className="text-sm text-gray-700">Gain de temps 10x</span>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
                  <Star className="w-5 h-5 text-blue-600" />
                  <span className="text-sm text-gray-700">Taux de succès 95%</span>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200">
                  <Shield className="w-5 h-5 text-purple-600" />
                  <span className="text-sm text-gray-700">Données sécurisées</span>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-lg bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200">
                  <Award className="w-5 h-5 text-orange-600" />
                  <span className="text-sm text-gray-700">Certifié ISO 27001</span>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="space-y-4">
                {isAuthenticated ? (
                  // Dashboard button if user is authenticated
                  <button
                    className="group w-full px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 text-white font-semibold rounded-xl hover:from-emerald-700 hover:to-green-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center space-x-2"
                    onClick={() => console.log('Navigate to dashboard')}
                  >
                    <BarChart3 className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    <span>Accéder au Dashboard</span>
                  </button>
                ) : (
                  <>
                    {/* Login button */}
                    <button
                      className="group w-full px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center space-x-2"
                      onClick={() => console.log('Navigate to login')}
                    >
                      <FileSearch className="w-5 h-5 group-hover:scale-110 transition-transform" />
                      <span>Commencer l'analyse</span>
                    </button>

                    {/* Register button */}
                    <button
                      className="group w-full px-8 py-4 border-2 border-indigo-600 text-indigo-600 font-semibold rounded-xl hover:bg-indigo-50 transition-all duration-300 flex items-center justify-center space-x-2 transform hover:-translate-y-1"
                      onClick={() => console.log('Navigate to register')}
                    >
                      <Users className="w-5 h-5 group-hover:scale-110 transition-transform" />
                      <span>Créer un compte</span>
                    </button>
                  </>
                )}

                {/* Demo button */}
                <button
                  className="group w-full px-8 py-4 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 font-semibold rounded-xl hover:from-gray-200 hover:to-gray-300 transition-all duration-300 flex items-center justify-center space-x-2 border border-gray-300"
                  onClick={() => console.log('Start demo')}
                >
                  <Clock className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span>Essai gratuit (7 jours)</span>
                </button>
              </div>

              {/* Trust indicators */}
              <div className="mt-8 text-center">
                <p className="text-sm text-gray-500 mb-4">Approuvé par 500+ entreprises</p>
                <div className="flex justify-center items-center space-x-6 text-xs text-gray-400">
                  <div className="flex items-center space-x-1">
                    <Shield className="w-3 h-3" />
                    <span>SOC 2 Type II</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Shield className="w-3 h-3" />
                    <span>GDPR Conforme</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Award className="w-3 h-3" />
                    <span>ISO 27001</span>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-8 text-center">
                <p className="text-xs text-gray-400">
                  © 2025 CV Analyzer Pro. Tous droits réservés.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom Styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
        
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-6px); }
        }
        
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
          50% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.6); }
        }
        
        @keyframes slideInLeft {
          0% { transform: translateX(-100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInRight {
          0% { transform: translateX(100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        
        .animate-float { animation: float 3s ease-in-out infinite; }
        .animate-float-delayed { animation: float-delayed 4s ease-in-out infinite; }
        .animate-float-slow { animation: float-slow 5s ease-in-out infinite; }
        .animate-pulse-glow { animation: pulse-glow 2s ease-in-out infinite; }
        .animate-slide-in-left { animation: slideInLeft 0.8s ease-out; }
        .animate-slide-in-right { animation: slideInRight 0.8s ease-out; }
        
        .glass-effect {
          backdrop-filter: blur(10px);
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .feature-card {
          transform: scale(1);
          transition: all 0.3s ease;
        }
        
        .feature-card:hover {
          transform: scale(1.05);
        }
        
        @media (prefers-reduced-motion: reduce) {
          .animate-float, .animate-float-delayed, .animate-float-slow, 
          .animate-pulse, .animate-pulse-glow, .animate-bounce {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
};

export default CVAnalyzerWelcome;