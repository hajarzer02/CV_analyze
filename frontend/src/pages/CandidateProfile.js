import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Linkedin, 
  GraduationCap, 
  Briefcase, 
  Code, 
  Globe, 
  Lightbulb,
  ArrowLeft,
  RefreshCw,
  Calendar,
  Award,
  Star,
  TrendingUp,
  Target,
  CheckCircle,
  ExternalLink,
  Sparkles,
  ChevronDown
} from 'lucide-react';
import { getCandidate, generateRecommendations, updateCandidateStatus } from '../services/api';

const CandidateProfile = () => {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingRecs, setGeneratingRecs] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCandidate();
  }, [id]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showStatusDropdown && !event.target.closest('.status-dropdown')) {
        setShowStatusDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showStatusDropdown]);

  const fetchCandidate = async () => {
    try {
      setLoading(true);
      const data = await getCandidate(id);
      setCandidate(data);
    } catch (err) {
      setError('Échec du chargement du profil du candidat');
      console.error('Error fetching candidate:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    try {
      setGeneratingRecs(true);
      const response = await generateRecommendations(id);
      
      // Replace old recommendations with new ones
      setCandidate(prev => ({
        ...prev,
        recommendations: [response.recommendations]
      }));
    } catch (err) {
      setError('Échec de la génération des recommandations');
      console.error('Error generating recommendations:', err);
    } finally {
      setGeneratingRecs(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      setUpdatingStatus(true);
      await updateCandidateStatus(id, newStatus);
      
      // Update local state
      setCandidate(prev => ({
        ...prev,
        status: newStatus
      }));
    } catch (err) {
      setError('Échec de la mise à jour du statut');
      console.error('Error updating status:', err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  // Status translations
  const getStatusTranslation = (status) => {
    const translations = {
      'New': 'Nouveau',
      'Interview Scheduled': 'Entretien Programmé',
      'Offer': 'Offre',
      'Hired': 'Embauché',
      'Rejected': 'Rejeté'
    };
    return translations[status] || status;
  };

  // Status color mapping (same as Dashboard)
  const getStatusColors = (status) => {
    const statusColors = {
      'New': 'bg-gray-100 text-gray-800',
      'Interview Scheduled': 'bg-blue-100 text-blue-800',
      'Offer': 'bg-yellow-100 text-yellow-800',
      'Hired': 'bg-green-100 text-green-800',
      'Rejected': 'bg-red-100 text-red-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  // Get just the background color for indicators
  const getStatusBgColor = (status) => {
    const statusColors = {
      'New': 'bg-gray-500',
      'Interview Scheduled': 'bg-blue-500',
      'Offer': 'bg-yellow-500',
      'Hired': 'bg-green-500',
      'Rejected': 'bg-red-500'
    };
    return statusColors[status] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-indigo-600 mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <User className="h-5 w-5 text-indigo-600 animate-pulse" />
            </div>
          </div>
          <p className="mt-3 text-gray-600 font-medium">Chargement du profil...</p>
        </div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="h-8 w-8 text-gray-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Profil non trouvé</h2>
          <p className="text-gray-600 mb-6">{error || 'Le candidat demandé n\'existe pas ou a été supprimé.'}</p>
        <Link
            to="/dashboard"
            className="inline-flex items-center px-5 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
            <ArrowLeft className="h-4 w-4 mr-2" />
          Retour au Tableau de Bord
        </Link>
        </div>
      </div>
    );
  }

  const { extracted_data, recommendations } = candidate;
  const contactInfo = extracted_data?.contact_info || {};
  const skills = extracted_data?.skills || [];
  const languages = extracted_data?.languages || [];
  const education = extracted_data?.education || [];
  const experience = extracted_data?.experience || [];
  const projects = extracted_data?.projects || [];
  const summary = extracted_data?.professional_summary || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
      <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
          <Link
                to="/dashboard"
                className="group p-2 text-gray-600 hover:text-indigo-600 hover:bg-gray-100 rounded-lg transition-all duration-200"
          >
                <ArrowLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
          </Link>
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                  <User className="h-6 w-6 text-white" />
                </div>
          <div>
                  <h1 className="text-2xl font-bold text-gray-900">
              {candidate.name || 'Candidat Inconnu'}
            </h1>
                  <div className="flex items-center space-x-2 mt-0.5">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                    <p className="text-sm text-gray-600">Profil du Candidat</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <p className="text-xs text-gray-500 mb-1">Statut</p>
                <div className="relative status-dropdown">
                  <button
                    onClick={() => setShowStatusDropdown(!showStatusDropdown)}
                    disabled={updatingStatus}
                    className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium ${getStatusColors(candidate?.status || 'New')} hover:opacity-80 disabled:opacity-50 transition-colors`}
                  >
                    {getStatusTranslation(candidate?.status || 'New')}
                    <ChevronDown className="h-3 w-3 ml-1" />
                  </button>
                  
                  {showStatusDropdown && (
                    <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                      {['New', 'Interview Scheduled', 'Offer', 'Hired', 'Rejected'].map((status) => (
                        <button
                          key={status}
                          onClick={() => {
                            handleStatusUpdate(status);
                            setShowStatusDropdown(false);
                          }}
                          className="w-full text-left px-3 py-1.5 text-xs text-gray-700 hover:bg-gray-100 transition-colors flex items-center space-x-2"
                        >
                          <div className={`w-2 h-2 rounded-full ${getStatusColors(status).split(' ')[0].replace('bg-', 'bg-')}`}></div>
                          <span>{getStatusTranslation(status)}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column - CV Information */}
          <div className="xl:col-span-2 space-y-4">
          {/* Contact Information */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-indigo-600 p-4">
                <h2 className="text-lg font-semibold text-white flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations de Contact
            </h2>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {contactInfo.emails?.map((email, index) => (
                    <div key={index} className="group flex items-center p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 transition-colors">
                      <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-indigo-200 transition-colors">
                        <Mail className="h-4 w-4 text-indigo-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Email</p>
                        <a href={`mailto:${email}`} className="text-sm text-gray-900 hover:text-indigo-600 font-medium transition-colors">
                    {email}
                  </a>
                      </div>
                </div>
              ))}
              {contactInfo.phones?.map((phone, index) => (
                    <div key={index} className="group flex items-center p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 transition-colors">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-gray-200 transition-colors">
                        <Phone className="h-4 w-4 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Téléphone</p>
                        <a href={`tel:${phone}`} className="text-sm text-gray-900 hover:text-indigo-600 font-medium transition-colors">
                    {phone}
                  </a>
                      </div>
                </div>
              ))}
              {contactInfo.address && (
                    <div className="group flex items-center p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 transition-colors md:col-span-2">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-gray-200 transition-colors">
                        <MapPin className="h-4 w-4 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">Adresse</p>
                        <span className="text-sm text-gray-900 font-medium">{contactInfo.address}</span>
                      </div>
                </div>
              )}
              {contactInfo.linkedin && (
                    <div className="group flex items-center p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 transition-colors md:col-span-2">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-gray-200 transition-colors">
                        <Linkedin className="h-4 w-4 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-500 font-medium">LinkedIn</p>
                  <a 
                    href={`https://${contactInfo.linkedin}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                          className="text-sm text-gray-900 hover:text-indigo-600 font-medium transition-colors flex items-center"
                  >
                    {contactInfo.linkedin}
                          <ExternalLink className="h-3 w-3 ml-2" />
                  </a>
                      </div>
                    </div>
                  )}
                </div>
              </div>
          </div>

          {/* Professional Summary */}
          {summary.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-indigo-600 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                    <Award className="h-5 w-5 mr-2" />
                    Résumé Professionnel
                  </h2>
                </div>
                <div className="p-4">
                  <div className="space-y-3">
                {summary.map((line, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700 leading-relaxed">{line}</p>
                      </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Skills */}
          {skills.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-gray-700 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                <Code className="h-5 w-5 mr-2" />
                    Compétences Techniques
              </h2>
                </div>
                <div className="p-4">
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                        className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
                  >
                        <Star className="h-3 w-3 mr-1.5" />
                    {skill}
                  </span>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Languages */}
          {languages.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-indigo-600 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                <Globe className="h-5 w-5 mr-2" />
                Langues
              </h2>
                </div>
                <div className="p-4">
                  <div className="space-y-3">
                {languages.map((lang, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-indigo-50 transition-colors">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <Globe className="h-4 w-4 text-indigo-600" />
                          </div>
                    <span className="font-medium text-gray-900">{lang.language}</span>
                        </div>
                        <span className="px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-medium">
                          {lang.level}
                        </span>
                  </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Education */}
          {education.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-gray-700 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                <GraduationCap className="h-5 w-5 mr-2" />
                Formation
              </h2>
                </div>
                <div className="p-4">
              <div className="space-y-4">
                {education.map((edu, index) => (
                      <div key={index} className="relative">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                              <GraduationCap className="h-4 w-4 text-gray-600" />
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                                <h3 className="text-sm font-semibold text-gray-900">{edu.degree}</h3>
                        {edu.institution && (
                                  <p className="text-xs text-gray-600 font-medium">{edu.institution}</p>
                        )}
                      </div>
                      {edu.date_range && (
                                <div className="flex items-center mt-1 sm:mt-0">
                                  <Calendar className="h-3 w-3 text-gray-400 mr-1" />
                                  <span className="text-xs text-gray-500 font-medium">{edu.date_range}</span>
                                </div>
                      )}
                    </div>
                    {edu.details.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {edu.details.map((detail, detailIndex) => (
                                  <li key={detailIndex} className="flex items-start space-x-2 text-xs text-gray-600">
                                    <div className="w-1 h-1 bg-gray-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                    <span>{detail}</span>
                          </li>
                        ))}
                      </ul>
                            )}
                          </div>
                        </div>
                        {index < education.length - 1 && (
                          <div className="absolute left-4 top-8 w-0.5 h-4 bg-gray-200"></div>
                    )}
                  </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Experience */}
          {experience.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-indigo-600 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                    Expérience Professionnelle
              </h2>
                </div>
                <div className="p-4">
              <div className="space-y-4">
                {experience.map((exp, index) => (
                      <div key={index} className="relative">
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                              <Briefcase className="h-4 w-4 text-indigo-600" />
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                                <h3 className="text-sm font-semibold text-gray-900">{exp.role}</h3>
                                <p className="text-xs text-gray-600 font-medium">{exp.company}</p>
                      </div>
                      {exp.date_range && (
                                <div className="flex items-center mt-1 sm:mt-0">
                                  <Calendar className="h-3 w-3 text-gray-400 mr-1" />
                                  <span className="text-xs text-gray-500 font-medium">{exp.date_range}</span>
                                </div>
                      )}
                    </div>
                    {exp.details.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {exp.details.map((detail, detailIndex) => (
                                  <li key={detailIndex} className="flex items-start space-x-2 text-xs text-gray-600">
                                    <div className="w-1 h-1 bg-indigo-500 rounded-full mt-1.5 flex-shrink-0"></div>
                                    <span>{detail}</span>
                          </li>
                        ))}
                      </ul>
                            )}
                          </div>
                        </div>
                        {index < experience.length - 1 && (
                          <div className="absolute left-4 top-8 w-0.5 h-4 bg-gray-200"></div>
                    )}
                  </div>
                ))}
                  </div>
              </div>
            </div>
          )}

            {/* Projects */}
            {projects.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="bg-indigo-600 p-4">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                    <Target className="h-5 w-5 mr-2" />
                    Projets
                  </h2>
                </div>
                <div className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {projects.map((project, index) => (
                      <div key={index} className="group bg-gray-50 rounded-lg p-3 hover:bg-indigo-50 transition-colors border border-gray-100">
                        <div className="flex items-start space-x-2">
                          <div className="w-6 h-6 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
                            <Target className="h-3 w-3 text-indigo-600" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900 mb-1 text-sm">{project.title}</h3>
                            {project.description && (
                              <p className="text-gray-600 text-xs leading-relaxed">{project.description}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
        </div>

          {/* Right Column - Job Recommendations */}
          <div className="xl:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden sticky top-4">
              <div className="bg-indigo-600 p-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-white flex items-center">
                    <Lightbulb className="h-5 w-5 mr-2" />
                    Recommandations IA
                  </h2>
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
              </div>
              <div className="p-4">
                <button
                  onClick={handleGenerateRecommendations}
                  disabled={generatingRecs}
                  className="w-full mb-4 px-4 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors"
                >
                  {generatingRecs ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Génération...</span>
                    </>
                  ) : (
                    <>
                      <Lightbulb className="h-4 w-4" />
                      <span className="text-sm">Générer des Recommandations</span>
                    </>
                  )}
                </button>

                {recommendations && recommendations.length > 0 ? (
                  <div className="space-y-3">
                    {recommendations.map((recGroup, groupIndex) => (
                      <div key={groupIndex} className="space-y-2">
                        {recGroup.map((rec, index) => (
                          <div key={index} className="group bg-gray-50 rounded-lg p-3 hover:bg-indigo-50 transition-colors border border-gray-100">
                            <div className="flex items-start space-x-2">
                              <div className="w-6 h-6 bg-indigo-100 rounded-lg flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
                                <TrendingUp className="h-3 w-3 text-indigo-600" />
                              </div>
                              <div className="flex-1">
                                <h3 className="font-medium text-gray-900 mb-1 text-sm">{rec.title}</h3>
                                <p className="text-gray-600 text-xs leading-relaxed">{rec.reason}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                      <Lightbulb className="h-6 w-6 text-indigo-600" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">Aucune recommandation</h3>
                    <p className="text-gray-600 mb-3 text-xs">Générez des suggestions d'emploi personnalisées</p>
                    <p className="text-xs text-gray-500">
                      Notre IA analysera le profil et proposera des opportunités adaptées
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;
