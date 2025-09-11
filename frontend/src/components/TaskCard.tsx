import React from "react";
import type { Task } from "../types";

function priBadge(p: number) {
  if (p >= 5) return "bg-[rgba(239,68,68,0.12)] text-red-600 ring-1 ring-[rgba(239,68,68,0.25)]";
  if (p === 4) return "bg-[rgba(249,115,22,0.12)] text-orange-600 ring-1 ring-[rgba(249,115,22,0.25)]";
  if (p === 3) return "bg-[rgba(250,204,21,0.12)] text-yellow-700 ring-1 ring-[rgba(250,204,21,0.25)]";
  if (p === 2) return "bg-[rgba(56,189,248,0.12)] text-sky-700 ring-1 ring-[rgba(56,189,248,0.25)]";
  return "bg-[rgba(113,113,122,0.12)] text-zinc-700 ring-1 ring-[rgba(113,113,122,0.25)]";
}

export const TaskCard: React.FC<{ task: Task }> = ({ task }) => {
  return (
<li className="rounded-xl bg-white px-3 py-2 border border-[rgba(0,0,0,0.06)] shadow-md hover:shadow-xl transition-transform hover:-translate-y-0.5">
  <div className="text-sm font-medium text-zinc-900">{task.text}</div>
  <div className="mt-1 flex items-center gap-2 text-[11px]">
    <span className={`px-2 py-0.5 rounded-full ${priBadge(task.priority)}`}>p{task.priority}</span>
    {task.due ? (
      <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 ring-1 ring-purple-200">
        due {task.due}
      </span>
    ) : null}
  </div>
</li>
  );
};