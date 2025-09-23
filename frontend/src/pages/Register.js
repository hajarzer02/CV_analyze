import React, { useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, AlertCircle, CheckCircle, FileText, Users, BarChart3, Shield, Target, Zap, Brain, Award } from 'lucide-react';
import { register } from '../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [focusedField, setFocusedField] = useState(null);
  
  const navigate = useNavigate();
  const formRef = useRef(null);

  const validateForm = () => {
    const newErrors = {};
    
    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Le nom est requis';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Le nom doit contenir au moins 2 caractères';
    }
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Veuillez entrer une adresse email valide';
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre';
    }
    
    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Veuillez confirmer votre mot de passe';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleInputFocus = (fieldName) => {
    setFocusedField(fieldName);
  };

  const handleInputBlur = () => {
    setFocusedField(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.target.type !== 'submit') {
      e.preventDefault();
      const form = e.target.form;
      const formElements = Array.from(form.elements);
      const currentIndex = formElements.indexOf(e.target);
      const nextElement = formElements[currentIndex + 1];
      
      if (nextElement) {
        nextElement.focus();
      } else {
        form.querySelector('button[type="submit"]')?.focus();
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      await register(formData.name.trim(), formData.email, formData.password);
      
      setMessage({ 
        type: 'success', 
        text: 'Inscription réussie ! Veuillez vous connecter.' 
      });
      
      // Redirect to login after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Échec de l\'inscription. Veuillez réessayer.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 relative overflow-hidden">
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-72 h-72 bg-emerald-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-teal-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-700"></div>
        <div className="absolute bottom-20 left-40 w-80 h-80 bg-green-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
      </div>
      
      {/* Floating particles */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-white rounded-full opacity-60 animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-3 h-3 bg-emerald-300 rounded-full opacity-40 animate-float-delayed"></div>
        <div className="absolute top-1/2 left-3/4 w-2 h-2 bg-teal-300 rounded-full opacity-50 animate-float-slow"></div>
        <div className="absolute bottom-1/4 right-1/3 w-1 h-1 bg-green-300 rounded-full opacity-70 animate-float"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-6 py-12">
        <div className="glass-effect rounded-3xl overflow-hidden flex flex-col lg:flex-row max-w-7xl w-full shadow-2xl animate-pulse-glow">
          
          {/* Left Panel - Branding & Features */}
          <div className="bg-gradient-to-br from-emerald-600 via-green-600 to-emerald-800 text-white p-12 flex flex-col justify-center items-center lg:w-1/2 relative animate-slide-in-left">
            
            {/* Decorative elements */}
            <div className="absolute top-0 left-0 w-full h-full">
              <div className="absolute bottom-20 left-10 w-16 h-16 border-2 border-white border-opacity-20 rounded-full animate-float-delayed"></div>
            </div>
            
            <div className="relative z-10 text-center">
              {/* Enhanced Logo with CV theme */}
              <div className="mb-8 relative">
                <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto animate-float backdrop-blur-sm">
                  <FileText className="w-12 h-12 text-white filter drop-shadow-lg" />
                </div>
              </div>
              
              <h1 className="text-5xl font-extrabold mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-emerald-200 to-green-200 drop-shadow-2xl">
                  CV Analyzer 
                </span>
              </h1>

              <p className="text-xl text-emerald-100 mb-8">Intelligence artificielle pour le recrutement moderne</p>
              
              {/* Feature highlights with CV analysis theme */}
              <div className="space-y-4 text-left max-w-sm">
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center">
                    <FileText className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Analyse automatique des CV</span>
                </div>
                
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-teal-500 rounded-full flex items-center justify-center">
                    <Target className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm">Matching intelligent des profils</span>
                </div>
                
                <div className="flex items-center space-x-3 feature-card p-3 rounded-lg glass-effect transition-all duration-300 hover:scale-105">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
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
                  <div className="text-xs text-emerald-200">Précision</div>
                </div>
                <div className="glass-effect p-4 rounded-lg">
                  <div className="text-2xl font-bold text-white">3s</div>
                  <div className="text-xs text-emerald-200">Analyse</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel - Registration Form */}
          <div className="bg-white bg-opacity-95 p-12 flex flex-col justify-center lg:w-1/2 relative animate-slide-in-right">
            
            {/* Decorative gradient */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-400 to-green-600 rounded-full opacity-10 -translate-y-16 translate-x-16"></div>
            
            <div className="relative z-10">
              <div className="mb-8">
                <h2 className="text-4xl font-bold text-gray-800 mb-4">
                  Créer votre compte
                  <span className="inline-block animate-bounce ml-2">🚀</span>
          </h2>
                <div className="w-20 h-1 bg-gradient-to-r from-emerald-500 to-green-500 rounded-full mb-6"></div>
                <p className="text-gray-600 text-lg leading-relaxed">
                  Rejoignez notre plateforme et commencez à analyser des CV avec notre IA avancée.
          </p>
        </div>
        
              {/* Registration Form */}
              <form 
                className="space-y-6" 
                onSubmit={handleSubmit} 
                ref={formRef}
                role="form"
                aria-label="Formulaire d'inscription"
                noValidate
              >
            {/* Name Field */}
                <div className="space-y-2">
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <User className={`h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'name' ? 'text-emerald-500' : 'text-gray-400'
                      }`} />
                </div>
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={formData.name}
                  onChange={handleInputChange}
                      onFocus={() => handleInputFocus('name')}
                      onBlur={handleInputBlur}
                      onKeyDown={handleKeyDown}
                      className={`block w-full pl-12 pr-4 py-4 bg-gray-50 border rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 text-base transition-all duration-200 group-hover:bg-gray-100 ${
                        errors.name ? 'border-red-400 ring-2 ring-red-400/20' : 'border-gray-200'
                      }`}
                      placeholder="Nom complet"
                      aria-describedby={errors.name ? 'name-error' : undefined}
                      aria-invalid={errors.name ? 'true' : 'false'}
                      required
                />
              </div>
              {errors.name && (
                    <div id="name-error" className="flex items-center space-x-2 animate-slide-in-right" role="alert">
                      <AlertCircle className="h-4 w-4 text-red-400" aria-hidden="true" />
                      <p className="text-sm text-red-400">{errors.name}</p>
                    </div>
              )}
            </div>

            {/* Email Field */}
                <div className="space-y-2">
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Mail className={`h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'email' ? 'text-emerald-500' : 'text-gray-400'
                      }`} />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleInputChange}
                      onFocus={() => handleInputFocus('email')}
                      onBlur={handleInputBlur}
                      onKeyDown={handleKeyDown}
                      className={`block w-full pl-12 pr-4 py-4 bg-gray-50 border rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 text-base transition-all duration-200 group-hover:bg-gray-100 ${
                        errors.email ? 'border-red-400 ring-2 ring-red-400/20' : 'border-gray-200'
                      }`}
                      placeholder="Adresse email professionnelle"
                      aria-describedby={errors.email ? 'email-error' : undefined}
                      aria-invalid={errors.email ? 'true' : 'false'}
                      required
                />
              </div>
              {errors.email && (
                    <div id="email-error" className="flex items-center space-x-2 animate-slide-in-right" role="alert">
                      <AlertCircle className="h-4 w-4 text-red-400" aria-hidden="true" />
                      <p className="text-sm text-red-400">{errors.email}</p>
                    </div>
              )}
            </div>

            {/* Password Field */}
                <div className="space-y-2">
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Lock className={`h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'password' ? 'text-emerald-500' : 'text-gray-400'
                      }`} />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleInputChange}
                      onFocus={() => handleInputFocus('password')}
                      onBlur={handleInputBlur}
                      onKeyDown={handleKeyDown}
                      className={`block w-full pl-12 pr-12 py-4 bg-gray-50 border rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 text-base transition-all duration-200 group-hover:bg-gray-100 ${
                        errors.password ? 'border-red-400 ring-2 ring-red-400/20' : 'border-gray-200'
                      }`}
                      placeholder="Mot de passe"
                      aria-describedby={errors.password ? 'password-error' : undefined}
                      aria-invalid={errors.password ? 'true' : 'false'}
                      required
                />
                <button
                  type="button"
                      className="absolute inset-y-0 right-0 pr-4 flex items-center group/eye"
                  onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                >
                  {showPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400 hover:text-emerald-500 transition-colors duration-200 group-hover/eye:scale-110" />
                  ) : (
                        <Eye className="h-5 w-5 text-gray-400 hover:text-emerald-500 transition-colors duration-200 group-hover/eye:scale-110" />
                  )}
                </button>
              </div>
              {errors.password && (
                    <div id="password-error" className="flex items-center space-x-2 animate-slide-in-right" role="alert">
                      <AlertCircle className="h-4 w-4 text-red-400" aria-hidden="true" />
                      <p className="text-sm text-red-400">{errors.password}</p>
                    </div>
              )}
            </div>

            {/* Confirm Password Field */}
                <div className="space-y-2">
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Lock className={`h-5 w-5 transition-colors duration-200 ${
                        focusedField === 'confirmPassword' ? 'text-emerald-500' : 'text-gray-400'
                      }`} />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                      onFocus={() => handleInputFocus('confirmPassword')}
                      onBlur={handleInputBlur}
                      onKeyDown={handleKeyDown}
                      className={`block w-full pl-12 pr-12 py-4 bg-gray-50 border rounded-xl shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 text-base transition-all duration-200 group-hover:bg-gray-100 ${
                        errors.confirmPassword ? 'border-red-400 ring-2 ring-red-400/20' : 'border-gray-200'
                      }`}
                      placeholder="Confirmer le mot de passe"
                      aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
                      aria-invalid={errors.confirmPassword ? 'true' : 'false'}
                      required
                />
                <button
                  type="button"
                      className="absolute inset-y-0 right-0 pr-4 flex items-center group/eye"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label={showConfirmPassword ? 'Masquer la confirmation du mot de passe' : 'Afficher la confirmation du mot de passe'}
                >
                  {showConfirmPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400 hover:text-emerald-500 transition-colors duration-200 group-hover/eye:scale-110" />
                  ) : (
                        <Eye className="h-5 w-5 text-gray-400 hover:text-emerald-500 transition-colors duration-200 group-hover/eye:scale-110" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                    <div id="confirmPassword-error" className="flex items-center space-x-2 animate-slide-in-right" role="alert">
                      <AlertCircle className="h-4 w-4 text-red-400" aria-hidden="true" />
                      <p className="text-sm text-red-400">{errors.confirmPassword}</p>
                    </div>
              )}
            </div>

            {/* Message Display */}
            {message.text && (
                  <div 
                    className={`rounded-xl p-4 border animate-slide-in-down ${
                message.type === 'success' 
                        ? 'bg-emerald-50 border-emerald-200' 
                        : 'bg-red-50 border-red-200'
                    }`}
                    role="alert"
                    aria-live="polite"
                  >
                    <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {message.type === 'success' ? (
                          <CheckCircle className="h-5 w-5 text-emerald-500 animate-bounce" aria-hidden="true" />
                    ) : (
                          <AlertCircle className="h-5 w-5 text-red-500 animate-pulse" aria-hidden="true" />
                    )}
                  </div>
                    <p className={`text-sm font-medium ${
                        message.type === 'success' ? 'text-emerald-700' : 'text-red-700'
                    }`}>
                      {message.text}
                    </p>
                </div>
              </div>
            )}

            {/* Submit Button */}
                <div className="space-y-4">
              <button
                type="submit"
                disabled={isLoading}
                    className="group w-full px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-600 text-white font-semibold rounded-xl hover:from-emerald-700 hover:to-green-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white"></div>
                        <span>Création du compte...</span>
                  </div>
                ) : (
                      <div className="flex items-center space-x-2">
                        <Users className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        <span>Créer le compte</span>
                      </div>
                )}
              </button>

                  {/* Login Link */}
                  <div className="text-center">
                    <p className="text-sm text-gray-600">
                      Déjà un compte ?{' '}
                      <Link 
                        to="/login" 
                        className="font-medium text-emerald-600 hover:text-emerald-500 transition-colors duration-200 hover:underline"
                      >
                        Se connecter
                      </Link>
                    </p>
                  </div>
                </div>
              </form>

            
              {/* Footer */}
              <div className="mt-8 text-center">
                <p className="text-xs text-gray-400">
                  © 2025 CV Analyzer. Tous droits réservés.
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
          0%, 100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.3); }
          50% { box-shadow: 0 0 30px rgba(16, 185, 129, 0.6); }
        }
        
        @keyframes slideInLeft {
          0% { transform: translateX(-100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideInRight {
          0% { transform: translateX(100%); opacity: 0; }
          100% { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slide-in-right {
          from { opacity: 0; transform: translateX(30px); }
          to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slide-in-down {
          from { opacity: 0; transform: translateY(-30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-float { animation: float 3s ease-in-out infinite; }
        .animate-float-delayed { animation: float-delayed 4s ease-in-out infinite; }
        .animate-float-slow { animation: float-slow 5s ease-in-out infinite; }
        .animate-pulse-glow { animation: pulse-glow 2s ease-in-out infinite; }
        .animate-slide-in-left { animation: slideInLeft 0.8s ease-out; }
        .animate-slide-in-right { animation: slideInRight 0.8s ease-out; }
        .animate-slide-in-right { animation: slide-in-right 0.4s ease-out; }
        .animate-slide-in-down { animation: slide-in-down 0.4s ease-out; }
        
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

export default Register;
