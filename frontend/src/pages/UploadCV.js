import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
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
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Télécharger un CV</h1>
        <p className="text-gray-600">
          Téléchargez un fichier CV pour extraire les informations et générer des recommandations d'emploi
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-8">
        <div
          {...getRootProps()}
          className={`text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'hover:border-gray-400'
          } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          
          {uploading ? (
            <div className="space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="text-gray-600">Traitement de votre CV...</p>
            </div>
          ) : uploadStatus === 'success' ? (
            <div className="space-y-4">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
              <p className="text-green-600 font-medium">CV téléchargé avec succès !</p>
              <p className="text-gray-600">Redirection vers le profil...</p>
            </div>
          ) : uploadStatus === 'error' ? (
            <div className="space-y-4">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
              <p className="text-red-600 font-medium">Échec du téléchargement</p>
              <p className="text-gray-600">Veuillez réessayer</p>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-12 w-12 text-gray-400 mx-auto" />
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {isDragActive ? 'Déposez le fichier ici' : 'Glissez-déposez un fichier CV ici'}
                </p>
                <p className="text-gray-600">ou cliquez pour sélectionner un fichier</p>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <FileText className="h-4 w-4" />
                <span>Fichiers PDF, DOCX, DOC ou TXT uniquement</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <div className="text-sm text-red-700">{error}</div>
          </div>
        </div>
      )}

      <div className="mt-8 text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Types de Fichiers Supportés</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <FileText className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">PDF</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <FileText className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">DOCX</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">DOC</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <FileText className="h-8 w-8 text-gray-500 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-900">TXT</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadCV;
