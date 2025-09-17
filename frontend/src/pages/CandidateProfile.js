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
  const skills = Array.isArray(extracted_data?.skills) ? extracted_data.skills : [];
  const languages = Array.isArray(extracted_data?.languages) ? extracted_data.languages : [];
  const education = Array.isArray(extracted_data?.education) ? extracted_data.education : [];
  const experience = Array.isArray(extracted_data?.experience) ? extracted_data.experience : [];
  const projects = Array.isArray(extracted_data?.projects) ? extracted_data.projects : [];
  const summary = Array.isArray(extracted_data?.professional_summary) ? extracted_data.professional_summary : [];
  const additionalInfo = Array.isArray(extracted_data?.additional_info) ? extracted_data.additional_info : [];

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
              {candidate.name || contactInfo.name || 'Candidat'}
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
                    className={`group inline-flex items-center px-4 py-2 rounded-xl text-sm font-semibold ${getStatusColors(candidate?.status || 'New')} hover:opacity-90 disabled:opacity-50 transition-all duration-200 shadow-sm hover:shadow-md`}
                    title="Cliquer pour changer le statut"
                  >
                    {updatingStatus ? (
                      <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <div className={`w-2 h-2 rounded-full mr-2 ${getStatusColors(candidate?.status || 'New').split(' ')[0].replace('bg-', 'bg-')}`}></div>
                    )}
                    {getStatusTranslation(candidate?.status || 'New')}
                    <ChevronDown className={`h-4 w-4 ml-2 transition-transform duration-200 ${showStatusDropdown ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {showStatusDropdown && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50 animate-in slide-in-from-top-2 duration-200">
                      {['New', 'Interview Scheduled', 'Offer', 'Hired', 'Rejected'].map((status) => (
                        <button
                          key={status}
                          onClick={() => {
                            handleStatusUpdate(status);
                            setShowStatusDropdown(false);
                          }}
                          className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-3 group"
                        >
                          <div className={`w-3 h-3 rounded-full ${getStatusColors(status).split(' ')[0].replace('bg-', 'bg-')}`}></div>
                          <span className="font-medium">{getStatusTranslation(status)}</span>
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

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column - CV Information */}
          <div className="xl:col-span-2 space-y-6">
          {/* Contact Information */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
              <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-5">
                <h2 className="text-lg font-bold text-white flex items-center">
                  <User className="h-5 w-5 mr-3" />
              Informations de Contact
            </h2>
              </div>
              <div className="p-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contactInfo.emails?.map((email, index) => (
                    <div key={index} className="group flex items-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-gray-100 hover:border-blue-200">
                      <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center mr-4 group-hover:bg-blue-200 transition-colors">
                        <Mail className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">Email</p>
                        <a href={`mailto:${email}`} className="text-sm text-gray-900 hover:text-blue-600 font-medium transition-colors">
                    {email}
                  </a>
                      </div>
                </div>
              ))}
              {contactInfo.phones?.map((phone, index) => (
                    <div key={index} className="group flex items-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-gray-100 hover:border-blue-200">
                      <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mr-4 group-hover:bg-gray-200 transition-colors">
                        <Phone className="h-5 w-5 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">Téléphone</p>
                        <a href={`tel:${phone}`} className="text-sm text-gray-900 hover:text-blue-600 font-medium transition-colors">
                    {phone}
                  </a>
                      </div>
                </div>
              ))}
              {contactInfo.address && (
                    <div className="group flex items-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-gray-100 hover:border-blue-200 md:col-span-2">
                      <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mr-4 group-hover:bg-gray-200 transition-colors">
                        <MapPin className="h-5 w-5 text-gray-600" />
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">Adresse</p>
                        <span className="text-sm text-gray-900 font-medium">{contactInfo.address}</span>
                      </div>
                </div>
              )}
              {contactInfo.linkedin && (
                    <div className="group flex items-center p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-gray-100 hover:border-blue-200 md:col-span-2">
                      <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mr-4 group-hover:bg-gray-200 transition-colors">
                        <Linkedin className="h-5 w-5 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-500 font-semibold uppercase tracking-wide">LinkedIn</p>
                  <a 
                    href={`https://${contactInfo.linkedin}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                          className="text-sm text-gray-900 hover:text-blue-600 font-medium transition-colors flex items-center"
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
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Award className="h-5 w-5 mr-3" />
                    Résumé Professionnel
                  </h2>
                </div>
                <div className="p-5">
                  <div className="space-y-4">
                {summary.map((line, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700 leading-relaxed font-medium">{typeof line === 'string' ? line : (line.title || line.description || JSON.stringify(line))}</p>
                      </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Skills */}
          {skills.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-slate-700 to-slate-800 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Code className="h-5 w-5 mr-3" />
                    Compétences Techniques
              </h2>
                </div>
                <div className="p-5">
                  <div className="flex flex-wrap gap-3">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                        className="group inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium bg-slate-100 text-slate-800 hover:bg-slate-200 hover:scale-105 transition-all duration-200 border border-slate-200 hover:border-slate-300"
                  >
                        <Star className="h-4 w-4 mr-2 group-hover:animate-pulse" />
                    {typeof skill === 'string' ? skill : (skill.title || skill.description || JSON.stringify(skill))}
                  </span>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Languages */}
          {languages.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-violet-600 to-violet-700 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Globe className="h-5 w-5 mr-3" />
                Langues
              </h2>
                </div>
                <div className="p-5">
                  <div className="space-y-4">
                {languages.map((lang, index) => (
                      <div key={index} className="group flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-violet-50 transition-all duration-200 border border-gray-100 hover:border-violet-200">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-violet-100 rounded-xl flex items-center justify-center group-hover:bg-violet-200 transition-colors">
                            <Globe className="h-5 w-5 text-violet-600" />
                          </div>
                          <span className="font-semibold text-gray-900">{lang.language}</span>
                        </div>
                        <span className="px-3 py-1.5 bg-violet-100 text-violet-800 rounded-full text-xs font-semibold">
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
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-slate-700 to-slate-800 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <GraduationCap className="h-5 w-5 mr-3" />
                Formation
              </h2>
                </div>
                <div className="p-5">
                  <div className="space-y-6">
                {education.map((edu, index) => (
                      <div key={index} className="relative">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center">
                              <GraduationCap className="h-6 w-6 text-slate-600" />
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                                <h3 className="text-base font-bold text-gray-900">{edu.degree}</h3>
                        {edu.institution && (
                                  <p className="text-sm text-gray-600 font-semibold">{edu.institution}</p>
                        )}
                      </div>
                      {edu.date_range && (
                                <div className="flex items-center mt-2 sm:mt-0">
                                  <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                                  <span className="text-sm text-gray-500 font-medium">{edu.date_range}</span>
                                </div>
                      )}
                    </div>
                    {edu.details && Array.isArray(edu.details) && edu.details.length > 0 && (
                              <ul className="mt-3 space-y-2">
                        {edu.details.map((detail, detailIndex) => (
                                  <li key={detailIndex} className="flex items-start space-x-3 text-sm text-gray-600">
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full mt-2 flex-shrink-0"></div>
                                    <span>{typeof detail === 'string' ? detail : (detail.title || detail.description || JSON.stringify(detail))}</span>
                          </li>
                        ))}
                      </ul>
                            )}
                          </div>
                        </div>
                        {index < education.length - 1 && (
                          <div className="absolute left-6 top-12 w-0.5 h-6 bg-gray-200"></div>
                    )}
                  </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Experience */}
          {experience.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Briefcase className="h-5 w-5 mr-3" />
                    Expérience Professionnelle
              </h2>
                </div>
                <div className="p-5">
                  <div className="space-y-6">
                {experience.map((exp, index) => (
                      <div key={index} className="relative">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0">
                            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                              <Briefcase className="h-6 w-6 text-emerald-600" />
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                                <h3 className="text-base font-bold text-gray-900">{exp.role}</h3>
                                <p className="text-sm text-gray-600 font-semibold">{exp.company}</p>
                      </div>
                      {exp.date_range && (
                                <div className="flex items-center mt-2 sm:mt-0">
                                  <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                                  <span className="text-sm text-gray-500 font-medium">{exp.date_range}</span>
                                </div>
                      )}
                    </div>
                    {exp.details && Array.isArray(exp.details) && exp.details.length > 0 && (
                              <ul className="mt-3 space-y-2">
                        {exp.details.map((detail, detailIndex) => (
                                  <li key={detailIndex} className="flex items-start space-x-3 text-sm text-gray-600">
                                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                                    <span>{typeof detail === 'string' ? detail : (detail.title || detail.description || JSON.stringify(detail))}</span>
                          </li>
                        ))}
                      </ul>
                            )}
                          </div>
                        </div>
                        {index < experience.length - 1 && (
                          <div className="absolute left-6 top-12 w-0.5 h-6 bg-gray-200"></div>
                    )}
                  </div>
                ))}
                  </div>
              </div>
            </div>
          )}

          {/* Projects */}
          {projects.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Target className="h-5 w-5 mr-3" />
                    Projets
                  </h2>
                </div>
                <div className="p-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((project, index) => (
                      <div key={index} className="group bg-gray-50 rounded-xl p-4 hover:bg-blue-50 transition-all duration-200 border border-gray-100 hover:border-blue-200 hover:shadow-md">
                        <div className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-xl flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                            <Target className="h-4 w-4 text-blue-600" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-bold text-gray-900 mb-2 text-sm">{project.title}</h3>
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

          {/* Additional Information */}
          {additionalInfo.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
                <div className="bg-gradient-to-r from-amber-600 to-amber-700 p-5">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Lightbulb className="h-5 w-5 mr-3" />
                    Informations Supplémentaires
                  </h2>
                </div>
                <div className="p-5">
                  <div className="space-y-4">
                {additionalInfo.map((info, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-sm text-gray-700 leading-relaxed font-medium">{typeof info === 'string' ? info : (info.title || info.description || JSON.stringify(info))}</p>
                      </div>
                ))}
                  </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Job Recommendations */}
          <div className="xl:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden sticky top-6 hover:shadow-xl transition-all duration-300">
              <div className="bg-gradient-to-r from-violet-600 to-violet-700 p-5">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white flex items-center">
                    <Lightbulb className="h-5 w-5 mr-3" />
                    Recommandations IA
              </h2>
                  <Sparkles className="h-5 w-5 text-white animate-pulse" />
                </div>
              </div>
              <div className="p-5">
              <button
                onClick={handleGenerateRecommendations}
                disabled={generatingRecs}
                  className="w-full mb-5 px-5 py-3 bg-gradient-to-r from-violet-600 to-violet-700 text-white font-semibold rounded-xl hover:from-violet-700 hover:to-violet-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105 disabled:hover:scale-100"
              >
                {generatingRecs ? (
                  <>
                      <RefreshCw className="h-5 w-5 animate-spin" />
                      <span className="text-sm">Génération en cours...</span>
                  </>
                ) : (
                  <>
                      <Lightbulb className="h-5 w-5" />
                      <span className="text-sm">Générer des Recommandations</span>
                  </>
                )}
              </button>

            {recommendations && Array.isArray(recommendations) && recommendations.length > 0 ? (
              <div className="space-y-4">
                {recommendations.map((recGroup, groupIndex) => (
                  <div key={groupIndex} className="space-y-3">
                    {Array.isArray(recGroup) && recGroup.map((rec, index) => (
                          <div key={index} className="group bg-gray-50 rounded-xl p-4 hover:bg-violet-50 transition-all duration-200 border border-gray-100 hover:border-violet-200 hover:shadow-md">
                            <div className="flex items-start space-x-3">
                              <div className="w-8 h-8 bg-violet-100 rounded-xl flex items-center justify-center group-hover:bg-violet-200 transition-colors">
                                <TrendingUp className="h-4 w-4 text-violet-600" />
                              </div>
                              <div className="flex-1">
                                <h3 className="font-bold text-gray-900 mb-2 text-sm">{rec.title}</h3>
                                <p className="text-gray-600 text-xs leading-relaxed">{rec.reason}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                    <div className="w-16 h-16 bg-violet-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Lightbulb className="h-8 w-8 text-violet-600" />
                    </div>
                    <h3 className="text-base font-bold text-gray-900 mb-2">Aucune recommandation</h3>
                    <p className="text-gray-600 mb-4 text-sm">Générez des suggestions d'emploi personnalisées</p>
                    <p className="text-xs text-gray-500 leading-relaxed">
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
