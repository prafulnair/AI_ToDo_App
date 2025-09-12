import { Card, Button } from "flowbite-react";
import type { Task } from "../../types/task";

interface TaskCardProps {
  task: Task;
  onDone: (id: string) => void;
  onDelete: (id: string) => void;
  onClose?: () => void; // optional close handler for modal
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onDone, onDelete, onClose }) => {
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
        {task.title}
      </h5>
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
        {task.isDone ? "Completed" : "Pending"}
      </p>

      <div className="flex justify-center gap-4 mt-3">
        <Button onClick={() => onDone(task.id)} disabled={task.isDone}>
          Done
          <svg
            className="-mr-1 ml-2 h-4 w-4"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 
              0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 
              11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 
              0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </Button>

        <Button onClick={() => onDelete(task.id)}>
          Delete
          <svg
            className="-mr-1 ml-2 h-4 w-4"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 
              0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 
              11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 
              0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </Button>
      </div>
    </Card>
  );
};

export default TaskCard;