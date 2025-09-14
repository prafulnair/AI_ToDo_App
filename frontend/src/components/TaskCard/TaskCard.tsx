import { Card, Button, Badge } from "flowbite-react";
import type { Task } from "../../types/task";

interface TaskCardProps {
  task: Task;
  onDone: (id: number) => void;
  onDelete: (id: number) => void;
  onClose?: () => void;
}

const priorityColor = (p: number) => {
  if (p >= 5) return "failure"; // 🔥 very urgent = red
  if (p === 4) return "warning"; // ⚠️ high = amber
  if (p === 3) return "info";    // ℹ️ medium = blue
  if (p === 2) return "success"; // ✅ low = green
  return "gray";                 // trivial
};

const priorityLabel = (p: number) => {
  if (p >= 5) return "🔥 Critical";
  if (p === 4) return "⚠️ High";
  if (p === 3) return "🔷 Medium";
  if (p === 2) return "✅ Low";
  return "• Trivial";
};

// const TaskCard: React.FC<TaskCardProps> = ({ task, onDone, onDelete, onClose }) => {
//   const isDone = task.status === "done";

//   return (
//     <Card className="max-w-md w-full shadow-md relative">
//       {/* Close button (modal only) */}
//       {onClose && (
//         <button
//           onClick={onClose}
//           className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
//         >
//           <svg
//             className="h-5 w-5"
//             fill="none"
//             stroke="currentColor"
//             viewBox="0 0 24 24"
//           >
//             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
//           </svg>
//         </button>
//       )}

//       <h5 className="text-xl font-bold tracking-tight text-gray-900 dark:text-white text-center">
//         {task.text}
//       </h5>

//       {/* Status + Priority */}
//       <div className="flex justify-center items-center gap-2 mt-2">
//         <p className="text-sm text-gray-500 dark:text-gray-400">
//           {isDone ? "Completed" : "Pending"}
//         </p>
//         {task.priority !== undefined && (
//           <Badge color={priorityColor(task.priority)}>
//             {priorityLabel(task.priority)}
//           </Badge>
//         )}
//       </div>

//       {/* Actions */}
//       <div className="flex justify-center gap-4 mt-3">
//         <Button onClick={() => onDone(task.id)} disabled={isDone}>
//           Done
//         </Button>

//         <Button color="failure" onClick={() => onDelete(task.id)}>
//           Delete
//         </Button>
//       </div>
//     </Card>
//   );
// };

// export default TaskCard;

const TaskCard: React.FC<TaskCardProps> = ({ task, onDone, onDelete, onClose }) => {
  const isDone = task.status === "done";

  return (
    <div className="w-96 border-black border-2 rounded-md hover:shadow-[6px_6px_0px_rgba(0,0,0,1)] bg-white relative p-6">
  {/* Close button */}
  {onClose && (
    <button
      onClick={onClose}
      className="absolute top-3 right-3 text-black hover:opacity-70"
    >
      ✕
    </button>
  )}

  {/* Task title */}
  <h5 className="text-xl font-extrabold text-center mb-4 leading-snug">
    {task.text}
  </h5>

  {/* Status + Priority inline */}
  <div className="flex justify-center gap-3 items-center mb-6">
    <span className="text-sm">{isDone ? "✅ Completed" : "⏳ Pending"}</span>
    {task.priority !== undefined && (
      <span
        className={`px-3 py-1 text-xs font-bold border-2 border-black ${
          task.priority >= 4
            ? "bg-yellow-200"
            : task.priority === 3
            ? "bg-blue-200"
            : task.priority === 2
            ? "bg-green-200"
            : "bg-gray-200"
        }`}
      >
        {priorityLabel(task.priority)}
      </span>
    )}
  </div>

  {/* Actions */}
  <div className="flex justify-between mt-4">
    <button
      onClick={() => onDone(task.id)}
      disabled={isDone}
      className="flex-1 mr-2 h-12 border-black border-2 bg-[#A6FAFF] hover:bg-[#79F7FF] hover:shadow-[2px_2px_0px_rgba(0,0,0,1)] active:bg-[#00E1EF] disabled:opacity-50"
    >
      Done
    </button>

    <button
      onClick={() => onDelete(task.id)}
      className="flex-1 ml-2 h-12 border-black border-2 bg-red-200 hover:bg-red-300 hover:shadow-[2px_2px_0px_rgba(0,0,0,1)] active:bg-red-400"
    >
      Delete
    </button>
  </div>
</div>
  );
};

export default TaskCard;