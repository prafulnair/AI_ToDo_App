import React, { useMemo } from "react";
import type { Task, Category } from "../types";
import { TaskCard } from "./TaskCard";

const CATS: Category[] = ["work", "career", "health", "errands", "personal"];
const label: Record<Category, string> = {
  work: "Work",
  career: "Career",
  health: "Health",
  errands: "Errands",
  personal: "Personal",
};

const catHeader = (c: Category) => {
  switch (c) {
    case "work":
      return "from-sky-100 to-blue-100 text-sky-900";
    case "career":
      return "from-pink-100 to-fuchsia-100 text-fuchsia-900";
    case "health":
      return "from-emerald-100 to-teal-100 text-emerald-900";
    case "errands":
      return "from-amber-100 to-orange-100 text-amber-900";
    default:
      return "from-violet-100 to-indigo-100 text-violet-900";
  }
};

export const TaskBoard: React.FC<{ tasks: Task[]; isolatedTask?: Task | null }> = ({ tasks, isolatedTask }) => {
  const groups = useMemo(() => {
    const map: Record<Category, Task[]> = { work: [], career: [], health: [], errands: [], personal: [] };
    for (const t of tasks) if (t.category !== "isolated") map[t.category as Category].push(t);
    return map;
  }, [tasks]);

  return (
    <div className="flex-1 h-full overflow-y-auto p-10 bg-slate-100">
      {/* Optional isolated single task */}
      {isolatedTask ? (
        <div className="mb-8">
          <div className="rounded-2xl bg-white border border-[rgba(0,0,0,0.06)] shadow-xl p-5">
            <h2 className="text-lg font-semibold text-zinc-900 mb-3">Task</h2>
            <ul className="space-y-2">
              <TaskCard task={isolatedTask} />
            </ul>
          </div>
        </div>
      ) : null}

      <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-8">
        {CATS.map((c) => (
          <div key={c} className="rounded-2xl bg-white border border-[rgba(0,0,0,0.06)] shadow-xl overflow-hidden">
            <div className={`px-5 py-3 bg-gradient-to-r ${catHeader(c)} text-sm font-semibold tracking-wide`}>
              {label[c]}
            </div>
            <div className="p-5">
              <ul className="space-y-2">
                {groups[c].length === 0 ? (
                  <li className="text-zinc-400 italic">No tasks</li>
                ) : (
                  groups[c].map((t) => <TaskCard key={t.id} task={t} />)
                )}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};