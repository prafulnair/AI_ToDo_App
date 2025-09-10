import React from "react";
import type { Task } from "../types/types";

const catColor: Record<string, string> = {
  work: "border-blue-300 bg-blue-50",
  personal: "border-purple-300 bg-purple-50",
  health: "border-green-300 bg-green-50",
  career: "border-amber-300 bg-amber-50",
  errand: "border-pink-300 bg-pink-50",
};

function chip(priority: number) {
  const palette = ["", "bg-gray-200", "bg-gray-300", "bg-yellow-200", "bg-orange-300", "bg-red-400 text-white"];
  return palette[priority] || "bg-gray-200";
}

export default function TaskCard({ task }: { task: Task }) {
  return (
    <div
      className={`rounded-xl border p-3 shadow-sm transition hover:shadow ${catColor[task.category] || "border-gray-200 bg-white"}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wide text-gray-600">{task.category}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${chip(task.priority)}`}>p{task.priority}</span>
      </div>
      <div className="mt-2 text-sm text-gray-900">{task.text}</div>
      <div className="mt-1 text-xs text-gray-600">
        {task.due_dt ? new Date(task.due_dt).toLocaleString() : "No due"}
      </div>
    </div>
  );
}