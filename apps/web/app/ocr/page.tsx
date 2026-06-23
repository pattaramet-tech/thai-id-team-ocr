"use client";

import { useState, useEffect } from "react";
import { api, type Team } from "@/lib/api";

interface UploadResult {
  id: number;
  firstName: string | null;
  lastName: string | null;
  fullName: string | null;
  confidence: number;
  sourceFilename: string;
}

export default function OCRPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<UploadResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedTeamId || files.length === 0) {
      setError("Please select a team and at least one file");
      return;
    }

    setUploading(true);
    setError(null);
    const uploadedResults: UploadResult[] = [];

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append("team_id", selectedTeamId.toString());
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/ocr/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Upload failed");
        }

        const result = await response.json();
        uploadedResults.push(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      }
    }

    setResults(uploadedResults);
    setFiles([]);
    setUploading(false);

    if (uploadedResults.length > 0) {
      // Auto-select the first team to show results
      await fetchTeams();
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
            No teams available. Please create a team first.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload & OCR</h1>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="rounded-lg bg-white p-6 shadow mb-8">
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
                  {team.name} ({team.ageGroup})
                </option>
              ))}
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Image Files (JPG/PNG)
            </label>
            <input
              type="file"
              multiple
              accept=".jpg,.jpeg,.png"
              onChange={handleFileSelect}
              disabled={uploading}
              className="w-full rounded border border-gray-300 px-3 py-2 disabled:bg-gray-100"
            />
            {files.length > 0 && (
              <p className="mt-2 text-sm text-gray-600">
                {files.length} file(s) selected
              </p>
            )}
          </div>

          <button
            onClick={handleUpload}
            disabled={uploading || !selectedTeamId || files.length === 0}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
          >
            {uploading ? "Uploading..." : "Upload & Process"}
          </button>
        </div>

        {results.length > 0 && (
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              OCR Results ({results.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      File
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      First Name
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Last Name
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <tr key={result.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">
                        {result.sourceFilename}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {result.firstName || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {result.lastName || "-"}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {(result.confidence * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
