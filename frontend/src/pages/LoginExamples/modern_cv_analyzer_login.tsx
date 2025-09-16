import React, { useState, useEffect } from 'react';
import { Eye, EyeOff, Mail, Lock, AlertCircle, CheckCircle, FileSearch, Users, TrendingUp, Shield, Zap, Star } from 'lucide-react';

const ModernCVAnalyzerLogin = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [focusedField, setFocusedField] = useState(null);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
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
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    
    // Simulate API call
    setTimeout(() => {
      setMessage({ 
        type: 'success', 
        text: 'Welcome to your CV Analytics Dashboard!' 
      });
      setIsLoading(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 relative overflow-hidden">
      {/* Modern Background Effects */}
      <div className="absolute inset-0">
        {/* Animated gradient orbs */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px]"></div>
        
        {/* Floating CV elements - simplified */}
        <div className="absolute top-20 left-10 w-12 h-16 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-lg backdrop-blur-sm border border-white/5 animate-float-slow">
          <FileSearch className="w-6 h-6 text-purple-400/60 m-auto mt-3" />
        </div>
        <div className="absolute top-32 right-16 w-10 h-10 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full backdrop-blur-sm border border-white/5 animate-float-delayed">
          <Users className="w-5 h-5 text-blue-400/60 m-auto mt-1.5" />
        </div>
        <div className="absolute bottom-32 left-20 w-14 h-14 bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-xl backdrop-blur-sm border border-white/5 animate-float-slow">
          <TrendingUp className="w-7 h-7 text-purple-400/60 m-auto mt-2" />
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Header Section */}
          <div className="text-center mb-8 animate-fade-in">
            {/* Enhanced Logo */}
            <div className="mx-auto mb-6 relative">
              <div className="w-32 h-32 mx-auto bg-gradient-to-tr from-purple-500 via-pink-500 to-blue-500 rounded-3xl shadow-2xl shadow-purple-500/25 flex items-center justify-center relative overflow-hidden group">
                {/* Animated background */}
                <div className="absolute inset-0 bg-gradient-to-tr from-purple-600 via-pink-600 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                
                {/* Logo content */}
                <div className="relative z-10">
                  <img 
                    src="/LOGapp.svg" 
                    alt="CVAnalyzer Logo" 
                    className="h-16 w-16 object-contain filter drop-shadow-lg"
                  />
                </div>
                
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-tr from-purple-500/20 via-pink-500/20 to-blue-500/20 blur-xl scale-110"></div>
              </div>
              
              {/* Floating particles around logo */}
              <div className="absolute -top-2 -left-2 w-3 h-3 bg-purple-400 rounded-full animate-ping"></div>
              <div className="absolute -top-1 -right-3 w-2 h-2 bg-pink-400 rounded-full animate-ping delay-500"></div>
              <div className="absolute -bottom-2 -right-1 w-2.5 h-2.5 bg-blue-400 rounded-full animate-ping delay-1000"></div>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent mb-3">
              CV Analyzer Pro
            </h1>
            <p className="text-lg text-slate-300 mb-2">
              AI-Powered Talent Intelligence
            </p>
            <p className="text-sm text-slate-400 mb-6">
              Transform recruiting with smart CV analysis
            </p>
            
            {/* Stats */}
            <div className="flex justify-center space-x-6 text-sm text-slate-400 mb-6">
              <div className="flex items-center space-x-1">
                <Star className="w-4 h-4 text-yellow-400" />
                <span>99.2% Accuracy</span>
              </div>
              <div className="flex items-center space-x-1">
                <Zap className="w-4 h-4 text-blue-400" />
                <span>3sec Analysis</span>
              </div>
            </div>
          </div>

          {/* Login Form */}
          <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 shadow-2xl">
            {/* Security indicator */}
            <div className="flex items-center justify-center space-x-2 mb-6 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span className="text-sm text-emerald-300 font-medium">Enterprise Security</span>
            </div>

            <div className="space-y-6">
              {/* Email Field */}
              <div className="space-y-2">
                <div className="relative">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    className={`w-full px-4 py-4 pl-12 bg-white/5 border rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-200 ${
                      errors.email ? 'border-red-400/50' : 'border-white/10'
                    } ${focusedField === 'email' ? 'bg-white/10' : ''}`}
                    placeholder="Enter your email"
                  />
                  <Mail className={`absolute left-4 top-4 w-5 h-5 transition-colors duration-200 ${
                    focusedField === 'email' ? 'text-purple-400' : 'text-slate-500'
                  }`} />
                  
                  {/* Floating label */}
                  <label className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                    focusedField === 'email' || formData.email 
                      ? '-top-2 left-4 text-xs text-purple-400 bg-slate-950 px-2 rounded' 
                      : 'top-4 text-slate-400'
                  }`}>
                    {focusedField === 'email' || formData.email ? 'Email Address' : ''}
                  </label>
                </div>
                {errors.email && (
                  <div className="flex items-center space-x-2 text-red-400 text-sm animate-slide-in">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.email}</span>
                  </div>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    className={`w-full px-4 py-4 pl-12 pr-12 bg-white/5 border rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all duration-200 ${
                      errors.password ? 'border-red-400/50' : 'border-white/10'
                    } ${focusedField === 'password' ? 'bg-white/10' : ''}`}
                    placeholder="Enter your password"
                  />
                  <Lock className={`absolute left-4 top-4 w-5 h-5 transition-colors duration-200 ${
                    focusedField === 'password' ? 'text-purple-400' : 'text-slate-500'
                  }`} />
                  
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-4 text-slate-400 hover:text-purple-400 transition-colors duration-200"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                  
                  {/* Floating label */}
                  <label className={`absolute left-12 transition-all duration-200 pointer-events-none ${
                    focusedField === 'password' || formData.password 
                      ? '-top-2 left-4 text-xs text-purple-400 bg-slate-950 px-2 rounded' 
                      : 'top-4 text-slate-400'
                  }`}>
                    {focusedField === 'password' || formData.password ? 'Password' : ''}
                  </label>
                </div>
                {errors.password && (
                  <div className="flex items-center space-x-2 text-red-400 text-sm animate-slide-in">
                    <AlertCircle className="w-4 h-4" />
                    <span>{errors.password}</span>
                  </div>
                )}
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 text-purple-500 bg-white/5 border-white/20 rounded focus:ring-purple-500/50"
                  />
                  <span className="text-sm text-slate-300">Remember me</span>
                </label>
                <button
                  type="button"
                  className="text-sm text-purple-400 hover:text-purple-300 transition-colors duration-200"
                >
                  Forgot password?
                </button>
              </div>

              {/* Message */}
              {message.text && (
                <div className={`p-4 rounded-xl border backdrop-blur-sm animate-fade-in ${
                  message.type === 'success' 
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' 
                    : 'bg-red-500/10 border-red-500/20 text-red-300'
                }`}>
                  <div className="flex items-center space-x-2">
                    {message.type === 'success' ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <AlertCircle className="w-5 h-5" />
                    )}
                    <span className="text-sm font-medium">{message.text}</span>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                onClick={handleSubmit}
                className="w-full py-4 px-6 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold rounded-xl shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-purple-500/50 active:scale-[0.98]"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Analyzing...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <FileSearch className="w-5 h-5" />
                    <span>Access Dashboard</span>
                  </div>
                )}
              </button>
            </div>

            {/* Footer */}
            <div className="mt-6 text-center">
              <p className="text-sm text-slate-400">
                Don't have an account?{' '}
                <button className="text-purple-400 hover:text-purple-300 transition-colors duration-200 font-medium">
                  Sign up here
                </button>
              </p>
              
              {/* Trust indicators */}
              <div className="flex justify-center items-center space-x-4 mt-4 text-xs text-slate-500">
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3" />
                  <span>SOC 2</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3" />
                  <span>GDPR</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3" />
                  <span>ISO 27001</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Styles */}
      <style jsx>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes float-delayed {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          33% { transform: translateY(-8px) translateX(4px); }
          66% { transform: translateY(-4px) translateX(-4px); }
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slide-in {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-float-slow { animation: float-slow 6s ease-in-out infinite; }
        .animate-float-delayed { animation: float-delayed 8s ease-in-out infinite; }
        .animate-fade-in { animation: fade-in 0.6s ease-out; }
        .animate-slide-in { animation: slide-in 0.3s ease-out; }
        
        @media (prefers-reduced-motion: reduce) {
          .animate-float-slow, .animate-float-delayed, .animate-pulse {
            animation: none;
          }
        }
      `}</style>
    </div>
  );
};

export default ModernCVAnalyzerLogin;