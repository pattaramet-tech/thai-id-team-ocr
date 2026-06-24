"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

interface User {
  id: number;
  username: string;
  display_name: string;
  role: string;
}

const LITE_MODE = process.env.NEXT_PUBLIC_LITE_MODE === "true";

export default function Header({ user }: { user?: User | null }) {
  const pathname = usePathname();
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);

  const isActive = (path: string) => pathname === path;

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        await fetch("http://localhost:8000/auth/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
      localStorage.removeItem("token");
      router.push("/");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <nav className="bg-white shadow">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and main nav */}
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Thai ID Team OCR
            </Link>

            <div className="hidden md:flex gap-4">
              <NavLink href="/teams" active={isActive("/teams")}>
                ทีม
              </NavLink>
              <NavLink href="/ocr" active={isActive("/ocr")}>
                Upload & OCR
              </NavLink>
              <NavLink href="/review" active={isActive("/review")}>
                Review
              </NavLink>
              <NavLink href="/export" active={isActive("/export")}>
                Export
              </NavLink>

              {/* Admin menu - only show if user is admin and not in Lite Mode */}
              {user && user.role === "admin" && !LITE_MODE && (
                <>
                  <div className="border-l border-gray-300" />
                  <NavLink
                    href="/admin/system"
                    active={isActive("/admin/system")}
                  >
                    สถานะระบบ
                  </NavLink>
                  <NavLink
                    href="/admin/backup"
                    active={isActive("/admin/backup")}
                  >
                    สำรองข้อมูล
                  </NavLink>
                  <NavLink href="/admin/help" active={isActive("/admin/help")}>
                    คู่มือ
                  </NavLink>
                </>
              )}

              {/* Lite mode simple backup/cleanup */}
              {user && user.role === "admin" && LITE_MODE && (
                <>
                  <div className="border-l border-gray-300" />
                  <NavLink
                    href="/admin/backup"
                    active={isActive("/admin/backup")}
                  >
                    สำรองข้อมูล
                  </NavLink>
                </>
              )}
            </div>
          </div>

          {/* User menu */}
          <div className="flex items-center gap-4 relative">
            {user ? (
              <>
                <div className="text-sm">
                  <div className="font-medium text-gray-900">
                    {user.display_name}
                  </div>
                  <div className="text-gray-500 text-xs">{user.role}</div>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowMenu(!showMenu)}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    ⋮
                  </button>
                  {showMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded shadow-lg z-50">
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <Link href="/auth/login" className="text-blue-600 hover:text-blue-700">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={`px-3 py-2 rounded-md text-sm font-medium transition ${
        active
          ? "bg-blue-600 text-white"
          : "text-gray-700 hover:bg-gray-100"
      }`}
    >
      {children}
    </Link>
  );
}
