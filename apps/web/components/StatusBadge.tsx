"use client";

type Status = "ok" | "healthy" | "available" | "installed" | "warning" | "error" | "unhealthy" | "not_found" | "missing" | "unknown";

const statusConfig: Record<Status, { bg: string; text: string; label: string }> = {
  ok: { bg: "bg-green-100", text: "text-green-800", label: "พร้อมใช้งาน" },
  healthy: {
    bg: "bg-green-100",
    text: "text-green-800",
    label: "พร้อมใช้งาน",
  },
  available: {
    bg: "bg-green-100",
    text: "text-green-800",
    label: "พร้อมใช้งาน",
  },
  installed: {
    bg: "bg-green-100",
    text: "text-green-800",
    label: "พร้อมใช้งาน",
  },
  warning: { bg: "bg-yellow-100", text: "text-yellow-800", label: "คำเตือน" },
  error: { bg: "bg-red-100", text: "text-red-800", label: "มีปัญหา" },
  unhealthy: {
    bg: "bg-red-100",
    text: "text-red-800",
    label: "มีปัญหา",
  },
  not_found: { bg: "bg-red-100", text: "text-red-800", label: "ไม่พบ" },
  missing: { bg: "bg-red-100", text: "text-red-800", label: "ไม่พร้อม" },
  unknown: { bg: "bg-gray-100", text: "text-gray-800", label: "ไม่ทราบ" },
};

export default function StatusBadge({ status }: { status: Status }) {
  const config = statusConfig[status] || statusConfig.unknown;
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
}
