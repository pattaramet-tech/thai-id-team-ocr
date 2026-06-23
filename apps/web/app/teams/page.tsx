"use client";

import { useState, useEffect } from "react";

interface Team {
  id: number;
  name: string;
  ageGroup: string;
  gender: string;
  division?: string;
  competitionYearBE: number;
  createdAt: string;
  updatedAt: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    ageGroup: "U18",
    gender: "Male",
    division: "",
    competitionYearBE: 2569,
  });

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const res = await fetch(`${API_BASE}/teams`);
      if (!res.ok) throw new Error("Failed to fetch teams");
      const data = await res.json();
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
      if (!formData.name.trim()) {
        setError("Team name is required");
        return;
      }

      const res = await fetch(`${API_BASE}/teams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          ageGroup: formData.ageGroup,
          gender: formData.gender,
          division: formData.division || undefined,
          competitionYearBE: formData.competitionYearBE,
        }),
      });

      if (!res.ok) throw new Error("Failed to create team");

      setFormData({
        name: "",
        ageGroup: "U18",
        gender: "Male",
        division: "",
        competitionYearBE: 2569,
      });
      setShowForm(false);
      await fetchTeams();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create team");
    }
  };

  const handleDeleteTeam = async (id: number) => {
    if (!confirm("Are you sure you want to delete this team?")) return;

    try {
      const res = await fetch(`${API_BASE}/teams/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete team");
      await fetchTeams();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete team");
    }
  };

  if (loading) return <div className="p-8">Loading teams...</div>;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-6xl px-4">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Teams</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            {showForm ? "Cancel" : "+ Create Team"}
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {showForm && (
          <div className="mb-8 rounded-lg bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-semibold">Create New Team</h2>
            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Team Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Age Group *
                  </label>
                  <select
                    value={formData.ageGroup}
                    onChange={(e) => setFormData({ ...formData, ageGroup: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  >
                    <option>U14</option>
                    <option>U16</option>
                    <option>U18</option>
                    <option>U20</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gender *
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Mixed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Division (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.division}
                    onChange={(e) => setFormData({ ...formData, division: e.target.value })}
                    placeholder="e.g., Division A"
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Competition Year (BE)
                  </label>
                  <input
                    type="number"
                    value={formData.competitionYearBE}
                    onChange={(e) => setFormData({ ...formData, competitionYearBE: parseInt(e.target.value) })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
              >
                Create Team
              </button>
            </form>
          </div>
        )}

        {teams.length === 0 ? (
          <div className="rounded-lg bg-blue-50 p-6 text-center">
            <p className="text-gray-600">No teams yet. Create your first team to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg bg-white shadow">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Team Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Age Group</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Gender</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Division</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Comp. Year</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Players</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {teams.map((team) => (
                  <tr key={team.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      <a href={`/teams/${team.id}`} className="text-blue-600 hover:text-blue-900">
                        {team.name}
                      </a>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.ageGroup}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.gender}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.division || "-"}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{team.competitionYearBE}</td>
                    <td className="px-6 py-4 text-sm">
                      <a href={`/teams/${team.id}`} className="text-blue-600 hover:text-blue-900">
                        View Players
                      </a>
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
