"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

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

interface Player {
  id: number;
  teamId: number;
  firstName: string;
  lastName: string;
  fullName: string;
  dateOfBirth: string | null;
  birthYearBE: number | null;
  eligibilityStatus: "eligible" | "over_age" | "unknown";
  eligibilityNote: string | null;
  status: string;
  createdAt: string;
  updatedAt: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EligibilityBadge = ({ status }: { status: string }) => {
  const badgeStyles = {
    eligible: "bg-green-100 text-green-800",
    over_age: "bg-red-100 text-red-800",
    unknown: "bg-gray-100 text-gray-800",
  };

  const labels = {
    eligible: "✓ Eligible",
    over_age: "✗ Over Age",
    unknown: "? Unknown",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badgeStyles[status as keyof typeof badgeStyles]}`}>
      {labels[status as keyof typeof labels]}
    </span>
  );
};

export default function TeamDetailPage() {
  const params = useParams();
  const router = useRouter();
  const teamId = parseInt(params.teamId as string);

  const [team, setTeam] = useState<Team | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    dateOfBirth: "",
  });

  useEffect(() => {
    fetchTeamAndPlayers();
  }, [teamId]);

  const fetchTeamAndPlayers = async () => {
    try {
      const teamRes = await fetch(`${API_BASE}/teams/${teamId}`);
      if (!teamRes.ok) throw new Error("Team not found");
      const teamData = await teamRes.json();
      setTeam(teamData);

      const playersRes = await fetch(`${API_BASE}/players?team_id=${teamId}`);
      if (!playersRes.ok) throw new Error("Failed to fetch players");
      const playersData = await playersRes.json();
      setPlayers(playersData);

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleAddPlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!formData.firstName.trim() || !formData.lastName.trim()) {
        setError("First name and last name are required");
        return;
      }

      const res = await fetch(`${API_BASE}/players`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          teamId,
          firstName: formData.firstName,
          lastName: formData.lastName,
          dateOfBirth: formData.dateOfBirth || null,
        }),
      });

      if (!res.ok) throw new Error("Failed to add player");

      setFormData({
        firstName: "",
        lastName: "",
        dateOfBirth: "",
      });
      setShowForm(false);
      await fetchTeamAndPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add player");
    }
  };

  const handleDeletePlayer = async (playerId: number) => {
    if (!confirm("Delete this player?")) return;

    try {
      const res = await fetch(`${API_BASE}/players/${playerId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete player");
      await fetchTeamAndPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete player");
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!team) return <div className="p-8 text-red-600">Team not found</div>;

  const eligibleCount = players.filter((p) => p.eligibilityStatus === "eligible").length;
  const overAgeCount = players.filter((p) => p.eligibilityStatus === "over_age").length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-6xl px-4">
        <button
          onClick={() => router.back()}
          className="mb-6 text-blue-600 hover:text-blue-900"
        >
          ← Back to Teams
        </button>

        {/* Team Info */}
        <div className="mb-8 rounded-lg bg-white p-6 shadow">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{team.name}</h1>
              <p className="text-gray-600">
                {team.ageGroup} • {team.gender}
                {team.division && ` • ${team.division}`}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Competition Year (BE)</p>
              <p className="text-2xl font-bold text-gray-900">{team.competitionYearBE}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-600">Total Players</p>
              <p className="text-2xl font-bold">{players.length}</p>
            </div>
            <div className="rounded-lg bg-green-50 p-4">
              <p className="text-sm text-green-700">Eligible</p>
              <p className="text-2xl font-bold text-green-900">{eligibleCount}</p>
            </div>
            <div className="rounded-lg bg-red-50 p-4">
              <p className="text-sm text-red-700">Over Age</p>
              <p className="text-2xl font-bold text-red-900">{overAgeCount}</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Add Player Form */}
        <div className="mb-8">
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            {showForm ? "Cancel" : "+ Add Player"}
          </button>

          {showForm && (
            <form onSubmit={handleAddPlayer} className="mt-4 rounded-lg bg-white p-6 shadow">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name *
                  </label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date of Birth (Optional)
                  </label>
                  <input
                    type="date"
                    value={formData.dateOfBirth}
                    onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
              </div>
              <button
                type="submit"
                className="mt-4 rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
              >
                Add Player
              </button>
            </form>
          )}
        </div>

        {/* Players List */}
        {players.length === 0 ? (
          <div className="rounded-lg bg-blue-50 p-6 text-center">
            <p className="text-gray-600">No players yet. Add your first player to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg bg-white shadow">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Date of Birth</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Birth Year (BE)</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Eligibility</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Note</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {players.map((player) => (
                  <tr key={player.id} className="border-b hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{player.fullName}</p>
                      <p className="text-sm text-gray-600">
                        {player.firstName} {player.lastName}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {player.dateOfBirth ? new Date(player.dateOfBirth).toLocaleDateString("th-TH") : "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {player.birthYearBE || "-"}
                    </td>
                    <td className="px-6 py-4">
                      <EligibilityBadge status={player.eligibilityStatus} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 max-w-xs">
                      {player.eligibilityNote || "-"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDeletePlayer(player.id)}
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
