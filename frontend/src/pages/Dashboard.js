import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Eye, Calendar, MapPin, Code, Trash2, AlertTriangle, Search, X, ChevronDown } from 'lucide-react';
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
  const [sortBy, setSortBy] = useState('name'); // name, match, status
  const [sortOrder, setSortOrder] = useState('asc'); // asc, desc

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const data = await getCandidates();
      setCandidates(data);
    } catch (err) {
      setError('Failed to fetch candidates');
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
      setError('Failed to delete candidate');
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
      setError('Failed to update candidate status');
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
      setError('Failed to match job');
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

  const sortCandidates = (candidates) => {
    return [...candidates].sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'match':
          aValue = matchResults?.[a.id]?.match || 0;
          bValue = matchResults?.[b.id]?.match || 0;
          break;
        case 'status':
          aValue = a.status || 'New';
          bValue = b.status || 'New';
          break;
        default:
          aValue = a.name || 'Unknown';
          bValue = b.name || 'Unknown';
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
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
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Candidates Dashboard</h1>
        <Link
          to="/upload"
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
        >
          Upload New CV
        </Link>
      </div>

      {/* Job Matching Section */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Matching</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              id="job-description"
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste a job description here..."
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
              {isMatching ? 'Matching...' : 'Match Candidates'}
            </button>
            {showMatchMode && (
              <button
                onClick={handleClearMatch}
                className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <X className="h-4 w-4 mr-2" />
                Clear Match
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
              <span className="text-blue-800 font-medium">
                Matching against: {jobDescription.substring(0, 50)}...
              </span>
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

      {candidates.length === 0 ? (
        <div className="text-center py-12">
          <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
          <p className="text-gray-600 mb-4">Upload your first CV to get started</p>
          <Link
            to="/upload"
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Upload CV
          </Link>
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => {
                      setSortBy('name');
                      setSortOrder(sortBy === 'name' && sortOrder === 'asc' ? 'desc' : 'asc');
                    }}
                  >
                    <div className="flex items-center">
                      Name
                      <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'name' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Skills
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => {
                      setSortBy('status');
                      setSortOrder(sortBy === 'status' && sortOrder === 'asc' ? 'desc' : 'asc');
                    }}
                  >
                    <div className="flex items-center">
                      Status
                      <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'status' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
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
                        Match %
                        <ChevronDown className={`h-4 w-4 ml-1 ${sortBy === 'match' ? (sortOrder === 'asc' ? 'rotate-180' : '') : 'opacity-50'}`} />
                      </div>
                    </th>
                  )}
                  {showMatchMode && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Missing Skills
                    </th>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortCandidates(candidates).map((candidate) => (
                  <tr key={candidate.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {candidate.name || 'Unknown'}
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
                            +{candidate.skills.length - 3} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mr-1" />
                        {candidate.location || 'Not specified'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={candidate.status || 'New'}
                        onChange={(e) => handleStatusChange(candidate.id, e.target.value)}
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border-0 ${getStatusColor(candidate.status || 'New')}`}
                      >
                        <option value="New">New</option>
                        <option value="Interview Scheduled">Interview Scheduled</option>
                        <option value="Offer">Offer</option>
                        <option value="Hired">Hired</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </td>
                    {showMatchMode && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm ${getMatchColor(matchResults?.[candidate.id]?.match || 0)}`}>
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
                              +{(matchResults?.[candidate.id]?.missing_skills || []).length - 3} more
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
                          View
                        </Link>
                        <button
                          onClick={() => handleDeleteClick(candidate)}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 transition-colors"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
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
                Delete Candidate
              </h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Are you sure you want to delete <strong>{deleteModal.candidate?.name || 'this candidate'}</strong>? 
                  This action cannot be undone and will also delete all associated job recommendations.
                </p>
              </div>
              <div className="flex justify-center space-x-4 mt-4">
                <button
                  onClick={handleDeleteCancel}
                  disabled={deleting}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center"
                >
                  {deleting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Deleting...
                    </>
                  ) : (
                    'Delete'
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
