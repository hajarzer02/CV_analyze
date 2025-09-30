import React, { useEffect, useState } from 'react';
import { getProfile, updateProfile, changeMyPassword } from '../services/api';
import { Shield, Mail, User as UserIcon, KeyRound, Save } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user, login } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState({ name: '', email: '', role: 'user' });
  const [savingInfo, setSavingInfo] = useState(false);
  const [pw, setPw] = useState({ current: '', next: '', confirm: '' });
  const [savingPw, setSavingPw] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const me = await getProfile();
        setInfo({ name: me.name, email: me.email, role: me.role });
        setError(null);
      } catch (e) {
        setError("Impossible de charger le profil");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSaveInfo = async (e) => {
    e.preventDefault();
    try {
      setSavingInfo(true);
      const updated = await updateProfile({ name: info.name, email: info.email });
      // Sync local auth user for header display
      const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
      const newUser = { ...storedUser, name: updated.name, email: updated.email };
      localStorage.setItem('user', JSON.stringify(newUser));
      // If context login expects token unchanged, just update state
      login(localStorage.getItem('token'), newUser);
      setSuccessMsg('Profil mis à jour');
      setError(null);
    } catch (err) {
      setError("Échec de la mise à jour du profil");
    } finally {
      setSavingInfo(false);
      setTimeout(() => setSuccessMsg(''), 2500);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    try {
      if (!pw.next || pw.next.length < 6) {
        setError('Le nouveau mot de passe doit contenir au moins 6 caractères');
        return;
      }
      if (pw.next !== pw.confirm) {
        setError('Les mots de passe ne correspondent pas');
        return;
      }
      setSavingPw(true);
      await changeMyPassword(pw.current, pw.next);
      setPw({ current: '', next: '', confirm: '' });
      setSuccessMsg('Mot de passe mis à jour');
      setError(null);
    } catch (err) {
      setError("Échec du changement de mot de passe");
    } finally {
      setSavingPw(false);
      setTimeout(() => setSuccessMsg(''), 2500);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Shield className="h-8 w-8 text-emerald-600" />
            <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
          </div>
          <p className="text-gray-600">Gérez vos informations personnelles et votre mot de passe.</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4 text-red-700">{error}</div>
        )}
        {successMsg && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4 text-green-700">{successMsg}</div>
        )}

        <div className="grid grid-cols-1 gap-8">
          <div className="bg-white shadow rounded-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Informations du profil</h2>
            <form onSubmit={handleSaveInfo} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nom</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <UserIcon className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={info.name}
                    onChange={(e) => setInfo({ ...info, name: e.target.value })}
                    className="block w-full pl-10 border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="email"
                    value={info.email}
                    onChange={(e) => setInfo({ ...info, email: e.target.value })}
                    className="block w-full pl-10 border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={savingInfo}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700"
                >
                  <Save className="h-4 w-4 mr-2" /> Sauvegarder
                </button>
              </div>
            </form>
          </div>

          <div className="bg-white shadow rounded-md p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Changer le mot de passe</h2>
            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Mot de passe actuel</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <KeyRound className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="password"
                    value={pw.current}
                    onChange={(e) => setPw({ ...pw, current: e.target.value })}
                    className="block w-full pl-10 border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Nouveau mot de passe</label>
                <input
                  type="password"
                  value={pw.next}
                  onChange={(e) => setPw({ ...pw, next: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Confirmer le nouveau mot de passe</label>
                <input
                  type="password"
                  value={pw.confirm}
                  onChange={(e) => setPw({ ...pw, confirm: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={savingPw}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Mettre à jour
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;


