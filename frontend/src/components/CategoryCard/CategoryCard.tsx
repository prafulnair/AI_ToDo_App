import { useState } from "react";
import { Button, Card } from "flowbite-react";
import type { Task } from "../../types/task";

interface CategoryCardProps {
  name: string;
  tasks: Task[];
  onTaskClick: (task: Task) => void;
}

const CategoryCard: React.FC<CategoryCardProps> = ({ name, tasks, onTaskClick }) => {
  const [expanded, setExpanded] = useState(false);

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
              {tasks.map((task) => (
                <li
                  key={task.id}
                  className="py-3 sm:py-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 rounded"
                  onClick={() => onTaskClick(task)}
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900 dark:text-white">
                        {task.title}
                      </p>
                      <p className="truncate text-xs text-gray-500 dark:text-gray-400">
                        {task.isDone ? "Completed" : "Pending"}
                      </p>
                    </div>
                    <div className="inline-flex items-center text-sm font-semibold text-gray-900 dark:text-white">
                      •
                    </div>
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