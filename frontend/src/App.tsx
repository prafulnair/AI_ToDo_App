import { useEffect, useState } from "react";
import InputArea from "./components/InputArea/InputArea";
import CategoryCard from "./components/CategoryCard/CategoryCard";
import TaskCard from "./components/TaskCard/TaskCard";
import Modal from "./components/Modal/Modal";

// Types
import type { Task, Category } from "./types/task";

import { apiFetch } from "./utils/api";

// --- API helpers ---
async function addTask(text: string): Promise<Task> {
  return apiFetch<Task>("/tasks", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

async function getTasks(): Promise<Task[]> {
  return apiFetch<Task[]>("/tasks");
}

async function markDone(id: number): Promise<Task> {
  return apiFetch<Task>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "done" }),
  });
}

async function deleteTask(id: number): Promise<Task> {
  return apiFetch<Task>(`/tasks/${id}`, { method: "DELETE" });
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      splitAndSet(data);
    } catch (err) {
      console.error("Failed to load tasks:", err);
    }
  };

  // --- Helper to split into isolated + categories ---
  const splitAndSet = (data: Task[]) => {
    const grouped: Record<string, Task[]> = {};
    const isolated: Task[] = [];

    data.forEach((t) => {
      if (t.category && t.category.trim() !== "") {
        if (!grouped[t.category]) grouped[t.category] = [];
        grouped[t.category].push(t);
      } else {
        isolated.push(t);
      }
    });

    setTasks(isolated);
    setCategories(
      Object.entries(grouped).map(([name, ts]) => ({
        name,
        tasks: ts,
      }))
    );
  };

  // --- Handlers ---
  const handleTaskSubmit = async (text: string) => {
    try {
      await addTask(text);
      await loadTasks(); // reload so AI categorization is reflected
    } catch (err) {
      console.error("Failed to add task:", err);
    }
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
  };

  const handleTaskDone = async (id: number) => {
    try {
      await markDone(id);
      await loadTasks();
      setSelectedTask(null);
    } catch (err) {
      console.error("Failed to mark task done:", err);
    }
  };

  const handleTaskDelete = async (id: number) => {
    try {
      await deleteTask(id);
      await loadTasks();
      setSelectedTask(null);
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  // --- Render ---
  return (
    <div className="grid grid-cols-3 h-screen bg-gray-100 dark:bg-gray-900">
      {/* Left: Input */}
      <div className="col-span-1 border-r border-gray-200 dark:border-gray-700 flex items-center justify-center bg-white dark:bg-gray-800">
        <InputArea onTaskSubmit={handleTaskSubmit} />
      </div>

      {/* Right: Task board */}
      <div className="col-span-2 p-6 overflow-y-auto space-y-4 relative">
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

        {/* Dynamic Category cards */}
        {categories.map((cat) => (
          <CategoryCard
            key={cat.name}
            name={cat.name}
            tasks={cat.tasks}
            onTaskClick={handleTaskClick}
          />
        ))}

        {/* Modal for single task */}
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