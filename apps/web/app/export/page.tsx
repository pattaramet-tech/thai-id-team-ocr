"use client";

import { useState, useEffect } from "react";
import { api, type Team } from "@/lib/api";

interface DuplicateWarning {
  name: string;
  count: number;
  files: string[];
}

export default function ExportPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicates, setDuplicates] = useState<Record<string, number>>({});
  const [verifiedCounts, setVerifiedCounts] = useState<Record<number, number>>({});

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      const data = await api.teams.list();
      setTeams(data);
      if (data.length > 0) {
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
      checkDuplicates();
      fetchVerifiedCount();
    }
  }, [selectedTeamId]);

  const checkDuplicates = async () => {
    if (!selectedTeamId) return;

    try {
      const response = await fetch(
        `http://localhost:8000/export/team/${selectedTeamId}/duplicates`,
        { method: "GET" }
      );
      if (!response.ok) throw new Error("Failed to check duplicates");
      const data = await response.json();

      // Format duplicates
      const duplicateMap: Record<string, number> = {};
      Object.entries(data.duplicates || {}).forEach(([name, group]: [string, any]) => {
        duplicateMap[name] = group.length;
      });
      setDuplicates(duplicateMap);
      setError(null);
    } catch (err) {
      // Silently fail - duplicates check is optional
      console.log("Duplicates check:", err instanceof Error ? err.message : "Unknown error");
    }
  };

  const fetchVerifiedCount = async () => {
    if (!selectedTeamId) return;

    try {
      const response = await fetch(
        `http://localhost:8000/players?team_id=${selectedTeamId}&status=verified`,
        { method: "GET" }
      );
      if (!response.ok) throw new Error("Failed to fetch count");
      const data = await response.json();
      setVerifiedCounts((prev) => ({
        ...prev,
        [selectedTeamId]: data.length,
      }));
    } catch (err) {
      console.log("Count fetch:", err instanceof Error ? err.message : "Unknown error");
    }
  };

  const handleExportTeam = async () => {
    if (!selectedTeamId) {
      setError("Please select a team");
      return;
    }

    setExporting(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/export/team/${selectedTeamId}`,
        { method: "GET" }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Export failed");
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get("content-disposition");
      let filename = "verified_players.xlsx";
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=([^;]+)/);
        if (match) filename = match[1];
      }

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

  const handleExportAll = async () => {
    setExporting(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/export/all", {
        method: "GET",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Export failed");
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get("content-disposition");
      let filename = "all_teams.xlsx";
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=([^;]+)/);
        if (match) filename = match[1];
      }

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <p className="p-8">Loading teams...</p>;
  }

  if (teams.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="mx-auto max-w-4xl px-4">
          <div className="rounded-lg bg-blue-50 p-4 text-blue-700">
            No teams available. Please create a team and verify some players first.
          </div>
        </div>
      </div>
    );
  }

  const selectedTeam = teams.find((t) => t.id === selectedTeamId);
  const verifiedCount = verifiedCounts[selectedTeamId || 0] || 0;
  const hasDuplicates = Object.keys(duplicates).length > 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Export to XLSX</h1>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Single Team Export */}
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Export Single Team
            </h2>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Team
              </label>
              <select
                value={selectedTeamId || ""}
                onChange={(e) => setSelectedTeamId(parseInt(e.target.value))}
                className="w-full rounded border border-gray-300 px-3 py-2"
              >
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.ageGroup}, {team.gender})
                  </option>
                ))}
              </select>
            </div>

            {selectedTeam && (
              <>
                <div className="mb-6 rounded-lg bg-blue-50 p-4">
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Team Info:</strong>
                  </p>
                  <p className="text-sm text-gray-600 mb-1">
                    Name: <strong>{selectedTeam.name}</strong>
                  </p>
                  <p className="text-sm text-gray-600 mb-1">
                    Age Group: <strong>{selectedTeam.ageGroup}</strong>
                  </p>
                  <p className="text-sm text-gray-600 mb-3">
                    Gender: <strong>{selectedTeam.gender}</strong>
                  </p>
                  <p className="text-sm text-gray-600">
                    Verified Players: <strong>{verifiedCount}</strong>
                  </p>
                </div>

                {hasDuplicates && (
                  <div className="mb-6 rounded-lg bg-yellow-50 p-4 border-l-4 border-yellow-400">
                    <p className="text-sm font-semibold text-yellow-900 mb-2">
                      ⚠️ Duplicate Names Found
                    </p>
                    <ul className="text-sm text-yellow-800">
                      {Object.entries(duplicates).map(([name, count]) => (
                        <li key={name} className="mb-1">
                          "{name}" appears {count} times
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={handleExportTeam}
                  disabled={exporting || verifiedCount === 0}
                  className="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400 transition"
                >
                  {exporting
                    ? "Exporting..."
                    : verifiedCount === 0
                      ? "No Verified Players"
                      : `Download XLSX (${verifiedCount} players)`}
                </button>
              </>
            )}
          </div>

          {/* All Teams Export */}
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Export All Teams
            </h2>

            <div className="mb-6">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Summary:</strong>
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                {teams.map((team) => {
                  const count = verifiedCounts[team.id] || 0;
                  return (
                    <li key={team.id}>
                      {team.name}: {count} verified player{count !== 1 ? "s" : ""}
                    </li>
                  );
                })}
              </ul>
            </div>

            <div className="mb-6 rounded-lg bg-green-50 p-4">
              <p className="text-sm text-green-900">
                Creates one Excel file with separate sheets for each team.
              </p>
            </div>

            <button
              onClick={handleExportAll}
              disabled={exporting || Object.values(verifiedCounts).every((c) => c === 0)}
              className="w-full rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:bg-gray-400 transition"
            >
              {exporting
                ? "Exporting..."
                : Object.values(verifiedCounts).every((c) => c === 0)
                  ? "No Verified Players"
                  : "Download All Teams XLSX"}
            </button>
          </div>
        </div>

        {/* Export Format Info */}
        <div className="mt-8 rounded-lg bg-white p-6 shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Format</h3>
          <p className="text-sm text-gray-700 mb-4">
            The exported Excel file includes the following columns:
          </p>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <li>• <strong>No</strong> - Row number</li>
            <li>• <strong>Team</strong> - Team name</li>
            <li>• <strong>Age Group</strong> - Team age group</li>
            <li>• <strong>Gender</strong> - Team gender category</li>
            <li>• <strong>First Name</strong> - Extracted first name</li>
            <li>• <strong>Last Name</strong> - Extracted last name</li>
            <li>• <strong>Full Name</strong> - Complete name</li>
            <li>• <strong>Source File</strong> - Original image filename</li>
            <li>• <strong>Verified Date</strong> - Date of verification</li>
          </ul>
          <p className="text-xs text-gray-500 mt-4">
            Only verified players are included in the export. Headers are frozen for easy scrolling.
          </p>
        </div>
      </div>
    </div>
  );
}
