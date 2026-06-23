"use client";

import { useState } from "react";

interface OCRBatchItem {
  sourceFilename: string;
  success: boolean;
  error?: string;
  ocrText?: string;
  firstName?: string;
  lastName?: string;
  fullName?: string;
  dateOfBirth?: string;
  birthYearBE?: number;
  confidence?: number;
  eligibilityStatus?: string;
  eligibilityNote?: string;
  warnings?: string[];
}

interface QueueItem extends OCRBatchItem {
  id: string; // temporary id for UI
  editedFirstName: string;
  editedLastName: string;
  editedDOB: string;
}

interface BatchUploadProps {
  teamId: number;
  onItemsSaved?: () => void;
}

const EligibilityBadge = ({ status }: { status?: string }) => {
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

  if (!status) return null;

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badgeStyles[status as keyof typeof badgeStyles]}`}>
      {labels[status as keyof typeof labels]}
    </span>
  );
};

export function BatchUpload({ teamId, onItemsSaved }: BatchUploadProps) {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showOCRText, setShowOCRText] = useState<Set<string>>(new Set());

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (!files || files.length === 0) return;

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append("team_id", teamId.toString());
      for (const file of files) {
        formData.append("files", file);
      }

      const response = await fetch("http://localhost:8000/ocr/batch-upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Batch OCR failed");
      }

      const batchResult = await response.json();

      // Convert to queue items with editable fields
      const newItems: QueueItem[] = batchResult.items.map(
        (item: OCRBatchItem, idx: number) => ({
          ...item,
          id: `${Date.now()}_${idx}`,
          editedFirstName: item.firstName || "",
          editedLastName: item.lastName || "",
          editedDOB: item.dateOfBirth || "",
        })
      );

      setQueue((prev) => [...prev, ...newItems]);
      e.currentTarget.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveItem = (id: string) => {
    setQueue((prev) => prev.filter((item) => item.id !== id));
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  };

  const handleSelectItem = (id: string) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.delete(id);
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedIds.size === queue.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(queue.map((item) => item.id)));
    }
  };

  const handleSaveSelected = async () => {
    const itemsToSave = queue.filter((item) => selectedIds.has(item.id));

    // Validate
    const errors: string[] = [];
    itemsToSave.forEach((item) => {
      if (!item.editedFirstName.trim()) errors.push(`${item.sourceFilename}: ชื่อจริงไม่ว่าง`);
      if (!item.editedLastName.trim()) errors.push(`${item.sourceFilename}: นามสกุลไม่ว่าง`);
    });

    if (errors.length > 0) {
      setError(errors.join("; "));
      return;
    }

    // Check for over_age and confirm
    const overAgeItems = itemsToSave.filter((item) => item.eligibilityStatus === "over_age");
    if (overAgeItems.length > 0) {
      if (!confirm(`${overAgeItems.length} นักกีฬาอายุเกินรุ่น ต้องการบันทึกต่อหรือไม่?`)) {
        return;
      }
    }

    try {
      setSaving(true);
      let successCount = 0;
      let failCount = 0;

      for (const item of itemsToSave) {
        try {
          const res = await fetch("http://localhost:8000/players", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              teamId,
              firstName: item.editedFirstName,
              lastName: item.editedLastName,
              dateOfBirth: item.editedDOB || null,
              sourceFilename: item.sourceFilename,
              ocrText: item.ocrText,
              confidence: item.confidence,
            }),
          });

          if (res.ok) {
            successCount++;
            // Remove from queue
            setQueue((prev) => prev.filter((q) => q.id !== item.id));
            setSelectedIds((prev) => {
              const newSet = new Set(prev);
              newSet.delete(item.id);
              return newSet;
            });
          } else {
            failCount++;
          }
        } catch (err) {
          failCount++;
        }
      }

      setError(null);
      if (onItemsSaved) onItemsSaved();
      alert(`บันทึกสำเร็จ ${successCount} รายการ${failCount > 0 ? `, ล้มเหลว ${failCount}` : ""}`);
    } finally {
      setSaving(false);
    }
  };

  const handleClearQueue = () => {
    if (confirm("ล้างคิว OCR ทั้งหมดหรือไม่?")) {
      setQueue([]);
      setSelectedIds(new Set());
    }
  };

  return (
    <div className="space-y-4">
      {/* File Upload */}
      <div className="rounded-lg bg-white p-6 shadow">
        <h3 className="mb-4 text-lg font-semibold">อัปโหลดหลายไฟล์</h3>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-4 text-red-700 text-sm">{error}</div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              เลือกไฟล์ (JPG/PNG) สูงสุด 30 ไฟล์
            </label>
            <input
              type="file"
              accept="image/jpeg,image/png"
              multiple
              onChange={handleFileSelect}
              disabled={uploading}
              className="w-full rounded border border-gray-300 px-3 py-2 disabled:bg-gray-100"
            />
          </div>

          {uploading && <p className="text-sm text-gray-600">กำลังประมวลผล OCR...</p>}

          {queue.length > 0 && (
            <p className="text-sm text-gray-600">
              {queue.length} ไฟล์ในคิว ({queue.filter((item) => item.success).length} สำเร็จ,{" "}
              {queue.filter((item) => !item.success).length} ล้มเหลว)
            </p>
          )}
        </div>
      </div>

      {/* Review Queue */}
      {queue.length > 0 && (
        <div className="rounded-lg bg-white p-6 shadow">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Review Queue</h3>
            <button
              onClick={handleClearQueue}
              className="text-sm text-red-600 hover:text-red-900"
            >
              ล้างคิว
            </button>
          </div>

          {/* Queue Table */}
          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === queue.length && queue.length > 0}
                      onChange={handleSelectAll}
                      className="rounded"
                    />
                  </th>
                  <th className="px-4 py-2 text-left">ไฟล์</th>
                  <th className="px-4 py-2 text-left">ชื่อจริง</th>
                  <th className="px-4 py-2 text-left">นามสกุล</th>
                  <th className="px-4 py-2 text-left">วันเกิด</th>
                  <th className="px-4 py-2 text-left">ปีเกิด (พ.ศ.)</th>
                  <th className="px-4 py-2 text-left">สถานะอายุ</th>
                  <th className="px-4 py-2 text-left">ความแม่นยำ</th>
                  <th className="px-4 py-2 text-right">ดำเนินการ</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-2">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(item.id)}
                        onChange={() => handleSelectItem(item.id)}
                        disabled={!item.success}
                        className="rounded disabled:bg-gray-100"
                      />
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <div className="font-medium">{item.sourceFilename}</div>
                      {item.error && <div className="text-red-600 text-xs">{item.error}</div>}
                    </td>
                    <td className="px-4 py-2">
                      {item.success ? (
                        <input
                          type="text"
                          value={item.editedFirstName}
                          onChange={(e) => {
                            setQueue((prev) =>
                              prev.map((q) =>
                                q.id === item.id ? { ...q, editedFirstName: e.target.value } : q
                              )
                            );
                          }}
                          className="w-24 rounded border border-gray-300 px-2 py-1 text-sm"
                        />
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {item.success ? (
                        <input
                          type="text"
                          value={item.editedLastName}
                          onChange={(e) => {
                            setQueue((prev) =>
                              prev.map((q) =>
                                q.id === item.id ? { ...q, editedLastName: e.target.value } : q
                              )
                            );
                          }}
                          className="w-24 rounded border border-gray-300 px-2 py-1 text-sm"
                        />
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {item.success ? (
                        <input
                          type="date"
                          value={item.editedDOB}
                          onChange={(e) => {
                            setQueue((prev) =>
                              prev.map((q) =>
                                q.id === item.id ? { ...q, editedDOB: e.target.value } : q
                              )
                            );
                          }}
                          className="w-28 rounded border border-gray-300 px-2 py-1 text-sm"
                        />
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-4 py-2 text-sm">{item.birthYearBE || "-"}</td>
                    <td className="px-4 py-2">
                      {item.success ? <EligibilityBadge status={item.eligibilityStatus} /> : "-"}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      {item.success ? `${((item.confidence || 0) * 100).toFixed(0)}%` : "-"}
                    </td>
                    <td className="px-4 py-2 text-right space-x-2">
                      {item.success && item.warnings && item.warnings.length > 0 && (
                        <button
                          onClick={() => {
                            setShowOCRText((prev) => {
                              const newSet = new Set(prev);
                              if (newSet.has(item.id)) {
                                newSet.delete(item.id);
                              } else {
                                newSet.add(item.id);
                              }
                              return newSet;
                            });
                          }}
                          className="text-blue-600 hover:text-blue-900 text-xs"
                        >
                          ⚠️
                        </button>
                      )}
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        className="text-red-600 hover:text-red-900 text-xs"
                      >
                        ลบ
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 justify-end">
            <button
              onClick={handleSaveSelected}
              disabled={saving || selectedIds.size === 0}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700 disabled:bg-gray-400"
            >
              {saving ? "กำลังบันทึก..." : `บันทึก (${selectedIds.size})`}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
