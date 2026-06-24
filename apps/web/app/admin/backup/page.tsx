"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import ConfirmModal from "@/components/ConfirmModal";

interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

interface Backup {
  filename: string;
  created_at: string;
  size_bytes: number;
  size_mb: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminBackupPage() {
  const [user, setUser] = useState<User | null>(null);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [includeExports, setIncludeExports] = useState(false);
  const [restoreConfirm, setRestoreConfirm] = useState<{
    isOpen: boolean;
    filename: string;
  }>({ isOpen: false, filename: "" });
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    filename: string;
  }>({ isOpen: false, filename: "" });
  const [restoring, setRestoring] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user && user.role === "admin") {
      fetchBackups();
    }
  }, [user]);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        window.location.href = "/auth/login";
        return;
      }

      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        localStorage.removeItem("token");
        window.location.href = "/auth/login";
        return;
      }

      const userData = await res.json();
      if (userData.role !== "admin") {
        window.location.href = "/";
        return;
      }

      setUser(userData);
    } catch (err) {
      console.error("Auth check failed:", err);
      window.location.href = "/auth/login";
    }
  };

  const fetchBackups = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/backup/list`, {
        headers: { Authorization: `Bearer ${token || ""}` },
      });

      if (!res.ok) throw new Error("Failed to fetch backups");
      const data = await res.json();
      setBackups(data.backups || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load backups");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    setCreating(true);
    try {
      const token = localStorage.getItem("token");
      const url = new URL(`${API_BASE}/backup/create`);
      if (includeExports) {
        url.searchParams.append("include_exports", "true");
      }

      const res = await fetch(url.toString(), {
        method: "POST",
        headers: { Authorization: `Bearer ${token || ""}` },
      });

      if (!res.ok) throw new Error("Failed to create backup");
      setError(null);
      await fetchBackups();
      setIncludeExports(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create backup");
    } finally {
      setCreating(false);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${API_BASE}/backup/download/${encodeURIComponent(filename)}`,
        {
          headers: { Authorization: `Bearer ${token || ""}` },
        }
      );

      if (!res.ok) throw new Error("Failed to download backup");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to download backup"
      );
    }
  };

  const handleRestoreConfirm = async () => {
    setRestoring(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/backup/restore`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({
          filename: restoreConfirm.filename,
          confirm_phrase: "RESTORE_CONFIRM",
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to restore backup");
      }

      setError(null);
      setRestoreConfirm({ isOpen: false, filename: "" });
      alert("ฟื้นฟูข้อมูลเสร็จแล้ว กรุณา Restart Backend");
      await fetchBackups();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to restore backup");
    } finally {
      setRestoring(false);
    }
  };

  const handleDeleteConfirm = async () => {
    setDeleting(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(
        `${API_BASE}/backup/${encodeURIComponent(deleteConfirm.filename)}`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token || ""}` },
        }
      );

      if (!res.ok) throw new Error("Failed to delete backup");

      setError(null);
      setDeleteConfirm({ isOpen: false, filename: "" });
      await fetchBackups();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete backup");
    } finally {
      setDeleting(false);
    }
  };

  if (!user || user.role !== "admin") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600 mb-4">กำลังตรวจสอบสิทธิ์...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">สำรองและฟื้นฟูข้อมูล</h1>
          <p className="text-gray-600 mt-2">
            จัดการสำรองข้อมูลฐานข้อมูลและไฟล์ export
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-red-600 hover:text-red-700 underline"
            >
              ปิด
            </button>
          </div>
        )}

        {/* Create Backup Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            สร้างไฟล์สำรอง
          </h2>

          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="includeExports"
                checked={includeExports}
                onChange={(e) => setIncludeExports(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="includeExports" className="text-gray-700">
                รวมไฟล์ Export XLSX ใน Backup (ค่าเริ่มต้น: ไม่รวม)
              </label>
            </div>

            <button
              onClick={handleCreateBackup}
              disabled={creating}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {creating ? "กำลังสร้าง..." : "สร้างไฟล์สำรอง"}
            </button>
          </div>
        </div>

        {/* Backups List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            ไฟล์สำรองที่มีอยู่
          </h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="text-gray-600">กำลังโหลด...</div>
            </div>
          ) : backups.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">ยังไม่มีไฟล์สำรอง</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      ชื่อไฟล์
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      วันที่สร้าง
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      ขนาด
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                      ตัวเลือก
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {backups.map((backup) => (
                    <tr
                      key={backup.filename}
                      className="border-b border-gray-200 hover:bg-gray-50"
                    >
                      <td className="px-4 py-3 text-sm text-gray-900">
                        {backup.filename}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(backup.created_at).toLocaleString("th-TH")}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {backup.size_mb.toFixed(2)} MB
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() =>
                              handleDownload(backup.filename)
                            }
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
                          >
                            ดาวน์โหลด
                          </button>
                          <button
                            onClick={() =>
                              setRestoreConfirm({
                                isOpen: true,
                                filename: backup.filename,
                              })
                            }
                            className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
                          >
                            ฟื้นฟู
                          </button>
                          <button
                            onClick={() =>
                              setDeleteConfirm({
                                isOpen: true,
                                filename: backup.filename,
                              })
                            }
                            className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
                          >
                            ลบ
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Restore Confirmation Modal */}
      <ConfirmModal
        isOpen={restoreConfirm.isOpen}
        title="⚠️ ฟื้นฟูข้อมูล"
        message={`คุณต้องการฟื้นฟูข้อมูลจากไฟล์ "${restoreConfirm.filename}" หรือไม่? การกระทำนี้จะแทนที่ฐานข้อมูลปัจจุบัน`}
        confirmText="ฟื้นฟู"
        cancelText="ยกเลิก"
        inputRequired="RESTORE_CONFIRM"
        loading={restoring}
        onConfirm={handleRestoreConfirm}
        onCancel={() =>
          setRestoreConfirm({ isOpen: false, filename: "" })
        }
      />

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteConfirm.isOpen}
        title="ลบไฟล์สำรอง"
        message={`คุณต้องการลบไฟล์ "${deleteConfirm.filename}" หรือไม่?`}
        confirmText="ลบ"
        cancelText="ยกเลิก"
        loading={deleting}
        onConfirm={handleDeleteConfirm}
        onCancel={() =>
          setDeleteConfirm({ isOpen: false, filename: "" })
        }
      />
    </div>
  );
}
