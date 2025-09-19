import { useEffect, useState } from "react";
import InputArea from "./components/InputArea/InputArea";
import CategoryCard from "./components/CategoryCard/CategoryCard";
import TaskCard from "./components/TaskCard/TaskCard";
import Modal from "./components/Modal/Modal";
import SummaryPanel from "./components/SummaryPanel/SummaryPanel";
import { useNotify } from "./components/ToastProvider";
import QuickStats from "./components/QuickStats/QuickStats";
import Navbar from "./components/Navbar/Navbar";

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

async function parseCommand(text: string): Promise<any> {
  return apiFetch<any>("/nlp/command", {
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

async function summarize(params: { timeframe: string; category?: string }) {
  return apiFetch<any>("/summary", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isFiltered, setIsFiltered] = useState(false);
  const [summaryData, setSummaryData] = useState<any | null>(null);
  const notify = useNotify();
  const [isSidebarOpen, setSidebarOpen] = useState(false);

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

  // --- Intent-aware task submit ---
const handleTaskSubmit = async (text: string) => {
  try {
    // 1. Ask AI what the user meant
    const intent = await apiFetch<{ intent: string; rationale: string }>(
      "/nlp/intent",
      {
        method: "POST",
        body: JSON.stringify({ text }),
      }
    );

    // 2. If it's a command → refine with /nlp/command
    if (intent.intent === "command") {
      const cmd = await parseCommand(text);

      if (cmd.action === "show") {
        const data = await getTasks();
        const filtered = data.filter((t) => {
          if (cmd.category && t.category !== cmd.category) return false;
          if (cmd.timeframe === "today" && t.due_dt) {
            const due = new Date(t.due_dt);
            const now = new Date();
            return due.toDateString() === now.toDateString();
          }
          return true;
        });
        splitAndSet(filtered);
        setIsFiltered(true);

        notify.info(
          `Showing ${filtered.length} task(s)${
            cmd.category ? ` in "${cmd.category}"` : ""
          } ${cmd.timeframe ? `for ${cmd.timeframe}` : ""}`
        );
        return;
      }

      if (cmd.action === "complete_all") {
  const data = await getTasks();
  let doneCount = 0;

  await Promise.all(
    data.map(async (t) => {
      if (t.status !== "done") {
        try {
          await markDone(t.id);
          doneCount++;
        } catch {
          // ignore already-done tasks
        }
      }
    })
  );

  await loadTasks();

  if (doneCount > 0) {
    notify.success(`Marked ${doneCount} task(s) as done`);
  } else {
    notify.info("All tasks were already marked as done");
  }
  return;
}

      if (cmd.action === "delete_category" && cmd.category) {
        const data = await getTasks();
        const toDelete = data.filter((t) => t.category === cmd.category);
        await Promise.all(toDelete.map((t) => deleteTask(t.id)));
        await loadTasks();

        notify.danger(`Deleted ${toDelete.length} task(s) in "${cmd.category}"`);
        return;
      }

      if (cmd.action === "summarize") {
        const data = await summarize({
          timeframe: cmd.timeframe || "all",
          category: cmd.category || undefined,
        });
        setSummaryData(data);

        notify.warning(
          `Summary generated for ${
            cmd.category ? `"${cmd.category}" ` : ""
          }${cmd.timeframe || "all"}`
        );
        return;
      }
    }

    // 3. Otherwise → treat as plain add task
    await addTask(text);
    await loadTasks();
    notify.success("Task added!");
  } catch (err) {
    console.error("Failed to process input:", err);
    notify.danger("Something went wrong while processing your request");
  }
};

  const handleTaskClick = (task: Task) => setSelectedTask(task);

  const handleTaskDone = async (id: number) => {
    try {
      await markDone(id);
      await loadTasks();
      notify.info("Task marked done!");
      setSelectedTask(null);
    } catch (err) {
      console.error("Failed to mark task done:", err);
    }
  };

  const handleTaskDelete = async (id: number) => {
    try {
      await deleteTask(id);
      await loadTasks();
      notify.danger("Task deleted!");
      setSelectedTask(null);
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  };

  const allTasks = [...tasks, ...categories.flatMap((c) => c.tasks)];

  return (
    <div className="flex flex-col h-screen">
      {/* 🔹 Top Navbar */}
      <Navbar onToggleSidebar={() => setSidebarOpen(!isSidebarOpen)} />

      {/* 🔹 Main Content Area with top margin */}
      <div className="grid grid-cols-3 flex-1 bg-gray-100 mt-4 gap-4 px-4">
        {/* Left Column (cyan card) */}
        <div className="col-span-1">
          <div
            className="w-full h-[90%] border-2 border-black rounded-md 
                       bg-[#9EE7EB] 
                       hover:shadow-[8px_8px_0px_rgba(0,0,0,1)] transition-shadow 
                       flex flex-col space-y-6 p-4"
          >
            <QuickStats
              total={allTasks.length}
              completed={allTasks.filter((t) => t.status === "done").length}
              pending={allTasks.filter((t) => t.status !== "done").length}
            />

            <div className="border-2 border-black rounded-md bg-white p-4 hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]">
              <InputArea
                onTaskSubmit={handleTaskSubmit}
                onSummarizeToday={async () => {
                  const data = await summarize({ timeframe: "today" });
                  setSummaryData(data);
                }}
                onSummarizeWeek={async () => {
                  const data = await summarize({ timeframe: "this_week" });
                  setSummaryData(data);
                }}
              />
            </div>
          </div>
        </div>

        {/* Right Column (purple card) */}
        <div className="col-span-2">
          <div
            className="w-full h-[90%] border-2 border-black rounded-md  
                       bg-[#A5B4FB] 
                       hover:shadow-[8px_8px_0px_rgba(0,0,0,1)] transition-shadow 
                       p-6 overflow-y-auto space-y-4 relative"
          >
            {categories.length === 0 && tasks.length === 0 && (
              <p className="text-gray-800 font-medium text-center">
                No tasks yet. Add one!
              </p>
            )}

            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onDone={handleTaskDone}
                onDelete={handleTaskDelete}
              />
            ))}

            {isFiltered && (
              <div className="text-center mb-4">
                <p className="text-sm text-gray-800">🔍 Showing filtered results</p>
                <button
                  className="text-sm text-blue-700 hover:underline"
                  onClick={() => {
                    loadTasks();
                    setIsFiltered(false);
                  }}
                >
                  🔙 Back to All Tasks
                </button>
              </div>
            )}

            {categories.map((cat) => (
              <CategoryCard
                key={cat.name}
                name={cat.name}
                tasks={cat.tasks}
                onTaskClick={handleTaskClick}
              />
            ))}

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

            {summaryData && (
              <Modal onClose={() => setSummaryData(null)}>
                <SummaryPanel
                  summary={summaryData}
                  tasks={allTasks}
                  onClose={() => setSummaryData(null)}
                  onTaskClick={handleTaskClick}
                />
              </Modal>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;