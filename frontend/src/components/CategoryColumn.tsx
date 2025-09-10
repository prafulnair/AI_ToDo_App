import React from "react";
import type { Task, Category } from "../types/types";
import TaskCard from "./TaskCard";

const titleColor: Record<Category, string> = {
  work: "text-blue-700",
  personal: "text-purple-700",
  health: "text-green-700",
  career: "text-amber-700",
  errand: "text-pink-700",
};

export default function CategoryColumn({
  title,
  tasks,
  onOpenCategory,
}: {
  title: Category;
  tasks: Task[];
  onOpenCategory?: (cat: Category) => void;
}) {
  return (
    <div className="bg-white rounded-2xl shadow p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-3">
        <h2 className={`font-semibold ${titleColor[title]}`}>{title.toUpperCase()}</h2>
        <button
          className="text-xs text-gray-500 hover:text-gray-800"
          onClick={() => onOpenCategory?.(title)}
        >
          view all →
        </button>
      </div>
      <div className="space-y-3">
        {tasks.length ? tasks.map(t => <TaskCard key={t.id} task={t} />)
                      : <div className="text-xs text-gray-400">No tasks</div>}
      </div>
    </div>
  );
}