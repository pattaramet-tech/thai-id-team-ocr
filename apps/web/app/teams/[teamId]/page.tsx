"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { OCRPreview } from "./ocr-preview";
import { BatchUpload } from "./batch-upload";

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
  status: "pending" | "verified" | "rejected";
  createdAt: string;
  updatedAt: string;
  verifiedAt?: string | null;
}

interface Duplicate {
  [fullName: string]: Array<{ id: number; firstName: string; lastName: string; sourceFilename?: string }>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EligibilityBadge = ({ status }: { status: string }) => {
  const badgeStyles = {
    eligible: "bg-green-100 text-green-800",
    over_age: "bg-red-100 text-red-800",
    unknown: "bg-gray-100 text-gray-800",
  };

  const labels = {
    eligible: "✓ ผ่านเกณฑ์",
    over_age: "✗ อายุเกินรุ่น",
    unknown: "? รอตรวจสอบ",
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badgeStyles[status as keyof typeof badgeStyles]}`}>
      {labels[status as keyof typeof labels]}
    </span>
  );
};

const StatusBadge = ({ status }: { status: string }) => {
  const badgeStyles = {
    pending: "bg-yellow-100 text-yellow-800",
    verified: "bg-green-100 text-green-800",
    rejected: "bg-red-100 text-red-800",
  };

  const labels = {
    pending: "รอตรวจ",
    verified: "ยืนยันแล้ว",
    rejected: "ไม่ผ่าน",
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
  const [showOCR, setShowOCR] = useState<false | "single" | "batch">(false);
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);
  const [duplicates, setDuplicates] = useState<Duplicate | null>(null);
  const [exporting, setExporting] = useState(false);
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

      // Fetch duplicates
      const dupRes = await fetch(`${API_BASE}/export/team/${teamId}/duplicates`);
      if (dupRes.ok) {
        const dupData = await dupRes.json();
        setDuplicates(dupData.duplicates || {});
      }

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

  const handleSaveFromOCR = async (data: {
    firstName: string;
    lastName: string;
    dateOfBirth: string | null;
    sourceFilename: string;
    ocrText: string;
    confidence: number;
  }) => {
    try {
      const res = await fetch(`${API_BASE}/players`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          teamId,
          firstName: data.firstName,
          lastName: data.lastName,
          dateOfBirth: data.dateOfBirth || undefined,
          sourceFilename: data.sourceFilename,
          ocrText: data.ocrText,
          confidence: data.confidence,
        }),
      });

      if (!res.ok) throw new Error("Failed to save player");
      setShowOCR(false);
      await fetchTeamAndPlayers();
    } catch (err) {
      throw err;
    }
  };

  const handleEditPlayer = (player: Player) => {
    setEditingPlayer({
      ...player,
      dateOfBirth: player.dateOfBirth || "",
    });
  };

  const handleSaveEdit = async () => {
    if (!editingPlayer) return;
    if (!editingPlayer.firstName.trim() || !editingPlayer.lastName.trim()) {
      setError("ชื่อและนามสกุลไม่ว่าง");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/players/${editingPlayer.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firstName: editingPlayer.firstName,
          lastName: editingPlayer.lastName,
          dateOfBirth: editingPlayer.dateOfBirth || null,
        }),
      });

      if (!res.ok) throw new Error("Failed to update player");
      setEditingPlayer(null);
      await fetchTeamAndPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update player");
    }
  };

  const handleVerifyPlayer = async (playerId: number) => {
    try {
      const res = await fetch(`${API_BASE}/players/${playerId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "verified" }),
      });

      if (!res.ok) throw new Error("Failed to verify player");
      await fetchTeamAndPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to verify player");
    }
  };

  const handleRejectPlayer = async (playerId: number) => {
    try {
      const res = await fetch(`${API_BASE}/players/${playerId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "rejected" }),
      });

      if (!res.ok) throw new Error("Failed to reject player");
      await fetchTeamAndPlayers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reject player");
    }
  };

  const handleExportTeam = async () => {
    try {
      setExporting(true);
      const res = await fetch(`${API_BASE}/export/team/${teamId}`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Export failed");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${team?.name || "team"}_verified_players.xlsx`;
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

  const handleExportAllTeams = async () => {
    try {
      setExporting(true);
      const res = await fetch(`${API_BASE}/export/all`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Export failed");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "all_teams_verified_players.xlsx";
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
              <p className="text-sm text-gray-600">ปีแข่งขัน (พ.ศ.)</p>
              <p className="text-2xl font-bold text-gray-900">{team.competitionYearBE}</p>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 text-center mb-6">
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-600">รวมนักกีฬา</p>
              <p className="text-2xl font-bold">{players.length}</p>
            </div>
            <div className="rounded-lg bg-green-50 p-4">
              <p className="text-sm text-green-700">ผ่านเกณฑ์</p>
              <p className="text-2xl font-bold text-green-900">{eligibleCount}</p>
            </div>
            <div className="rounded-lg bg-red-50 p-4">
              <p className="text-sm text-red-700">อายุเกินรุ่น</p>
              <p className="text-2xl font-bold text-red-900">{overAgeCount}</p>
            </div>
            <div className="rounded-lg bg-blue-50 p-4">
              <p className="text-sm text-blue-700">ยืนยันแล้ว</p>
              <p className="text-2xl font-bold text-blue-900">{players.filter((p) => p.status === "verified").length}</p>
            </div>
          </div>

          {/* Export Buttons */}
          <div className="flex gap-2 justify-end">
            <button
              onClick={handleExportTeam}
              disabled={exporting || players.filter((p) => p.status === "verified").length === 0}
              className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:bg-gray-400"
            >
              {exporting ? "กำลังส่งออก..." : "📥 ส่งออก XLSX"}
            </button>
            <button
              onClick={handleExportAllTeams}
              disabled={exporting}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
            >
              {exporting ? "กำลังส่งออก..." : "📥 ส่งออกทั้งหมด"}
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Duplicate Warning */}
        {duplicates && Object.keys(duplicates).length > 0 && (
          <div className="mb-4 rounded-lg bg-amber-50 border border-amber-200 p-4">
            <p className="text-sm font-semibold text-amber-900 mb-2">⚠️ พบรายชื่อซ้ำในทีม</p>
            <ul className="text-sm text-amber-800 space-y-1">
              {Object.entries(duplicates).map(([name, players]) => (
                <li key={name}>
                  <strong>{name}</strong> - {players.length} คน
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Add Player Form */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => setShowForm(!showForm)}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              {showForm ? "ยกเลิก" : "+ เพิ่มนักกีฬา"}
            </button>
            <button
              onClick={() => setShowOCR(showOCR === "single" ? false : "single")}
              className="rounded-lg bg-purple-600 px-4 py-2 text-white hover:bg-purple-700"
            >
              {showOCR === "single" ? "ปิด" : "📤 อัปโหลดไฟล์เดี่ยว"}
            </button>
            <button
              onClick={() => setShowOCR(showOCR === "batch" ? false : "batch")}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
            >
              {showOCR === "batch" ? "ปิด" : "📥 อัปโหลดหลายไฟล์"}
            </button>
          </div>

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

          {showOCR === "single" && team && (
            <OCRPreview
              teamId={teamId}
              teamAgeGroup={team.ageGroup}
              onSave={handleSaveFromOCR}
              onCancel={() => setShowOCR(false)}
            />
          )}

          {showOCR === "batch" && (
            <BatchUpload
              teamId={teamId}
              onItemsSaved={fetchTeamAndPlayers}
            />
          )}
        </div>

        {/* Players List */}
        {players.length === 0 ? (
          <div className="rounded-lg bg-blue-50 p-6 text-center">
            <p className="text-gray-600">ยังไม่มีนักกีฬา เพิ่มนักกีฬาคนแรกของคุณเพื่อเริ่มต้น</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg bg-white shadow">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold">ชื่อ-นามสกุล</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">วันเกิด</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">ปีเกิด (พ.ศ.)</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">สถานะอายุ</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">สถานะ</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold">ดำเนินการ</th>
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
                    <td className="px-6 py-4">
                      <StatusBadge status={player.status} />
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => handleEditPlayer(player)}
                        className="text-blue-600 hover:text-blue-900 text-sm"
                      >
                        แก้ไข
                      </button>
                      {player.status === "pending" && (
                        <>
                          <button
                            onClick={() => handleVerifyPlayer(player.id)}
                            className="text-green-600 hover:text-green-900 text-sm"
                          >
                            ยืนยัน
                          </button>
                          <button
                            onClick={() => handleRejectPlayer(player.id)}
                            className="text-orange-600 hover:text-orange-900 text-sm"
                          >
                            ไม่ผ่าน
                          </button>
                        </>
                      )}
                      {player.status === "verified" && (
                        <button
                          onClick={() => handleRejectPlayer(player.id)}
                          className="text-orange-600 hover:text-orange-900 text-sm"
                        >
                          ยกเลิก
                        </button>
                      )}
                      {player.status === "rejected" && (
                        <button
                          onClick={() => handleVerifyPlayer(player.id)}
                          className="text-green-600 hover:text-green-900 text-sm"
                        >
                          อนุมัติ
                        </button>
                      )}
                      <button
                        onClick={() => handleDeletePlayer(player.id)}
                        className="text-red-600 hover:text-red-900 text-sm"
                      >
                        ลบ
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Edit Player Modal */}
        {editingPlayer && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-lg">
              <h2 className="text-xl font-bold mb-4">แก้ไขนักกีฬา</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ชื่อจริง *
                  </label>
                  <input
                    type="text"
                    value={editingPlayer.firstName}
                    onChange={(e) => setEditingPlayer({ ...editingPlayer, firstName: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    นามสกุล *
                  </label>
                  <input
                    type="text"
                    value={editingPlayer.lastName}
                    onChange={(e) => setEditingPlayer({ ...editingPlayer, lastName: e.target.value })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    วันเกิด
                  </label>
                  <input
                    type="date"
                    value={editingPlayer.dateOfBirth || ""}
                    onChange={(e) => setEditingPlayer({ ...editingPlayer, dateOfBirth: e.target.value || null })}
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
              </div>

              <div className="flex gap-2 justify-end mt-6">
                <button
                  onClick={() => setEditingPlayer(null)}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
                >
                  ยกเลิก
                </button>
                <button
                  onClick={handleSaveEdit}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                >
                  บันทึก
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
