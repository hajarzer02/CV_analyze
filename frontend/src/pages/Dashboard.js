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
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={fetchCandidates}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de Bord des Candidats</h1>
      </div>

      {/* Job Matching Section */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Correspondance d'Emploi</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-2">
              Description du Poste
            </label>
            <textarea
              id="job-description"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Collez une description de poste ici..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              rows={4}
            />
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleJobMatch}
              disabled={!jobDescription.trim() || isMatching}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Search className="h-4 w-4 mr-2" />
              {isMatching ? 'Correspondance...' : 'Correspondre aux Candidats'}
            </button>
            {showMatchMode && (
              <button
                onClick={handleClearMatch}
                className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <X className="h-4 w-4 mr-2" />
                Effacer la Correspondance
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Match Mode Banner */}
      {showMatchMode && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Search className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <span className="text-blue-800 font-medium">
                  Correspondance avec : {jobDescription.substring(0, 50)}...
                </span>
                <p className="text-blue-600 text-sm mt-1">
                  Les candidats sont triés automatiquement par pourcentage de correspondance (du plus élevé au plus faible)
                </p>
              </div>
            </div>
            <button
              onClick={handleClearMatch}
              className="text-blue-600 hover:text-blue-800"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Filters and Search Section */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtres et Recherche</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search by name */}
          <div>
            <label htmlFor="search-name" className="block text-sm font-medium text-gray-700 mb-2">
              Rechercher par nom
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                id="search-name"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Nom du candidat..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          {/* Status filter */}
          <div>
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
              Filtrer par statut
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">Tous les statuts</option>
              <option value="New">Nouveau</option>
              <option value="Interview Scheduled">Entretien Programmé</option>
              <option value="Offer">Offre</option>
              <option value="Hired">Embauché</option>
              <option value="Rejected">Rejeté</option>
            </select>
          </div>

          {/* Date sort */}
          <div>
            <label htmlFor="date-sort" className="block text-sm font-medium text-gray-700 mb-2">
              Trier par date
            </label>
            <select
              id="date-sort"
              value={dateSortOrder}
              onChange={(e) => {
                setDateSortOrder(e.target.value);
                setSortBy('date');
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="newest">Plus récent en premier</option>
              <option value="oldest">Plus ancien en premier</option>
            </select>
          </div>
        </div>

        {/* Active filters indicator and clear button */}
        {(searchTerm || statusFilter !== 'all' || dateSortOrder !== 'newest') && (
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-gray-600">Filtres actifs :</span>
              {searchTerm && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Recherche: "{searchTerm}"
                  <button
                    onClick={() => setSearchTerm('')}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              {statusFilter !== 'all' && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Statut: {statusFilter}
                  <button
                    onClick={() => setStatusFilter('all')}
                    className="ml-1 text-green-600 hover:text-green-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
              {dateSortOrder !== 'newest' && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  Date: {dateSortOrder === 'oldest' ? 'Plus ancien' : 'Plus récent'}
                  <button
                    onClick={() => setDateSortOrder('newest')}
                    className="ml-1 text-purple-600 hover:text-purple-800"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              )}
            </div>
            <button
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('all');
                setDateSortOrder('newest');
                setSortBy('name');
              }}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <X className="h-4 w-4 mr-2" />
              Effacer tous les filtres
            </button>
          </div>
        )}
      </div>

      {/* Results count */}
      {candidates.length > 0 && (
        <div className="bg-gray-50 px-6 py-3 rounded-lg">
          <p className="text-sm text-gray-600">
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
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${showMatchMode ? 'cursor-default' : 'cursor-pointer hover:bg-gray-100'}`}
                    onClick={showMatchMode ? undefined : () => {
                      setSortBy('name');
                      setSortOrder(sortBy === 'name' && sortOrder === 'asc' ? 'desc' : 'asc');
                    }}
                  >
                    <div className="flex items-center">
                      Nom
                      <ChevronDown className={`h-4 w-4 ml-1 ${showMatchMode ? 'opacity-30' : (sortBy === 'name' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50')}`} />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Compétences
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Emails
                  </th>
                  <th 
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${showMatchMode ? 'cursor-default' : 'cursor-pointer hover:bg-gray-100'}`}
                    onClick={showMatchMode ? undefined : () => {
                      setSortBy('status');
                      setSortOrder(sortBy === 'status' && sortOrder === 'asc' ? 'desc' : 'asc');
                    }}
                  >
                    <div className="flex items-center">
                      Statut
                      <ChevronDown className={`h-4 w-4 ml-1 ${showMatchMode ? 'opacity-30' : (sortBy === 'status' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50')}`} />
                    </div>
                  </th>
                  {showMatchMode && (
                    <th 
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => {
                        setSortBy('match');
                        setSortOrder(sortBy === 'match' && sortOrder === 'asc' ? 'desc' : 'asc');
                      }}
                    >
                      <div className="flex items-center">
                        Correspondance %
                        <ChevronDown className={`h-4 w-4 ml-1 text-blue-600 ${sortBy === 'match' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                        {showMatchMode && (
                          <span className="ml-2 text-xs text-blue-600 font-normal">
                          </span>
                        )}
                      </div>
                    </th>
                  )}
                  {showMatchMode && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Compétences Manquantes
                    </th>
                  )}
                  <th 
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${showMatchMode ? 'cursor-default' : 'cursor-pointer hover:bg-gray-100'}`}
                    onClick={showMatchMode ? undefined : () => {
                      setSortBy('date');
                      setSortOrder(sortBy === 'date' && sortOrder === 'asc' ? 'desc' : 'asc');
                    }}
                  >
                    <div className="flex items-center">
                      Date de Téléchargement
                      <ChevronDown className={`h-4 w-4 ml-1 ${showMatchMode ? 'opacity-30' : (sortBy === 'date' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50')}`} />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filterAndSortCandidates(candidates).map((candidate) => (
                  <tr key={candidate.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {candidate.name || 'Inconnu'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {candidate.skills.slice(0, 3).map((skill, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                          >
                            {skill}
                          </span>
                        ))}
                        {candidate.skills.length > 3 && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            +{candidate.skills.length - 3} de plus
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        {/* <span className="text-gray-500 mr-1">@</span> */}
                        {candidate.email || 'Non spécifié'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={candidate.status || 'New'}
                        onChange={(e) => handleStatusChange(candidate.id, e.target.value)}
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border-0 ${getStatusColor(candidate.status || 'New')}`}
                      >
                        <option value="New">Nouveau</option>
                        <option value="Interview Scheduled">Entretien Programmé</option>
                        <option value="Offer">Offre</option>
                        <option value="Hired">Embauché</option>
                        <option value="Rejected">Rejeté</option>
                      </select>
                    </td>
                    {showMatchMode && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getMatchColor(matchResults?.[candidate.id]?.match || 0)} ${getMatchBackgroundColor(matchResults?.[candidate.id]?.match || 0)}`}>
                          {matchResults?.[candidate.id]?.match || 0}%
                        </div>
                      </td>
                    )}
                    {showMatchMode && (
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {(matchResults?.[candidate.id]?.missing_skills || []).slice(0, 3).map((skill, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800"
                            >
                              {skill}
                            </span>
                          ))}
                          {(matchResults?.[candidate.id]?.missing_skills || []).length > 3 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                              +{(matchResults?.[candidate.id]?.missing_skills || []).length - 3} de plus
                            </span>
                          )}
                        </div>
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(candidate.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <Link
                          to={`/candidate/${candidate.id}`}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-primary-700 bg-primary-100 hover:bg-primary-200 transition-colors"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Voir
                        </Link>
                        <button
                          onClick={() => handleDeleteClick(candidate)}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 transition-colors"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Supprimer
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mt-4">
                Supprimer le Candidat
              </h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Êtes-vous sûr de vouloir supprimer <strong>{deleteModal.candidate?.name || 'ce candidat'}</strong> ? 
                  Cette action ne peut pas être annulée et supprimera également toutes les recommandations d'emploi associées.
                </p>
              </div>
              <div className="flex justify-center space-x-4 mt-4">
                <button
                  onClick={handleDeleteCancel}
                  disabled={deleting}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors disabled:opacity-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
                >
                  {deleting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Suppression...
                    </>
                  ) : (
                    'Supprimer'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
