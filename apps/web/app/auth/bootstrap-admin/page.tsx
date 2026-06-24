"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function BootstrapAdminPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [canCreate, setCanCreate] = useState(true);

  useEffect(() => {
    checkCanCreate();
  }, []);

  const checkCanCreate = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/bootstrap-admin`, {
        method: "OPTIONS",
      });

      // If we get a 405, the endpoint exists but method not allowed (means users exist)
      // If we can create, continue
      setCanCreate(true);
    } catch (err) {
      setCanCreate(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!username.trim() || !password.trim() || !displayName.trim()) {
        throw new Error("ทุกฟิลด์จำเป็นต้องกรอก");
      }

      if (password.length < 8) {
        throw new Error("รหัสผ่านต้องมีความยาว 8 ตัวอักษรขึ้นไป");
      }

      const res = await fetch(`${API_BASE}/auth/bootstrap-admin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          password,
          display_name: displayName,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "ไม่สามารถสร้าง Admin ได้");
      }

      setSuccess(true);
      setTimeout(() => {
        router.push("/auth/login");
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error creating admin");
    } finally {
      setLoading(false);
    }
  };

  if (!canCreate) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg shadow p-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
              Admin ถูกสร้างแล้ว
            </h1>
            <p className="text-gray-600 text-center mb-6">
              ระบบมี Admin อยู่แล้ว ไปที่หน้า Login
            </p>
            <a
              href="/auth/login"
              className="block text-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              เข้าสู่ระบบ
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="text-5xl mb-4">✅</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">สำเร็จแล้ว</h1>
            <p className="text-gray-600 mb-6">
              สร้าง Admin สำเร็จ ไปที่หน้า Login กำลังเปลี่ยนหน้า...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2 text-center">
            Thai ID Team OCR
          </h1>
          <p className="text-gray-600 text-center mb-6">
            สร้าง Admin User (คนแรก)
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Display Name
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="เช่น Admin Thai ID"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password (8 ตัวอักษรขึ้นไป)
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
            >
              {loading ? "กำลังสร้าง..." : "สร้าง Admin"}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              มี Admin แล้ว?{" "}
              <a href="/auth/login" className="text-blue-600 hover:text-blue-700">
                เข้าสู่ระบบ
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
