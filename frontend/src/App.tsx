import { useState } from "react";
import InputArea from "./components/InputArea/InputArea";
import CategoryCard from "./components/CategoryCard/CategoryCard";
import TaskCard from "./components/TaskCard/TaskCard";
import Modal from "./components/Modal/Modal";

// Types
import type { Task, Category } from "./types/task";

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([
    {
      name: "Work",
      tasks: [
        {
          id: "w1",
          title: "Finish project draft",
          isDone: false,
          createdAt: new Date(),
        },
        {
          id: "w2",
          title: "Email Stephanie",
          isDone: true,
          createdAt: new Date(),
        },
      ],
    },
    {
      name: "Health",
      tasks: [
        {
          id: "h1",
          title: "Yoga at 7pm",
          isDone: false,
          createdAt: new Date(),
        },
      ],
    },
  ]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const handleTaskSubmit = (text: string) => {
    const newTask: Task = {
      id: Date.now().toString(),
      title: text,
      isDone: false,
      createdAt: new Date(),
    };

    // Randomly assign: isolated OR category
    const random = Math.random();
    if (random < 0.5) {
      // Add to isolated tasks
      setTasks((prev) => [...prev, newTask]);
    } else {
      // Add to a random category
      setCategories((prev) => {
        if (prev.length === 0) return prev;
        const randomIndex = Math.floor(Math.random() * prev.length);
        const updated = [...prev];
        updated[randomIndex] = {
          ...updated[randomIndex],
          tasks: [...updated[randomIndex].tasks, newTask],
        };
        return updated;
      });
    }
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
  };

  const handleTaskDone = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isDone: true } : t))
    );
    setCategories((prev) =>
      prev.map((c) => ({
        ...c,
        tasks: c.tasks.map((t) =>
          t.id === id ? { ...t, isDone: true } : t
        ),
      }))
    );
    setSelectedTask(null);
  };

  const handleTaskDelete = (id: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
    setCategories((prev) =>
      prev.map((c) => ({
        ...c,
        tasks: c.tasks.filter((t) => t.id !== id),
      }))
    );
    setSelectedTask(null);
  };

  return (
    <div className="grid grid-cols-3 h-screen bg-gray-100 dark:bg-gray-900">
      {/* Left: Input */}
      <div className="col-span-1 border-r border-gray-200 dark:border-gray-700 flex items-center justify-center bg-white dark:bg-gray-800">
        <InputArea onTaskSubmit={handleTaskSubmit} />
      </div>

      {/* Right: Task board */}
      <div className="col-span-2 p-6 overflow-y-auto space-y-4 relative">
        {/* Empty state */}
        {categories.length === 0 && tasks.length === 0 && (
          <p className="text-gray-500 text-center">No tasks yet. Add one!</p>
        )}

        {/* Isolated tasks */}
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onDone={handleTaskDone}
            onDelete={handleTaskDelete}
          />
        ))}

        {/* Category cards */}
        {categories.map((cat) => (
          <CategoryCard
            key={cat.name}
            name={cat.name}
            tasks={cat.tasks}
            onTaskClick={handleTaskClick}
          />
        ))}

        {/* Overlay TaskCard when a task is selected */}
        {/* Overlay TaskCard when a task is selected */}
{/* Overlay TaskCard when a task is selected */}
{selectedTask && (
  <Modal onClose={() => setSelectedTask(null)}>
    <TaskCard
      task={selectedTask}
      onDone={handleTaskDone}
      onDelete={handleTaskDelete}
      onClose={() => setSelectedTask(null)}
    />
  </Modal>
)}
      </div>
    </div>
  );
}

export default App;