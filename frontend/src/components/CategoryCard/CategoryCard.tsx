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
    <Card className="max-w-md mx-auto shadow-md">
      {/* Collapsed view */}
      {!expanded && (
        <div className="text-center">
          <h5 className="text-xl font-bold tracking-tight text-gray-900 dark:text-white">
            {name}
          </h5>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {tasks.length} task{tasks.length !== 1 && "s"}
          </p>
          <div className="flex justify-center">
            <Button onClick={() => setExpanded(true)}>Expand</Button>
          </div>
        </div>
      )}

      {/* Expanded view */}
      {expanded && (
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h5 className="text-xl font-bold leading-none text-gray-900 dark:text-white">
              {name}
            </h5>
            <Button size="xs" color="light" onClick={() => setExpanded(false)}>
              Collapse
            </Button>
          </div>
          <div className="flow-root">
            <ul className="divide-y divide-gray-200 dark:divide-gray-700">
              {sortedTasks.map((task) => (
                <li
                  key={task.id}
                  className="py-3 sm:py-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded"
                  onClick={() => onTaskClick(task)}
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900 dark:text-white">
                        {task.text}
                      </p>
                      <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                        {task.status === "done" ? "Completed" : "Pending"}
                      </p>
                      {task.due_dt && (
                        <p className={`truncate text-xs ${getDueClass(task)}`}>
                          Due: {new Date(task.due_dt).toLocaleString()}
                        </p>
                      )}
                    </div>
                    {task.priority !== undefined && (
                      <Badge color={priorityColor(task.priority)}>
                        {priorityLabel(task.priority)}
                      </Badge>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </Card>
  );
};

export default CategoryCard;