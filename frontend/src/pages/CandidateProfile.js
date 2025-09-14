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
  RefreshCw
} from 'lucide-react';
import { getCandidate, generateRecommendations } from '../services/api';

const CandidateProfile = () => {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingRecs, setGeneratingRecs] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCandidate();
  }, [id]);

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
      
      // Update candidate with new recommendations
      setCandidate(prev => ({
        ...prev,
        recommendations: [...(prev.recommendations || []), response.recommendations]
      }));
    } catch (err) {
      setError('Échec de la génération des recommandations');
      console.error('Error generating recommendations:', err);
    } finally {
      setGeneratingRecs(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error || 'Candidat non trouvé'}</div>
        <Link
          to="/"
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Retour au Tableau de Bord
        </Link>
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/"
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {candidate.name || 'Candidat Inconnu'}
            </h1>
            <p className="text-gray-600">Profil du Candidat</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - CV Information */}
        <div className="space-y-6">
          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations de Contact
            </h2>
            <div className="space-y-3">
              {contactInfo.emails?.map((email, index) => (
                <div key={index} className="flex items-center text-gray-600">
                  <Mail className="h-4 w-4 mr-3" />
                  <a href={`mailto:${email}`} className="hover:text-primary-600">
                    {email}
                  </a>
                </div>
              ))}
              {contactInfo.phones?.map((phone, index) => (
                <div key={index} className="flex items-center text-gray-600">
                  <Phone className="h-4 w-4 mr-3" />
                  <a href={`tel:${phone}`} className="hover:text-primary-600">
                    {phone}
                  </a>
                </div>
              ))}
              {contactInfo.address && (
                <div className="flex items-center text-gray-600">
                  <MapPin className="h-4 w-4 mr-3" />
                  <span>{contactInfo.address}</span>
                </div>
              )}
              {contactInfo.linkedin && (
                <div className="flex items-center text-gray-600">
                  <Linkedin className="h-4 w-4 mr-3" />
                  <a 
                    href={`https://${contactInfo.linkedin}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:text-primary-600"
                  >
                    {contactInfo.linkedin}
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Professional Summary */}
          {summary.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Résumé Professionnel</h2>
              <div className="space-y-2">
                {summary.map((line, index) => (
                  <p key={index} className="text-gray-600">{line}</p>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          {skills.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Code className="h-5 w-5 mr-2" />
                Compétences
              </h2>
              <div className="flex flex-wrap gap-2">
                {skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Languages */}
          {languages.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Globe className="h-5 w-5 mr-2" />
                Langues
              </h2>
              <div className="space-y-2">
                {languages.map((lang, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="font-medium text-gray-900">{lang.language}</span>
                    <span className="text-gray-600">{lang.level}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {education.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <GraduationCap className="h-5 w-5 mr-2" />
                Formation
              </h2>
              <div className="space-y-4">
                {education.map((edu, index) => (
                  <div key={index} className="border-l-4 border-primary-200 pl-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">{edu.degree}</h3>
                        {edu.institution && (
                          <p className="text-gray-600">{edu.institution}</p>
                        )}
                      </div>
                      {edu.date_range && (
                        <span className="text-sm text-gray-500">{edu.date_range}</span>
                      )}
                    </div>
                    {edu.details.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {edu.details.map((detail, detailIndex) => (
                          <li key={detailIndex} className="text-sm text-gray-600">
                            • {detail}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Experience */}
          {experience.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Briefcase className="h-5 w-5 mr-2" />
                Expérience
              </h2>
              <div className="space-y-4">
                {experience.map((exp, index) => (
                  <div key={index} className="border-l-4 border-primary-200 pl-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium text-gray-900">{exp.role}</h3>
                        <p className="text-gray-600">{exp.company}</p>
                      </div>
                      {exp.date_range && (
                        <span className="text-sm text-gray-500">{exp.date_range}</span>
                      )}
                    </div>
                    {exp.details.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {exp.details.map((detail, detailIndex) => (
                          <li key={detailIndex} className="text-sm text-gray-600">
                            • {detail}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {projects.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Projets</h2>
              <div className="space-y-4">
                {projects.map((project, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <h3 className="font-medium text-gray-900">{project.title}</h3>
                    {project.description && (
                      <p className="text-gray-600 mt-1">{project.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Job Recommendations */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <Lightbulb className="h-5 w-5 mr-2" />
                Recommandations d'Emploi
              </h2>
              <button
                onClick={handleGenerateRecommendations}
                disabled={generatingRecs}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {generatingRecs ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Génération...</span>
                  </>
                ) : (
                  <>
                    <Lightbulb className="h-4 w-4" />
                    <span>Générer des Recommandations</span>
                  </>
                )}
              </button>
            </div>

            {recommendations && recommendations.length > 0 ? (
              <div className="space-y-4">
                {recommendations.map((recGroup, groupIndex) => (
                  <div key={groupIndex} className="space-y-3">
                    {recGroup.map((rec, index) => (
                      <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                        <h3 className="font-medium text-gray-900 mb-2">{rec.title}</h3>
                        <p className="text-gray-600 text-sm">{rec.reason}</p>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">Aucune recommandation pour le moment</p>
                <p className="text-sm text-gray-500">
                  Cliquez sur "Générer des Recommandations" pour obtenir des suggestions d'emploi alimentées par l'IA
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;
