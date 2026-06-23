"use client";

import { useState, useEffect } from "react";
import { api, type Team } from "@/lib/api";

interface Player {
  id: number;
  teamId: number;
  firstName: string | null;
  lastName: string | null;
  fullName: string | null;
  sourceFilename: string;
  ocrText: string | null;
  confidence: number;
  status: string;
  createdAt: string;
  verifiedAt: string | null;
}

interface EditingPlayer {
  id: number;
  firstName: string;
  lastName: string;
}

export default function ReviewPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingPlayer, setEditingPlayer] = useState<EditingPlayer | null>(null);
  const [expandedPlayerId, setExpandedPlayerId] = useState<number | null>(null);

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const data = await api.teams.list();
      setTeams(data);
      if (data.length > 0 && !selectedTeamId) {
        setSelectedTeamId(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load teams");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedTeamId) {
      fetchPlayers();
    }
  }, [selectedTeamId]);

  const fetchPlayers = async () => {
    if (!selectedTeamId) return;

    try {
      const response = await fetch(
        `http://localhost:8000/players?team_id=${selectedTeamId}`,
        { method: "GET" }
      );
      if (!response.ok) throw new Error("Failed to fetch players");
      const data = await response.json();
      setPlayers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load players");
    }
  };

  const handleStartEdit = (player: Player) => {
    setEditingPlayer({
      id: player.id,
      firstName: player.firstName || "",
      lastName: player.lastName || "",
    });
  };

  const handleSaveEdit = async (playerId: number) => {
    if (!editingPlayer) return;

    try {
      const response = await fetch(
        `http://localhost:8000/players/${playerId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            firstName: editingPlayer.firstName,
            lastName: editingPlayer.lastName,
            fullName:
              editingPlayer.firstName && editingPlayer.lastName
                ? `${editingPlayer.firstName} ${editingPlayer.lastName}`
                : editingPlayer.firstName,
          }),
        }
      );

      if (!response.ok) throw new Error("Failed to save");
      setEditingPlayer(null);
      await fetchPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    }
  };

  const handleVerify = async (playerId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/players/${playerId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "verified" }),
        }
      );

      if (!response.ok) throw new Error("Failed to verify");
      await fetchPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify");
    }
  };

  const handleReject = async (playerId: number) => {
    try {
      const response = await fetch(
        `http://localhost:8000/players/${playerId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "rejected" }),
        }
      );

      if (!response.ok) throw new Error("Failed to reject");
      await fetchPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject");
    }
  };

  const pendingPlayers = players.filter((p) => p.status === "pending");
  const verifiedPlayers = players.filter((p) => p.status === "verified");
  const rejectedPlayers = players.filter((p) => p.status === "rejected");

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-6xl px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Review Players</h1>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-600">Loading teams...</p>
        ) : teams.length === 0 ? (
          <p className="text-gray-600">No teams available.</p>
        ) : (
          <>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Team
              </label>
              <select
                value={selectedTeamId || ""}
                onChange={(e) => setSelectedTeamId(parseInt(e.target.value))}
                className="rounded border border-gray-300 px-3 py-2"
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.ageGroup})
                  </option>
                ))}
              </select>
            </div>

            {players.length === 0 ? (
              <p className="text-gray-600">No players for this team yet.</p>
            ) : (
              <>
                {pendingPlayers.length > 0 && (
                  <div className="mb-8">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      Pending Review ({pendingPlayers.length})
                    </h2>
                    <div className="space-y-4">
                      {pendingPlayers.map((player) => (
                        <div
                          key={player.id}
                          className="rounded-lg bg-white p-6 shadow border-l-4 border-yellow-400"
                        >
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <p className="text-sm text-gray-600">
                                {player.sourceFilename}
                              </p>
                              <p className="text-sm text-gray-500">
                                Confidence: {(player.confidence * 100).toFixed(1)}%
                              </p>
                            </div>
                            <button
                              onClick={() =>
                                setExpandedPlayerId(
                                  expandedPlayerId === player.id ? null : player.id
                                )
                              }
                              className="text-sm text-blue-600 hover:text-blue-900"
                            >
                              {expandedPlayerId === player.id
                                ? "Hide OCR"
                                : "Show OCR"}
                            </button>
                          </div>

                          {expandedPlayerId === player.id && player.ocrText && (
                            <div className="mb-4 p-4 bg-gray-50 rounded text-sm text-gray-700 max-h-48 overflow-y-auto border border-gray-200">
                              <pre className="whitespace-pre-wrap break-words font-mono text-xs">
                                {player.ocrText}
                              </pre>
                            </div>
                          )}

                          {editingPlayer?.id === player.id ? (
                            <div className="mb-4 grid grid-cols-2 gap-4">
                              <input
                                type="text"
                                value={editingPlayer.firstName}
                                onChange={(e) =>
                                  setEditingPlayer({
                                    ...editingPlayer,
                                    firstName: e.target.value,
                                  })
                                }
                                placeholder="First Name"
                                className="rounded border border-gray-300 px-3 py-2"
                              />
                              <input
                                type="text"
                                value={editingPlayer.lastName}
                                onChange={(e) =>
                                  setEditingPlayer({
                                    ...editingPlayer,
                                    lastName: e.target.value,
                                  })
                                }
                                placeholder="Last Name"
                                className="rounded border border-gray-300 px-3 py-2"
                              />
                            </div>
                          ) : (
                            <div className="mb-4 grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm text-gray-600">First Name</p>
                                <p className="font-semibold">
                                  {player.firstName || "-"}
                                </p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-600">Last Name</p>
                                <p className="font-semibold">
                                  {player.lastName || "-"}
                                </p>
                              </div>
                            </div>
                          )}

                          <div className="flex gap-2">
                            {editingPlayer?.id === player.id ? (
                              <>
                                <button
                                  onClick={() => handleSaveEdit(player.id)}
                                  className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                                >
                                  Save
                                </button>
                                <button
                                  onClick={() => setEditingPlayer(null)}
                                  className="rounded bg-gray-400 px-4 py-2 text-white hover:bg-gray-500"
                                >
                                  Cancel
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleStartEdit(player)}
                                  className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                                >
                                  Edit
                                </button>
                                <button
                                  onClick={() => handleVerify(player.id)}
                                  className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                                >
                                  Verify
                                </button>
                                <button
                                  onClick={() => handleReject(player.id)}
                                  className="rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700"
                                >
                                  Reject
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {verifiedPlayers.length > 0 && (
                  <div className="mb-8">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      Verified ({verifiedPlayers.length})
                    </h2>
                    <div className="space-y-2">
                      {verifiedPlayers.map((player) => (
                        <div
                          key={player.id}
                          className="rounded-lg bg-white p-4 shadow border-l-4 border-green-400"
                        >
                          <p className="font-semibold">
                            {player.fullName || `${player.firstName} ${player.lastName}`}
                          </p>
                          <p className="text-sm text-gray-600">
                            {player.sourceFilename}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {rejectedPlayers.length > 0 && (
                  <div>
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                      Rejected ({rejectedPlayers.length})
                    </h2>
                    <div className="space-y-2">
                      {rejectedPlayers.map((player) => (
                        <div
                          key={player.id}
                          className="rounded-lg bg-white p-4 shadow border-l-4 border-red-400"
                        >
                          <p className="font-semibold">
                            {player.fullName || `${player.firstName} ${player.lastName}`}
                          </p>
                          <p className="text-sm text-gray-600">
                            {player.sourceFilename}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
