"use client";

import { useState } from "react";

// Candidate type matching backend structure
interface FieldCandidate {
  fieldName: string;
  value: string | { first: string; last: string } | null;
  rawText: string;
  normalizedText: string;
  source: string;
  templateVersion: string;
  roiName: string;
  confidence: number;
  score: number;
  parser: string;
  warnings: string[];
}

interface OCRDebugInfo {
  ocrText: string;
  preprocessingMethod: string;
  psmMode: number;
  confidence: number;
  extractionMode?: string;
  cardDetected?: boolean;
  cardWarped?: boolean;
  cardLikeFallbackUsed?: boolean;
  roiPresetUsed?: string;
  roiResults?: Record<string, any>;
  fieldCandidates?: Record<string, FieldCandidate[]>;
  selectedCandidates?: Record<string, FieldCandidate>;
  reviewReasons?: string[];
}

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
  // New structured OCR fields
  extraction_mode?: string;
  roi_preset?: string | null;
  card_detected?: boolean;
  card_warped?: boolean;
  card_like_fallback_used?: boolean;
  field_candidates?: Record<string, FieldCandidate[]>;
  selected_candidates?: Record<string, FieldCandidate>;
  review_reasons?: string[];
  debugInfo?: OCRDebugInfo;
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
  const [activeTab, setActiveTab] = useState<"structured" | "candidates" | "confidence" | "debug" | "raw">("structured");

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

  // Translate review reason to Thai
  const translateReviewReason = (reason: string): string => {
    const translations: Record<string, string> = {
      MISSING_FIRST_NAME: "ไม่พบชื่อจริง",
      MISSING_LAST_NAME: "ไม่พบนามสกุล",
      MISSING_DATE_OF_BIRTH: "ไม่พบวันเกิด",
      LOW_OCR_CONFIDENCE: "ความมั่นใจต่ำ",
      FULL_OCR_FALLBACK_ONLY: "ใช้ OCR แบบเดิมเท่านั้น",
    };
    return translations[reason] || reason;
  };

  // Handle candidate selection
  const selectCandidate = (candidate: FieldCandidate) => {
    if (candidate.fieldName === "thai_full_name" && typeof candidate.value === "object" && candidate.value) {
      setEditedFirstName(candidate.value.first);
      setEditedLastName(candidate.value.last);
    } else if (candidate.fieldName === "english_first_name" && typeof candidate.value === "string") {
      setEditedFirstName(candidate.value);
    } else if (candidate.fieldName === "english_last_name" && typeof candidate.value === "string") {
      setEditedLastName(candidate.value);
    } else if ((candidate.fieldName === "dob_english" || candidate.fieldName === "dob_thai") && typeof candidate.value === "string") {
      setEditedDOB(candidate.value);
    }
    setActiveTab("structured");
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
      <div className="flex items-center justify-between mb-6">
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

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex gap-4">
          {(["structured", "candidates", "confidence", "debug", "raw"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab === "structured" && "ผลลัพธ์"}
              {tab === "candidates" && "ตัวเลือก"}
              {tab === "confidence" && "สถิติ"}
              {tab === "debug" && "Debug"}
              {tab === "raw" && "ข้อความ OCR"}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="py-4">
        {/* Structured Tab */}
        {activeTab === "structured" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ชื่อจริง
                </label>
                <input
                  type="text"
                  value={editedFirstName}
                  onChange={(e) => setEditedFirstName(e.target.value)}
                  placeholder="กรอกชื่อจริง"
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
                  placeholder="กรอกนามสกุล"
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

            {(() => {
              const fieldCandidates = preview.field_candidates || preview.debugInfo?.fieldCandidates;
              return fieldCandidates && Object.keys(fieldCandidates).length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900 mb-2">
                    💡 ใช้ tab "ตัวเลือก" เพื่อเลือก candidate อื่นหากผลลัพธ์ไม่ถูกต้อง
                  </p>
                </div>
              );
            })()}
          </div>
        )}

        {/* Candidates Tab */}
        {activeTab === "candidates" && (
          <div className="space-y-6">
            {(() => {
              const fieldCandidates = preview.field_candidates || preview.debugInfo?.fieldCandidates;
              return fieldCandidates ? (
                Object.entries(fieldCandidates).map(([fieldName, candidates]) => {
                  if (candidates.length === 0) return null;
                  return (
                    <div key={fieldName} className="border rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3">{fieldName}</h4>
                      <div className="space-y-2">
                        {candidates.map((candidate, idx) => (
                          <div key={idx} className="bg-gray-50 p-3 rounded border border-gray-200">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex-1">
                                <p className="font-medium text-gray-900">
                                  {typeof candidate.value === "object" && candidate.value
                                    ? `${candidate.value.first} ${candidate.value.last}`
                                    : candidate.value || "(ว่าง)"}
                                </p>
                                <p className="text-xs text-gray-600 mt-1">
                                  Raw: {candidate.rawText.substring(0, 50)}...
                                </p>
                                <div className="flex gap-4 mt-2 text-xs text-gray-600">
                                  <span>V: {candidate.templateVersion}</span>
                                  <span>Score: {candidate.score.toFixed(1)}</span>
                                  <span>Conf: {(candidate.confidence * 100).toFixed(0)}%</span>
                                </div>
                              </div>
                              <button
                                onClick={() => selectCandidate(candidate)}
                                className="ml-2 rounded bg-blue-500 px-3 py-1 text-sm text-white hover:bg-blue-600"
                              >
                                ใช้
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-gray-600">ไม่มี candidates สำหรับการเลือก</p>
              );
            })()}
          </div>
        )}

        {/* Confidence Tab */}
        {activeTab === "confidence" && (
          <div className="space-y-4">
            {(() => {
              // Support both top-level fields and debugInfo fallback
              const extractionMode = preview.extraction_mode || preview.debugInfo?.extractionMode || "N/A";
              const roiPreset = preview.roi_preset || preview.debugInfo?.roiPresetUsed || "N/A";
              const cardDetected = preview.card_detected !== undefined ? preview.card_detected : preview.debugInfo?.cardDetected ?? false;
              const cardWarped = preview.card_warped !== undefined ? preview.card_warped : preview.debugInfo?.cardWarped ?? false;
              const cardLikeFallbackUsed = preview.card_like_fallback_used !== undefined ? preview.card_like_fallback_used : preview.debugInfo?.cardLikeFallbackUsed ?? false;
              const reviewReasons = preview.review_reasons || preview.debugInfo?.reviewReasons || [];

              return (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">Extraction Mode</p>
                      <p className="font-semibold text-gray-900">{extractionMode}</p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">ROI Preset</p>
                      <p className="font-semibold text-gray-900">{roiPreset}</p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">Card Detected</p>
                      <p className="font-semibold text-gray-900">{cardDetected ? "✓ ใช่" : "✗ ไม่"}</p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">Card Warped</p>
                      <p className="font-semibold text-gray-900">{cardWarped ? "✓ ใช่" : "✗ ไม่"}</p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">Card-like Fallback</p>
                      <p className="font-semibold text-gray-900">{cardLikeFallbackUsed ? "✓ ใช่" : "✗ ไม่"}</p>
                    </div>

                    <div className="bg-gray-50 p-4 rounded">
                      <p className="text-sm text-gray-600">OCR Confidence</p>
                      <p className="font-semibold text-gray-900">{(preview.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>

                  {reviewReasons.length > 0 && (
                    <div className="rounded-lg bg-orange-50 p-4 border border-orange-200">
                      <p className="text-sm font-semibold text-orange-900 mb-2">ต้องตรวจสอบ:</p>
                      <ul className="text-sm text-orange-800 space-y-1">
                        {reviewReasons.map((reason, i) => (
                          <li key={i}>• {translateReviewReason(reason)}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        )}

        {/* Debug Tab */}
        {activeTab === "debug" && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const debugText = [
                    `Extraction Mode: ${preview.extraction_mode}`,
                    `ROI Preset: ${preview.roi_preset}`,
                    `Card Detected: ${preview.card_detected}`,
                    `Card-like Fallback: ${preview.card_like_fallback_used}`,
                    `Confidence: ${(preview.confidence * 100).toFixed(0)}%`,
                  ].join("\n");
                  navigator.clipboard.writeText(debugText);
                }}
                className="rounded bg-gray-500 px-4 py-2 text-sm text-white hover:bg-gray-600"
              >
                Copy Debug Info
              </button>
            </div>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-wrap font-mono text-xs text-gray-700 max-h-64 overflow-y-auto">
                {JSON.stringify(
                  {
                    extraction_mode: preview.extraction_mode,
                    roi_preset: preview.roi_preset,
                    card_detected: preview.card_detected,
                    card_like_fallback_used: preview.card_like_fallback_used,
                    confidence: preview.confidence,
                    review_reasons: preview.review_reasons,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        )}

        {/* Raw Text Tab */}
        {activeTab === "raw" && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-600 mb-2">OCR Output (ID numbers redacted):</p>
            <pre className="whitespace-pre-wrap text-wrap font-mono text-xs text-gray-700 max-h-64 overflow-y-auto">
              {preview.ocrText}
            </pre>
          </div>
        )}
      </div>

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
