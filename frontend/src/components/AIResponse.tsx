import React from "react";

export default function AIResponse({ message }: { message: string }) {
  if (!message) return null;
  return (
    <div className="mt-3 text-sm bg-gradient-to-r from-emerald-50 to-emerald-100 border border-emerald-300 text-emerald-900 px-3 py-2 rounded-xl shadow-sm">
      {message}
    </div>
  );
}