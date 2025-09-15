import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Eye, Calendar, Code, Trash2, AlertTriangle, Search, X, ChevronDown } from 'lucide-react';
import { getCandidates, deleteCandidate, updateCandidateStatus, matchJob } from '../services/api';

const Dashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, candidate: null });
  const [deleting, setDeleting] = useState(false);
  
  // Job matching state
  const [jobDescription, setJobDescription] = useState('');
  const [isMatching, setIsMatching] = useState(false);
  const [matchResults, setMatchResults] = useState(null);
  const [showMatchMode, setShowMatchMode] = useState(false);
  const [sortBy, setSortBy] = useState('name'); // name, match, status, date
  const [sortOrder, setSortOrder] = useState('asc'); // asc, desc
  
  // Filter and search state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, New, Interview Scheduled, Offer, Hired, Rejected
  const [dateSortOrder, setDateSortOrder] = useState('newest'); // newest, oldest

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const data = await getCandidates();
      setCandidates(data);
    } catch (err) {
      setError('Échec du chargement des candidats');
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (candidate) => {
    setDeleteModal({ isOpen: true, candidate });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteModal.candidate) return;

    try {
      setDeleting(true);
      await deleteCandidate(deleteModal.candidate.id);
      
      // Remove the candidate from the list
      setCandidates(candidates.filter(c => c.id !== deleteModal.candidate.id));
      
      // Close modal
      setDeleteModal({ isOpen: false, candidate: null });
    } catch (err) {
      setError('Échec de la suppression du candidat');
      console.error('Error deleting candidate:', err);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteModal({ isOpen: false, candidate: null });
  };

  const handleStatusChange = async (candidateId, newStatus) => {
    try {
      await updateCandidateStatus(candidateId, newStatus);
      
      // Update the candidate in the local state
      setCandidates(candidates.map(candidate => 
        candidate.id === candidateId 
          ? { ...candidate, status: newStatus }
          : candidate
      ));
    } catch (err) {
      setError('Échec de la mise à jour du statut du candidat');
      console.error('Error updating status:', err);
    }
  };

  const handleJobMatch = async () => {
    if (!jobDescription.trim()) return;
    
    try {
      setIsMatching(true);
      const results = await matchJob(jobDescription);
      
      // Create a map of candidate_id to match data
      const matchMap = {};
      results.forEach(match => {
        matchMap[match.candidate_id] = {
          match: match.match,
          missing_skills: match.missing_skills
        };
      });
      
      setMatchResults(matchMap);
      setShowMatchMode(true);
    } catch (err) {
      setError('Échec de la correspondance d\'emploi');
      console.error('Error matching job:', err);
    } finally {
      setIsMatching(false);
    }
  };

  const handleClearMatch = () => {
    setMatchResults(null);
    setShowMatchMode(false);
    setJobDescription('');
  };

  const getStatusColor = (status) => {
    const colors = {
      'New': 'bg-gray-100 text-gray-800',
      'Interview Scheduled': 'bg-blue-100 text-blue-800',
      'Offer': 'bg-yellow-100 text-yellow-800',
      'Hired': 'bg-green-100 text-green-800',
      'Rejected': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getMatchColor = (match) => {
    if (match >= 80) return 'text-green-600 font-semibold';
    if (match >= 60) return 'text-yellow-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  const getMatchBackgroundColor = (match) => {
    if (match >= 80) return 'bg-green-100';
    if (match >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const filterAndSortCandidates = (candidates) => {
    // Appliquer les filtres
    let filteredCandidates = candidates.filter(candidate => {
      // Filtre par nom (recherche)
      const matchesSearch = !searchTerm || 
        (candidate.name && candidate.name.toLowerCase().includes(searchTerm.toLowerCase()));
      
      // Filtre par statut
      const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });

    // Appliquer le tri
    return [...filteredCandidates].sort((a, b) => {
      let aValue, bValue;
      
      // Si le mode de correspondance est actif, trier automatiquement par pourcentage de correspondance
      if (showMatchMode && matchResults) {
        aValue = matchResults[a.id]?.match || 0;
        bValue = matchResults[b.id]?.match || 0;
        // Tri décroissant (plus élevé en premier)
        return bValue - aValue;
      }
      
      // Sinon, utiliser le tri normal basé sur sortBy
      switch (sortBy) {
        case 'match':
          aValue = matchResults?.[a.id]?.match || 0;
          bValue = matchResults?.[b.id]?.match || 0;
          break;
        case 'status':
          aValue = a.status || 'New';
          bValue = b.status || 'New';
          break;
        case 'date':
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          // Pour les dates, utiliser l'ordre spécifique
          if (dateSortOrder === 'newest') {
            return bValue - aValue; // Plus récent en premier
          } else {
            return aValue - bValue; // Plus ancien en premier
          }
        default:
          aValue = a.name || 'Inconnu';
          bValue = b.name || 'Inconnu';
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-64 space-y-4">
        <div className="relative">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200"></div>
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent absolute top-0 left-0"></div>
        </div>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-700">Chargement des candidats</h3>
          <p className="text-gray-500 text-sm">Analyse des données en cours...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md mx-auto">
          <div className="p-3 bg-red-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Erreur de chargement</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchCandidates}
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors duration-200 shadow-lg hover:shadow-xl"
          >
            <Code className="h-4 w-4 mr-2" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
            <Code className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Tableau de Bord des Candidats
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              Gérez et analysez vos candidats avec l'intelligence artificielle
            </p>
          </div>
        </div>
      </div>

      {/* Job Matching Section */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-lg border border-blue-200 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
          <div className="flex items-center">
            <div className="p-2 bg-white/20 rounded-lg mr-3">
              <Search className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Correspondance d'Emploi IA</h2>
              <p className="text-blue-100 text-sm">Trouvez les meilleurs candidats grâce à l'intelligence artificielle</p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="space-y-6">
            {/* Job Description Input */}
            <div className="space-y-3">
              <label htmlFor="job-description" className="block text-sm font-semibold text-gray-700">
                Description du Poste
              </label>
              <div className="relative">
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Décrivez le poste recherché... (ex: Développeur React avec 3 ans d'expérience, maîtrise de TypeScript, expérience avec les tests unitaires)"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none"
                  rows={4}
                />
                <div className="absolute bottom-3 right-3 text-xs text-gray-400">
                  {jobDescription.length}/500 caractères
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleJobMatch}
                disabled={!jobDescription.trim() || isMatching}
                className="flex-1 inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                {isMatching ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <Search className="h-5 w-5 mr-3" />
                    Analyser les Candidats
                  </>
                )}
              </button>
              
              {showMatchMode && (
                <button
                  onClick={handleClearMatch}
                  className="inline-flex items-center justify-center px-6 py-3 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  <X className="h-5 w-5 mr-2" />
                  Effacer
                </button>
              )}
            </div>

            {/* Tips Section */}
            <div className="bg-white/60 rounded-lg p-4 border border-blue-200">
              <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Conseils pour de meilleurs résultats
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Incluez les compétences techniques requises</li>
                <li>• Mentionnez le niveau d'expérience souhaité</li>
                <li>• Ajoutez les technologies et outils spécifiques</li>
                <li>• Décrivez les responsabilités principales</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Match Mode Banner */}
      {showMatchMode && (
        <div className="bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 border-2 border-green-200 rounded-xl shadow-lg overflow-hidden animate-in slide-in-from-top-2 duration-500">
          <div className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl shadow-lg">
                    <Search className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="text-lg font-bold text-green-800">Mode Correspondance Actif</h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 animate-pulse">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-1.5"></span>
                      En cours
                    </span>
                  </div>
                  <div className="bg-white/70 rounded-lg p-3 border border-green-200">
                    <p className="text-sm font-medium text-gray-700 mb-1">Recherche basée sur :</p>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      "{jobDescription.length > 100 ? jobDescription.substring(0, 100) + '...' : jobDescription}"
                    </p>
                  </div>
                  <div className="mt-3 flex items-center space-x-4 text-sm text-green-700">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      Tri automatique par correspondance
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
                      {candidates.length} candidat{candidates.length > 1 ? 's' : ''} analysé{candidates.length > 1 ? 's' : ''}
                    </div>
                  </div>
                </div>
              </div>
              <button
                onClick={handleClearMatch}
                className="flex-shrink-0 p-2 text-green-600 hover:text-green-800 hover:bg-white/50 rounded-lg transition-all duration-200 group"
                title="Fermer le mode correspondance"
              >
                <X className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
              </button>
            </div>
          </div>
          
          {/* Progress indicator */}
          <div className="h-1 bg-gradient-to-r from-green-400 via-emerald-400 to-teal-400 animate-pulse"></div>
        </div>
      )}

      {/* Filters and Search Section */}
      <div className="bg-gradient-to-br from-gray-50 to-slate-100 rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-slate-600 to-gray-700 px-6 py-4">
          <div className="flex items-center">
            <div className="p-2 bg-white/20 rounded-lg mr-3">
              <Search className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Filtres et Recherche</h2>
              <p className="text-gray-200 text-sm">Affinez votre recherche de candidats</p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Search by name */}
            <div className="space-y-3">
              <label htmlFor="search-name" className="block text-sm font-semibold text-gray-700 flex items-center">
                <Search className="h-4 w-4 mr-2 text-blue-600" />
                Rechercher par nom
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors duration-200" />
                </div>
                <input
                  type="text"
                  id="search-name"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Tapez le nom du candidat..."
                  className="w-full pl-10 pr-10 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white"
                />
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm('')}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors duration-200"
                  >
                    <X className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Status filter */}
            <div className="space-y-3">
              <label htmlFor="status-filter" className="block text-sm font-semibold text-gray-700 flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Filtrer par statut
              </label>
              <div className="relative">
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200 bg-white appearance-none cursor-pointer"
                >
                  <option value="all">Tous les statuts</option>
                  <option value="New"> Nouveau</option>
                  <option value="Interview Scheduled"> Entretien Programmé</option>
                  <option value="Offer"> Offre</option>
                  <option value="Hired"> Embauché</option>
                  <option value="Rejected"> Rejeté</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>

            {/* Date sort */}
            <div className="space-y-3">
              <label htmlFor="date-sort" className="block text-sm font-semibold text-gray-700 flex items-center">
                <Calendar className="h-4 w-4 mr-2 text-purple-600" />
                Trier par date
              </label>
              <div className="relative">
                <select
                  id="date-sort"
                  value={dateSortOrder}
                  onChange={(e) => {
                    setDateSortOrder(e.target.value);
                    setSortBy('date');
                  }}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white appearance-none cursor-pointer"
                >
                  <option value="newest"> Plus récent en premier</option>
                  <option value="oldest"> Plus ancien en premier</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Active filters indicator and clear button */}
        {(searchTerm || statusFilter !== 'all' || dateSortOrder !== 'newest') && (
          <div className="mt-6 p-4 bg-white/80 rounded-xl border border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-sm font-semibold text-gray-700 flex items-center">
                  <div className="w-2 h-2 bg-orange-500 rounded-full mr-2"></div>
                  Filtres actifs :
                </span>
                <div className="flex flex-wrap gap-2">
                  {searchTerm && (
                    <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200 shadow-sm">
                      <Search className="h-3 w-3 mr-1.5" />
                      "{searchTerm}"
                      <button
                        onClick={() => setSearchTerm('')}
                        className="ml-2 text-blue-600 hover:text-blue-800 transition-colors duration-200"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                  {statusFilter !== 'all' && (
                    <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-200 shadow-sm">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-1.5"></div>
                      {statusFilter}
                      <button
                        onClick={() => setStatusFilter('all')}
                        className="ml-2 text-green-600 hover:text-green-800 transition-colors duration-200"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                  {dateSortOrder !== 'newest' && (
                    <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-purple-100 text-purple-800 border border-purple-200 shadow-sm">
                      <Calendar className="h-3 w-3 mr-1.5" />
                      {dateSortOrder === 'oldest' ? 'Plus ancien' : 'Plus récent'}
                      <button
                        onClick={() => setDateSortOrder('newest')}
                        className="ml-2 text-purple-600 hover:text-purple-800 transition-colors duration-200"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setDateSortOrder('newest');
                  setSortBy('name');
                }}
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white font-semibold rounded-xl hover:from-red-600 hover:to-pink-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <X className="h-4 w-4 mr-2" />
                Effacer tous les filtres
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Results count */}
      {candidates.length > 0 && (
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Code className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-800">
                  {(() => {
                    const filteredCandidates = filterAndSortCandidates(candidates);
                    const totalCandidates = candidates.length;
                    const filteredCount = filteredCandidates.length;
                    
                    if (filteredCount === totalCandidates) {
                      return `${totalCandidates} candidat${totalCandidates > 1 ? 's' : ''} au total`;
                    } else {
                      return `${filteredCount} candidat${filteredCount > 1 ? 's' : ''} sur ${totalCandidates} (filtré${searchTerm || statusFilter !== 'all' ? 's' : ''})`;
                    }
                  })()}
                </p>
                <p className="text-xs text-gray-600">
                  {(() => {
                    const filteredCandidates = filterAndSortCandidates(candidates);
                    const totalCandidates = candidates.length;
                    const filteredCount = filteredCandidates.length;
                    
                    if (filteredCount === totalCandidates) {
                      return "Tous les candidats sont affichés";
                    } else {
                      return `Filtrage actif - ${totalCandidates - filteredCount} candidat${totalCandidates - filteredCount > 1 ? 's' : ''} masqué${totalCandidates - filteredCount > 1 ? 's' : ''}`;
                    }
                  })()}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-indigo-600 font-medium">Mise à jour en temps réel</span>
            </div>
          </div>
        </div>
      )}

      {candidates.length === 0 ? (
        <div className="text-center py-12">
          <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun candidat trouvé</h3>
          <p className="text-gray-600 mb-4">Téléchargez votre premier CV pour commencer</p>
          <Link
            to="/upload"
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Télécharger CV
          </Link>
        </div>
      ) : filterAndSortCandidates(candidates).length === 0 ? (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun candidat ne correspond aux filtres</h3>
          <p className="text-gray-600 mb-4">Essayez de modifier vos critères de recherche ou de filtrage</p>
          <button
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('all');
              setDateSortOrder('newest');
              setSortBy('name');
            }}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Effacer tous les filtres
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Table Header with Sort Controls */}
          <div className="bg-gradient-to-r from-slate-50 to-gray-50 rounded-xl p-6 border border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Candidats</h3>
                <p className="text-sm text-gray-600">
                  {filterAndSortCandidates(candidates).length} candidat{filterAndSortCandidates(candidates).length > 1 ? 's' : ''} trouvé{filterAndSortCandidates(candidates).length > 1 ? 's' : ''}
                </p>
              </div>
              
              {/* Sort Controls */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => {
                    setSortBy('name');
                    setSortOrder(sortBy === 'name' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                  className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    sortBy === 'name' 
                      ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                      : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <span>Nom</span>
                  <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'name' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                </button>
                
                <button
                  onClick={() => {
                    setSortBy('status');
                    setSortOrder(sortBy === 'status' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                  className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    sortBy === 'status' 
                      ? 'bg-green-100 text-green-700 border border-green-200' 
                      : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <span>Statut</span>
                  <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'status' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                </button>
                
                <button
                  onClick={() => {
                    setSortBy('date');
                    setSortOrder(sortBy === 'date' && sortOrder === 'asc' ? 'desc' : 'asc');
                  }}
                  className={`inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    sortBy === 'date' 
                      ? 'bg-purple-100 text-purple-700 border border-purple-200' 
                      : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <Calendar className="h-4 w-4 mr-1" />
                  <span>Date</span>
                  <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'date' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Candidates Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filterAndSortCandidates(candidates).map((candidate, index) => (
              <div
                key={candidate.id}
                className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 group"
                style={{
                  animationDelay: `${index * 100}ms`,
                  animation: 'fadeInUp 0.6s ease-out forwards'
                }}
              >
                {/* Card Header */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-100">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                        {(candidate.name || 'U').charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-200">
                          {candidate.name || 'Inconnu'}
                        </h3>
                        <p className="text-sm text-gray-600 flex items-center">
                          <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                          {candidate.email || 'Email non spécifié'}
                        </p>
                      </div>
                    </div>
                    
                    {/* Match Score Badge */}
                    {showMatchMode && (
                      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold shadow-lg ${getMatchColor(matchResults?.[candidate.id]?.match || 0)} ${getMatchBackgroundColor(matchResults?.[candidate.id]?.match || 0)}`}>
                        {matchResults?.[candidate.id]?.match || 0}%
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-6 space-y-4">
                  {/* Skills Section */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                      <Code className="h-4 w-4 mr-2 text-blue-600" />
                      Compétences
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {candidate.skills.slice(0, 4).map((skill, skillIndex) => (
                        <span
                          key={skillIndex}
                          className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 border border-blue-200"
                        >
                          {skill}
                        </span>
                      ))}
                      {candidate.skills.length > 4 && (
                        <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
                          +{candidate.skills.length - 4} autres
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Missing Skills (Match Mode) */}
                  {showMatchMode && matchResults?.[candidate.id]?.missing_skills && matchResults[candidate.id].missing_skills.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                        <AlertTriangle className="h-4 w-4 mr-2 text-red-500" />
                        Compétences manquantes
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {matchResults[candidate.id].missing_skills.slice(0, 3).map((skill, skillIndex) => (
                          <span
                            key={skillIndex}
                            className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-red-100 text-red-800 border border-red-200"
                          >
                            {skill}
                          </span>
                        ))}
                        {matchResults[candidate.id].missing_skills.length > 3 && (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
                            +{matchResults[candidate.id].missing_skills.length - 3} autres
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Status and Date */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                      <select
                        value={candidate.status || 'New'}
                        onChange={(e) => handleStatusChange(candidate.id, e.target.value)}
                        className={`text-xs font-semibold px-3 py-1.5 rounded-lg border-0 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 ${getStatusColor(candidate.status || 'New')}`}
                      >
                        <option value="New">Nouveau</option>
                        <option value="Interview Scheduled">Entretien</option>
                        <option value="Offer">Offre</option>
                        <option value="Hired">Embauché</option>
                        <option value="Rejected">Rejeté</option>
                      </select>
                    </div>
                    <div className="flex items-center text-xs text-gray-500">
                      <Calendar className="h-3 w-3 mr-1" />
                      {formatDate(candidate.created_at)}
                    </div>
                  </div>
                </div>

                {/* Card Footer */}
                <div className="bg-gray-50 px-6 py-4 border-t border-gray-100">
                  <div className="flex space-x-2">
                    <Link
                      to={`/candidate/${candidate.id}`}
                      className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      Voir le profil
                    </Link>
                    <button
                      onClick={() => handleDeleteClick(candidate)}
                      className="inline-flex items-center justify-center px-4 py-2 bg-white text-red-600 text-sm font-semibold rounded-lg border border-red-200 hover:bg-red-50 hover:border-red-300 transition-all duration-200 shadow-md hover:shadow-lg"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full transform transition-all duration-300 scale-100">
            <div className="p-8">
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                  <AlertTriangle className="h-8 w-8 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Supprimer le Candidat
                </h3>
                <p className="text-gray-600 mb-6">
                  Êtes-vous sûr de vouloir supprimer <strong className="text-gray-900">{deleteModal.candidate?.name || 'ce candidat'}</strong> ? 
                  Cette action ne peut pas être annulée.
                </p>
                
                <div className="flex space-x-3">
                  <button
                    onClick={handleDeleteCancel}
                    disabled={deleting}
                    className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-all duration-200 disabled:opacity-50"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleDeleteConfirm}
                    disabled={deleting}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 disabled:opacity-50 flex items-center justify-center shadow-lg hover:shadow-xl"
                  >
                    {deleting ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Suppression...
                      </>
                    ) : (
                      <>
                        <Trash2 className="h-5 w-5 mr-2" />
                        Supprimer
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
