import { useState } from "react";
import { Button, Card, Badge } from "flowbite-react";
import type { Task } from "../../types/task";

interface CategoryCardProps {
  name: string;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

const priorityColor = (p: number) => {
  if (p >= 5) return "failure"; // 🔥 very urgent
  if (p === 4) return "warning"; // ⚠️ high
  if (p === 3) return "info";    // medium
  if (p === 2) return "success"; // low
  return "gray";                 // trivial
};

const priorityLabel = (p: number) => {
  if (p >= 5) return "🔥 Critical";
  if (p === 4) return "⚠️ High";
  if (p === 3) return "🔷 Medium";
  if (p === 2) return "✅ Low";
  return "• Trivial";
};

const CategoryCard: React.FC<CategoryCardProps> = ({ name, tasks, onTaskClick }) => {
  const [expanded, setExpanded] = useState(false);

  // Sort tasks: due date soonest first, then by priority desc
  const sortedTasks = [...tasks].sort((a, b) => {
    const da = a.due_dt ? new Date(a.due_dt).getTime() : Infinity;
    const db = b.due_dt ? new Date(b.due_dt).getTime() : Infinity;
    if (da !== db) return da - db;

    const pa = a.priority ?? 0;
    const pb = b.priority ?? 0;
    return pb - pa; // higher priority first
  });

  const getDueClass = (task: Task) => {
    if (!task.due_dt) return "text-gray-500";
    const due = new Date(task.due_dt);
    const now = new Date();
    if (due < now && task.status !== "done") return "text-red-500 font-semibold";
    const diffHours = (due.getTime() - now.getTime()) / (1000 * 60 * 60);
    if (diffHours <= 24) return "text-amber-500 font-medium";
    if (diffHours <= 48) return "text-yellow-500 font-medium";
    return "text-gray-500";
  };

  return (
    <div className="w-full max-w-md border-black border-2 rounded-md bg-white hover:shadow-[6px_6px_0px_rgba(0,0,0,1)] transition-shadow p-2">
      {/* Collapsed view */}
      {!expanded && (
        <div className="p-6 text-center">
          <h5 className="text-xl font-extrabold mb-2">{name}</h5>
          <p className="text-sm text-gray-600 mb-4">
            {tasks.length} task{tasks.length !== 1 && "s"}
          </p>
          <button
            onClick={() => setExpanded(true)}
            className="h-10 px-4 border-black border-2 bg-[#A6FAFF] hover:bg-[#79F7FF] hover:shadow-[2px_2px_0px_rgba(0,0,0,1)]"
          >
            Expand
          </button>
        </div>
      )}

      {/* Expanded view */}
      {expanded && (
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h5 className="text-xl font-extrabold">{name}</h5>
            <button
              onClick={() => setExpanded(false)}
              className="h-8 px-3 border-black border-2 bg-gray-200 hover:bg-gray-300 hover:shadow-[2px_2px_0px_rgba(0,0,0,1)] text-sm"
            >
              Collapse
            </button>
          </div>

          <ul className="divide-y divide-gray-300">
            {sortedTasks.map((task) => (
              <li
                key={task.id}
                className="py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => onTaskClick(task)}
              >
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1 pr-3">
                    <p className="truncate text-sm font-bold">{task.text}</p>
                    <p className="truncate text-xs text-gray-500">
                      {task.status === "done" ? "✅ Completed" : "⏳ Pending"}
                    </p>
                    {task.due_dt && (
                      <p className={`truncate text-xs ${getDueClass(task)}`}>
                        Due: {new Date(task.due_dt).toLocaleString()}
                      </p>
                    )}
                  </div>
                  {task.priority !== undefined && (
                    <span className="ml-2 px-2 py-1 border-2 border-black bg-yellow-100 text-xs font-bold">
                      {priorityLabel(task.priority)}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default CategoryCard;