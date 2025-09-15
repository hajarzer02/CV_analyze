import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Sparkles, 
  Shield, 
  Zap,
  ArrowRight,
  Eye,
  Clock
} from 'lucide-react';
import { uploadCV } from '../services/api';

const UploadCV = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);
    setUploadStatus(null);

    try {
      const response = await uploadCV(file);
      setUploadStatus('success');
      
      // Redirect to candidate profile after successful upload
      setTimeout(() => {
        navigate(`/candidate/${response.candidate_id}`);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Échec du téléchargement. Veuillez réessayer.');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 -m-4 p-4">
      <div className="max-w-3xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full mb-3">
            <Upload className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2">
            Télécharger un CV
          </h1>
          <p className="text-base text-gray-600 max-w-lg mx-auto">
            Transformez votre CV en opportunités d'emploi avec notre analyse intelligente
          </p>
        </div>

        {/* Main Upload Area */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
          {/* Upload Zone */}
          <div className="p-4 md:p-6">
        <div
          {...getRootProps()}
              className={`relative group transition-all duration-300 ease-in-out ${
            isDragActive
                  ? 'scale-105 shadow-2xl'
                  : 'hover:scale-105'
              } ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <input {...getInputProps()} />
          
              {/* Background Pattern */}
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-purple-50 opacity-50"></div>
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.1),transparent_50%)]"></div>
              
              {/* Border Animation */}
              <div className={`absolute inset-0 rounded-2xl border-2 transition-all duration-300 ${
                isDragActive 
                  ? 'border-indigo-400 shadow-lg shadow-indigo-200' 
                  : 'border-dashed border-gray-300 group-hover:border-indigo-300'
              }`}></div>
              
              {/* Content */}
              <div className="relative z-10 p-4 md:p-6 text-center">
          {uploading ? (
            <div className="space-y-4">
                    <div className="relative">
                      <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600 mx-auto"></div>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Zap className="h-5 w-5 text-indigo-600 animate-pulse" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">Analyse en cours...</h3>
                      <p className="text-sm text-gray-600">Notre IA analyse votre CV et extrait les informations clés</p>
                    </div>
                    <div className="flex items-center justify-center space-x-2 text-xs text-indigo-600">
                      <Clock className="h-3 w-3" />
                      <span>Généralement 10-30 secondes</span>
                    </div>
            </div>
          ) : uploadStatus === 'success' ? (
            <div className="space-y-4">
                    <div className="relative">
                      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto animate-bounce">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                      </div>
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                        <Sparkles className="h-2 w-2 text-white" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-green-700 mb-1">CV analysé avec succès !</h3>
                      <p className="text-sm text-gray-600 mb-3">Votre profil a été créé et les recommandations sont prêtes</p>
                      <div className="inline-flex items-center space-x-2 text-indigo-600 font-medium text-sm">
                        <span>Redirection en cours...</span>
                        <ArrowRight className="h-3 w-3 animate-pulse" />
                      </div>
                    </div>
            </div>
          ) : uploadStatus === 'error' ? (
            <div className="space-y-4">
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                      <AlertCircle className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-red-700 mb-1">Échec du téléchargement</h3>
                      <p className="text-sm text-gray-600">Une erreur s'est produite lors du traitement de votre fichier</p>
                    </div>
                    <button 
                      onClick={() => {
                        setUploadStatus(null);
                        setError(null);
                      }}
                      className="inline-flex items-center px-3 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Réessayer
                    </button>
            </div>
                ) : (
                  <div className="space-y-4">
                    {/* Main Upload Icon */}
                    <div className="relative">
                      <div className={`w-14 h-14 mx-auto rounded-xl flex items-center justify-center transition-all duration-300 ${
                        isDragActive 
                          ? 'bg-indigo-100 scale-105' 
                          : 'bg-gray-100 group-hover:bg-indigo-50'
                      }`}>
                        <Upload className={`h-7 w-7 transition-colors duration-300 ${
                          isDragActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-indigo-500'
                        }`} />
                      </div>
                      {isDragActive && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-10 h-10 border-2 border-indigo-400 border-dashed rounded-lg animate-pulse"></div>
                        </div>
                      )}
                    </div>

                    {/* Upload Text */}
                    <div className="space-y-2">
                      <h3 className="text-lg font-bold text-gray-900">
                        {isDragActive ? 'Déposez votre CV ici' : 'Glissez-déposez votre CV'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {isDragActive ? 'Relâchez pour commencer l\'analyse' : 'ou cliquez pour sélectionner un fichier'}
                      </p>
                    </div>

                    {/* File Type Info */}
                    <div className="flex items-center justify-center space-x-2 text-xs text-gray-500 bg-gray-50 rounded-full px-3 py-1">
                      <Shield className="h-3 w-3" />
                      <span>Fichiers sécurisés : PDF, DOCX, DOC, TXT</span>
                    </div>

                    {/* Upload Button */}
                    <div className="pt-1">
                      <button className="inline-flex items-center px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl">
                        <Upload className="h-4 w-4 mr-2" />
                        Choisir un fichier
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="px-4 pb-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-700">{error}</div>
              </div>
            </div>
          )}
        </div>

        {/* Features Section */}
        {/* <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center group">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center mx-auto mb-4 hover:scale-105 transition-transform duration-200">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analyse Rapide</h3>
            <p className="text-gray-600">Traitement intelligent en quelques secondes avec notre IA avancée</p>
      </div>

          <div className="text-center group">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-4 hover:scale-105 transition-transform duration-200">
              <Eye className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Extraction Précise</h3>
            <p className="text-gray-600">Identification automatique des compétences, expériences et formations</p>
          </div>
          
          <div className="text-center group">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-4 hover:scale-105 transition-transform duration-200">
              <Sparkles className="h-6 w-6 text-white" />
        </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommandations</h3>
            <p className="text-gray-600">Suggestions d'emplois personnalisées basées sur votre profil</p>
          </div>
        </div> */}

        {/* Supported File Types */}
        <div className="mt-6">
          <div className="text-center mb-3">
            <h3 className="text-base font-bold text-gray-900 mb-1">Types de Fichiers Supportés</h3>
            <p className="text-xs text-gray-600">Choisissez le format qui vous convient le mieux</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { type: 'PDF', icon: FileText, color: 'from-red-500 to-red-600', desc: 'Format standard' },
              { type: 'DOCX', icon: FileText, color: 'from-blue-500 to-blue-600', desc: 'Word moderne' },
              { type: 'DOC', icon: FileText, color: 'from-blue-600 to-blue-700', desc: 'Word classique' },
              { type: 'TXT', icon: FileText, color: 'from-gray-500 to-gray-600', desc: 'Texte simple' }
            ].map((file, index) => (
              <div key={index} className="group">
                <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 text-center border border-white/20 shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105">
                  <div className={`w-8 h-8 bg-gradient-to-r ${file.color} rounded-lg flex items-center justify-center mx-auto mb-2 hover:scale-105 transition-transform duration-200`}>
                    <file.icon className="h-4 w-4 text-white" />
                  </div>
                  <h4 className="font-semibold text-gray-900 text-sm mb-1">{file.type}</h4>
                  <p className="text-xs text-gray-600">{file.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-4 text-center">
          <div className="inline-flex items-center space-x-2 text-xs text-gray-500 bg-white/60 backdrop-blur-sm rounded-full px-3 py-1.5 border border-white/20">
            <Shield className="h-3 w-3" />
            <span>Vos fichiers sont traités de manière sécurisée et ne sont pas stockés</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadCV;
