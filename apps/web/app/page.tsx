"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";

interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

export default function Home() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        return;
      }

      const res = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
      }
    } catch (err) {
      console.error("Auth check failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            OCR Management Dashboard
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Extract Thai names from ID cards and application documents
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <a
              href="/teams"
              className="block rounded-lg bg-blue-600 p-6 text-white hover:bg-blue-700 transition"
            >
              <h3 className="text-xl font-semibold mb-2">Teams</h3>
              <p>Create and manage competition teams</p>
            </a>

            <a
              href="/ocr"
              className="block rounded-lg bg-blue-600 p-6 text-white hover:bg-blue-700 transition"
            >
              <h3 className="text-xl font-semibold mb-2">Upload & OCR</h3>
              <p>Upload images and extract names automatically</p>
            </a>

            <a
              href="/review"
              className="block rounded-lg bg-blue-600 p-6 text-white hover:bg-blue-700 transition"
            >
              <h3 className="text-xl font-semibold mb-2">Review Players</h3>
              <p>Review and verify extracted names</p>
            </a>

            <a
              href="/export"
              className="block rounded-lg bg-blue-600 p-6 text-white hover:bg-blue-700 transition"
            >
              <h3 className="text-xl font-semibold mb-2">Export XLSX</h3>
              <p>Export verified players to Excel</p>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
