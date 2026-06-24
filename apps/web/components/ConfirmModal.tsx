"use client";

import { useState } from "react";

interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  inputRequired?: string;
  loading?: boolean;
}

export default function ConfirmModal({
  isOpen,
  title,
  message,
  confirmText = "ยืนยัน",
  cancelText = "ยกเลิก",
  onConfirm,
  onCancel,
  inputRequired,
  loading = false,
}: ConfirmModalProps) {
  const [input, setInput] = useState("");

  if (!isOpen) return null;

  const canConfirm = !inputRequired || input === inputRequired;

  const handleConfirm = () => {
    if (canConfirm) {
      setInput("");
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">{title}</h2>
        <p className="text-gray-600 mb-6">{message}</p>

        {inputRequired && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              พิมพ์ "{inputRequired}" เพื่อยืนยัน:
            </label>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={inputRequired}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:opacity-50"
          >
            {cancelText}
          </button>
          <button
            onClick={handleConfirm}
            disabled={!canConfirm || loading}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "กำลังดำเนินการ..." : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
