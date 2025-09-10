import React from "react";
import type { Task } from "../types/task";
import TaskCard from "./TaskCard";

const DynamicView: React.FC<{ tasks: Task[] }> = ({ tasks }) => {
  if (tasks.length === 0) {
    return <div className="text-neutral-500 dark:text-neutral-400">No tasks yet.</div>;
  }

  // group by category
  const grouped = tasks.reduce<Record<string, Task[]>>((acc, t) => {
    (acc[t.category] ||= []).push(t);
    return acc;
  }, {});

  return (
    <div className="space-y-10">
      {Object.entries(grouped).map(([category, list]) => (
        <section key={category}>
          <header className="mb-3 flex items-center justify-between">
            <h2 className="uppercase tracking-wide text-sm text-neutral-500 dark:text-neutral-400">
              {category}
            </h2>
            <span className="text-xs text-neutral-400">{list.length} {list.length === 1 ? "task" : "tasks"}</span>
          </header>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {list.map(t => <TaskCard key={t.id} task={t} />)}
          </div>
        </section>
      ))}
    </div>
  );
};

export default DynamicView;