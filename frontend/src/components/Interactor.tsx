import React, { useRef, useState } from "react";

export default function Interactor({
  onSubmit,
  loading = false,
}: {
  onSubmit: (text: string) => Promise<void> | void;
  loading?: boolean;
}) {
  const [value, setValue] = useState("");
  const taRef = useRef<HTMLTextAreaElement | null>(null);

  function autoGrow() {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const text = value.trim();
    if (!text) return;
    await onSubmit(text);
    setValue("");
    autoGrow();
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-gray-200 rounded-2xl p-3 shadow-sm">
      <div className="flex items-start gap-2">
        <div className="flex-1">
          <textarea
            ref={taRef}
            value={value}
            onChange={(e) => { setValue(e.target.value); autoGrow(); }}
            onInput={autoGrow}
            rows={1}
            placeholder='Try: “coffee with Brian at 5” or “view all work today”'
            className="w-full resize-none outline-none px-3 py-2 rounded-xl bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 px-4 py-2 rounded-xl bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "…" : "Go"}
        </button>
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        <span>Assistant understands: add / view / delete</span>
        <span className="hidden sm:block">Delete is strict: “delete task id 4”</span>
      </div>
    </form>
  );
}