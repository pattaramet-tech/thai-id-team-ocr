"use client";

import { useState } from "react";

interface OCRPreview {
  sourceFilename: string;
  ocrText: string;
  firstName: string | null;
  lastName: string | null;
  fullName: string | null;
  dateOfBirth: string | null;
  birthYearBE: number | null;
  confidence: number;
  eligibilityStatus: "eligible" | "over_age" | "unknown";
  eligibilityNote: string | null;
  warnings: string[];
}

interface OCRPreviewProps {
  teamId: number;
  teamAgeGroup: string;
  onSave: (data: {
    firstName: string;
    lastName: string;
    dateOfBirth: string | null;
    sourceFilename: string;
    ocrText: string;
    confidence: number;
  }) => Promise<void>;
  onCancel: () => void;
}

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

export function OCRPreview({
  teamId,
  teamAgeGroup,
  onSave,
  onCancel,
}: OCRPreviewProps) {
  const [preview, setPreview] = useState<OCRPreview | null>(null);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showOCRText, setShowOCRText] = useState(false);

  // Edit state
  const [editedFirstName, setEditedFirstName] = useState<string>("");
  const [editedLastName, setEditedLastName] = useState<string>("");
  const [editedDOB, setEditedDOB] = useState<string>("");

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append("team_id", teamId.toString());
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/ocr/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "OCR failed");
      }

      const data: OCRPreview = await response.json();
      setPreview(data);

      // Initialize edit state with OCR results
      setEditedFirstName(data.firstName || "");
      setEditedLastName(data.lastName || "");
      setEditedDOB(data.dateOfBirth || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    if (!editedFirstName.trim() || !editedLastName.trim()) {
      setError("ชื่อและนามสกุลไม่ว่าง");
      return;
    }

    if (preview?.eligibilityStatus === "over_age") {
      if (!confirm("นักกีฬาอายุเกินรุ่น ต้องการบันทึกต่อหรือไม่?")) {
        return;
      }
    }

    try {
      setSaving(true);
      await onSave({
        firstName: editedFirstName,
        lastName: editedLastName,
        dateOfBirth: editedDOB || null,
        sourceFilename: preview?.sourceFilename || "",
        ocrText: preview?.ocrText || "",
        confidence: preview?.confidence || 0,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "บันทึกล้มเหลว");
    } finally {
      setSaving(false);
    }
  };

  if (!preview) {
    return (
      <div className="rounded-lg bg-white p-6 shadow">
        <h3 className="mb-4 text-lg font-semibold">อัปโหลดสำเนาบัตรประชาชน</h3>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              เลือกไฟล์ (JPG/PNG)
            </label>
            <input
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleFileSelect}
              disabled={uploading}
              className="w-full rounded border border-gray-300 px-3 py-2 disabled:bg-gray-100"
            />
          </div>

          {uploading && <p className="text-sm text-gray-600">กำลังประมวลผล OCR...</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-lg bg-white p-6 shadow">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">ตรวจสอบผลลัพธ์ OCR</h3>
        <p className="text-sm text-gray-600">{preview.sourceFilename}</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {preview.warnings.length > 0 && (
        <div className="rounded-lg bg-yellow-50 p-4">
          <p className="text-sm font-semibold text-yellow-900 mb-2">คำเตือน:</p>
          <ul className="text-sm text-yellow-800 space-y-1">
            {preview.warnings.map((w, i) => (
              <li key={i}>• {w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* OCR Data Display */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ชื่อจริง
          </label>
          <input
            type="text"
            value={editedFirstName}
            onChange={(e) => setEditedFirstName(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            นามสกุล
          </label>
          <input
            type="text"
            value={editedLastName}
            onChange={(e) => setEditedLastName(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            วันเกิด
          </label>
          <input
            type="date"
            value={editedDOB}
            onChange={(e) => setEditedDOB(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ปีเกิด (พ.ศ.)
          </label>
          <input
            type="text"
            value={preview.birthYearBE || "-"}
            disabled
            className="w-full rounded border border-gray-300 bg-gray-50 px-3 py-2"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            สถานะการลงเข้าร่วม
          </label>
          <div className="pt-2">
            <EligibilityBadge status={preview.eligibilityStatus} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ความแม่นยำ
          </label>
          <div className="flex items-center pt-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  preview.confidence > 0.8
                    ? "bg-green-500"
                    : preview.confidence > 0.6
                      ? "bg-yellow-500"
                      : "bg-red-500"
                }`}
                style={{ width: `${preview.confidence * 100}%` }}
              />
            </div>
            <span className="ml-2 text-sm text-gray-600">
              {(preview.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {preview.eligibilityNote && (
        <div className="rounded-lg bg-blue-50 p-4">
          <p className="text-sm text-blue-900">{preview.eligibilityNote}</p>
        </div>
      )}

      {/* OCR Text Accordion */}
      <details className="border border-gray-200 rounded-lg">
        <summary className="cursor-pointer p-4 font-medium text-gray-700 hover:bg-gray-50">
          ดูข้อความ OCR แบบเต็ม
        </summary>
        <div className="border-t p-4 bg-gray-50">
          <pre className="whitespace-pre-wrap break-words font-mono text-xs text-gray-700 max-h-48 overflow-y-auto">
            {preview.ocrText}
          </pre>
        </div>
      </details>

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end pt-4 border-t">
        <button
          onClick={onCancel}
          disabled={saving}
          className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:bg-gray-100"
        >
          ยกเลิก
        </button>

        <button
          onClick={() => {
            setPreview(null);
            setError(null);
          }}
          disabled={saving}
          className="rounded-lg border border-blue-300 px-4 py-2 text-blue-700 hover:bg-blue-50 disabled:bg-gray-100"
        >
          อัปโหลดใหม่
        </button>

        <button
          onClick={handleSave}
          disabled={saving || !editedFirstName.trim() || !editedLastName.trim()}
          className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700 disabled:bg-gray-400"
        >
          {saving ? "กำลังบันทึก..." : "บันทึกเข้ารายชื่อทีม"}
        </button>
      </div>
    </div>
  );
}
