import React from "react";
import type { Task, Category } from "../types/types";
import CategoryColumn from "./CategoryColumn";
import TaskCard from "./TaskCard";

const ORDER: Category[] = ["work","personal","health","career","errand"];

function groupByCategory(tasks: Task[]): Record<Category, Task[]> {
  const init: Record<Category, Task[]> = { work:[], personal:[], health:[], career:[], errand:[] };
  tasks.forEach(t => init[t.category].push(t));
  return init;
}

export default function TaskBoard({
  tasks,
  onOpenCategory,
}: {
  tasks: Task[];
  onOpenCategory?: (cat: Category) => void;
}) {
  // Simple morphing: stream if < 4 tasks, otherwise columns
  if (tasks.length < 4) {
    return (
      <div className="grid grid-cols-1 gap-3">
        {tasks.map(t => <TaskCard key={t.id} task={t} />)}
      </div>
    );
  }

  const grouped = groupByCategory(tasks);
  return (
    <div className="grid grid-cols-3 gap-4">
      {ORDER.map(cat => (
        <CategoryColumn
          key={cat}
          title={cat}
          tasks={grouped[cat]}
          onOpenCategory={onOpenCategory}
        />
      ))}
    </div>
  );
}