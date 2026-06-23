"use client";

import { useState, useEffect } from "react";
import { api, type Team } from "@/lib/api";

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: "", ageGroup: "", gender: "" });

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const data = await api.teams.list();
      setTeams(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load teams");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.teams.create({
        name: formData.name,
        ageGroup: formData.ageGroup,
        gender: formData.gender,
      });
      setFormData({ name: "", ageGroup: "", gender: "" });
      setShowForm(false);
      await fetchTeams();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create team");
    }
  };

  const handleDeleteTeam = async (id: number) => {
    if (confirm("Are you sure you want to delete this team?")) {
      try {
        await api.teams.delete(id);
        await fetchTeams();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete team");
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Teams</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            {showForm ? "Cancel" : "Create Team"}
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {showForm && (
          <form onSubmit={handleCreateTeam} className="mb-8 rounded-lg bg-white p-6 shadow">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Team Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full rounded border border-gray-300 px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Age Group
                </label>
                <input
                  type="text"
                  value={formData.ageGroup}
                  onChange={(e) => setFormData({ ...formData, ageGroup: e.target.value })}
                  placeholder="e.g., Under 18"
                  className="mt-1 block w-full rounded border border-gray-300 px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Gender
                </label>
                <input
                  type="text"
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  placeholder="e.g., Male, Female, Mixed"
                  className="mt-1 block w-full rounded border border-gray-300 px-3 py-2"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="mt-4 rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700"
            >
              Create Team
            </button>
          </form>
        )}

        {loading ? (
          <p className="text-gray-600">Loading teams...</p>
        ) : teams.length === 0 ? (
          <p className="text-gray-600">No teams yet. Create one to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full rounded-lg bg-white shadow">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Team Name
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Age Group
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Gender
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Created
                  </th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {teams.map((team) => (
                  <tr key={team.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{team.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.ageGroup}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.gender}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(team.createdAt).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDeleteTeam(team.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
