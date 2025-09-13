import { Card, Button } from "flowbite-react";
import type { Task } from "../../types/task";

// TaskCard.tsx
interface TaskCardProps {
  task: Task;
  onDone: (id: number) => void;
  onDelete: (id: number) => void;
  onClose?: () => void;
}
const TaskCard: React.FC<TaskCardProps> = ({ task, onDone, onDelete, onClose }) => {
  const isDone = task.status === "done";

  return (
    <Card className="max-w-md w-full shadow-md relative">
      {/* Close button (only if provided) */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      <h5 className="text-xl font-bold tracking-tight text-gray-900 dark:text-white text-center">
        {task.text}
      </h5>
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
        {isDone ? "Completed" : "Pending"}
      </p>

      <div className="flex justify-center gap-4 mt-3">
        <Button onClick={() => onDone(task.id)} disabled={isDone}>
          Done
        </Button>

        <Button color="failure" onClick={() => onDelete(task.id)}>
          Delete
        </Button>
      </div>
    </Card>
  );
};

export default TaskCard;