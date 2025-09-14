// src/components/SummaryPanel/SummaryPanel.tsx
import { useState } from "react";
import type { Task } from "../../types/task";
import { Card, Badge, Button } from "flowbite-react";

interface SummaryData {
  headline: string;
  kpis: { open: number; completed: number; overdue: number; due_today: number };
  highlights: string[];
  by_category: { name: string; open: number; done: number }[];
  urgent_ids: number[];
  overdue_ids: number[];
  markdown: string;
  narrative?: string; // <-- NEW (plain text)

}

interface Props {
  summary: SummaryData;
  tasks: Task[];
  onClose: () => void;
  onTaskClick: (task: Task) => void;
}

const SummaryPanel: React.FC<Props> = ({ summary, tasks, onClose, onTaskClick }) => {
  const [copied, setCopied] = useState(false);

  const copyMarkdown = () => {
    navigator.clipboard.writeText(summary.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const findTask = (id: number) => tasks.find((t) => t.id === id);

  return (
    <div className="w-full max-w-2xl border-2 border-black rounded-md bg-white shadow-[6px_6px_0px_rgba(0,0,0,1)] hover:shadow-[10px_10px_0px_rgba(0,0,0,1)] transition-shadow p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-2xl font-extrabold">{summary.headline}</h3>
        <button
          onClick={onClose}
          className="px-3 py-1 border-2 border-black bg-gray-200 hover:bg-gray-300 active:translate-x-[2px] active:translate-y-[2px]"
        >
          Close
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        <div className="bg-gray-100 border-2 border-black p-2 text-center">
          <p className="text-sm font-semibold">Open</p>
          <p className="text-xl font-bold">{summary.kpis.open}</p>
        </div>
        <div className="bg-gray-100 border-2 border-black p-2 text-center">
          <p className="text-sm font-semibold">Completed</p>
          <p className="text-xl font-bold">{summary.kpis.completed}</p>
        </div>
        <div className="bg-gray-100 border-2 border-black p-2 text-center">
          <p className="text-sm font-semibold">Overdue</p>
          <p className="text-xl font-bold text-red-600">{summary.kpis.overdue}</p>
        </div>
        <div className="bg-gray-100 border-2 border-black p-2 text-center">
          <p className="text-sm font-semibold">Due Today</p>
          <p className="text-xl font-bold text-amber-600">{summary.kpis.due_today}</p>
        </div>
      </div>

      {/* Narrative (AI summary text)
      <div className="mb-6 p-3 border-2 border-black bg-gray-50">
        <p className="text-base leading-relaxed">{summary.markdown}</p>
      </div> */}

              {/* Conversational narrative (PLAIN TEXT) */}
      {(summary.narrative && summary.narrative.trim()) ? (
        <div className="border-2 border-black rounded-md p-4 mb-6 bg-white">
          <p className="text-base leading-relaxed">{summary.narrative}</p>
        </div>
      ) : null}

      {/* Highlights */}
      {summary.highlights.length > 0 && (
        <div className="mb-4">
          <h4 className="font-bold mb-2">Highlights</h4>
          <ul className="list-disc list-inside text-sm space-y-1">
            {summary.highlights.map((h, idx) => (
              <li key={idx}>{h}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Categories */}
      <div className="flex flex-wrap gap-2 mb-4">
        {summary.by_category.map((c) => (
          <span
            key={c.name}
            className="px-3 py-1 border-2 border-black bg-blue-100 text-sm font-semibold"
          >
            {c.name}: {c.open} open / {c.done} done
          </span>
        ))}
      </div>

      {/* Urgent & Overdue */}
      <div className="mb-6">
        {summary.urgent_ids.length > 0 && (
          <div className="mb-3">
            <h4 className="font-bold">Urgent</h4>
            <ul className="text-sm space-y-1">
              {summary.urgent_ids.map((id) => {
                const t = findTask(id);
                return (
                  t && (
                    <li
                      key={id}
                      className="cursor-pointer hover:underline"
                      onClick={() => onTaskClick(t)}
                    >
                      {t.text}
                    </li>
                  )
                );
              })}
            </ul>
          </div>
        )}
        {summary.overdue_ids.length > 0 && (
          <div>
            <h4 className="font-bold">Overdue</h4>
            <ul className="text-sm text-red-600 space-y-1">
              {summary.overdue_ids.map((id) => {
                const t = findTask(id);
                return (
                  t && (
                    <li
                      key={id}
                      className="cursor-pointer hover:underline"
                      onClick={() => onTaskClick(t)}
                    >
                      {t.text}
                    </li>
                  )
                );
              })}
            </ul>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-end">
        <button
          onClick={copyMarkdown}
          className="px-3 py-1 border-2 border-black bg-green-200 hover:bg-green-300 active:translate-x-[2px] active:translate-y-[2px] text-sm"
        >
          {copied ? "Copied!" : "Copy Narrative"}
        </button>
      </div>
    </div>
  );
};

export default SummaryPanel;