"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import StatusBadge from "@/components/StatusBadge";

interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

interface SystemHealth {
  version: string;
  database: { status: string; message?: string };
  directories: Record<
    string,
    {
      status: string;
      writable: boolean;
      path: string;
      error?: string;
    }
  >;
  tesseract: { status: string; version?: string; message?: string };
  thai_language: { status: string; language?: string; message?: string };
  poppler: { status: string; message?: string };
  statistics: {
    teams: number;
    players: number;
    audit_logs: number;
  };
  disk_usage: {
    uploads_bytes: number;
    uploads_mb: number;
    exports_bytes: number;
    exports_mb: number;
    temp_bytes: number;
    temp_mb: number;
  };
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminSystemPage() {
  const [user, setUser] = useState<User | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user && user.role === "admin") {
      fetchSystemHealth();
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

  const fetchSystemHealth = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_BASE}/system/health`, {
        headers: { Authorization: `Bearer ${token || ""}` },
      });

      if (!res.ok) throw new Error("Failed to fetch system health");
      const data = await res.json();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load system health");
    } finally {
      setLoading(false);
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
          <h1 className="text-3xl font-bold text-gray-900">สถานะระบบ</h1>
          <p className="text-gray-600 mt-2">
            ตรวจสอบสถานะการทำงานของระบบและส่วนประกอบที่จำเป็น
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
            <button
              onClick={fetchSystemHealth}
              className="mt-2 text-red-600 hover:text-red-700 underline"
            >
              ลองใหม่
            </button>
          </div>
        )}

        {loading ? (
          <div className="text-center py-8">
            <div className="text-gray-600">กำลังโหลด...</div>
          </div>
        ) : health ? (
          <div className="space-y-6">
            {/* App Version */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                เวอร์ชันระบบ
              </h2>
              <div className="text-2xl font-bold text-blue-600">
                v{health.version}
              </div>
            </div>

            {/* Database Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                ฐานข้อมูล
              </h2>
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-gray-700">สถานะ: {health.database.message}</p>
                </div>
                <StatusBadge
                  status={
                    health.database.status as
                      | "healthy"
                      | "unhealthy"
                  }
                />
              </div>
            </div>

            {/* Directories */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                ไดเรกทอรี่
              </h2>
              <div className="space-y-3">
                {Object.entries(health.directories).map(([name, dir]) => (
                  <div
                    key={name}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {name} ({dir.path})
                      </p>
                      {!dir.writable && (
                        <p className="text-sm text-red-600">
                          {dir.error || "ไม่สามารถเขียนไฟล์ได้"}
                        </p>
                      )}
                    </div>
                    <StatusBadge
                      status={
                        dir.writable ? ("ok" as const) : ("error" as const)
                      }
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* OCR Dependencies */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                ส่วนประกอบ OCR
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Tesseract OCR</p>
                    {health.tesseract.version && (
                      <p className="text-sm text-gray-600">
                        {health.tesseract.version}
                      </p>
                    )}
                    {health.tesseract.message && (
                      <p className="text-sm text-gray-600">
                        {health.tesseract.message}
                      </p>
                    )}
                  </div>
                  <StatusBadge
                    status={
                      health.tesseract.status as
                        | "installed"
                        | "not_found"
                    }
                  />
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Thai Language Data</p>
                    {health.thai_language.message && (
                      <p className="text-sm text-gray-600">
                        {health.thai_language.message}
                      </p>
                    )}
                  </div>
                  <StatusBadge
                    status={
                      health.thai_language.status as
                        | "available"
                        | "missing"
                        | "unknown"
                    }
                  />
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Poppler (PDF Support)</p>
                    {health.poppler.message && (
                      <p className="text-sm text-gray-600">
                        {health.poppler.message}
                      </p>
                    )}
                  </div>
                  <StatusBadge
                    status={
                      health.poppler.status as
                        | "available"
                        | "not_found"
                    }
                  />
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                สถิติ
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded">
                  <p className="text-2xl font-bold text-blue-600">
                    {health.statistics.teams}
                  </p>
                  <p className="text-gray-600">ทีม</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded">
                  <p className="text-2xl font-bold text-blue-600">
                    {health.statistics.players}
                  </p>
                  <p className="text-gray-600">ผู้เล่น</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded">
                  <p className="text-2xl font-bold text-blue-600">
                    {health.statistics.audit_logs}
                  </p>
                  <p className="text-gray-600">บันทึก</p>
                </div>
              </div>
            </div>

            {/* Disk Usage */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                ใช้พื้นที่
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded">
                  <p className="text-gray-700 font-medium">Upload</p>
                  <p className="text-lg font-bold text-gray-900">
                    {health.disk_usage.uploads_mb.toFixed(2)} MB
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded">
                  <p className="text-gray-700 font-medium">Export</p>
                  <p className="text-lg font-bold text-gray-900">
                    {health.disk_usage.exports_mb.toFixed(2)} MB
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded">
                  <p className="text-gray-700 font-medium">Temp</p>
                  <p className="text-lg font-bold text-gray-900">
                    {health.disk_usage.temp_mb.toFixed(2)} MB
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
