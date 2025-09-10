import React, { useEffect, useMemo, useState } from "react";
import Interactor from "./components/Interactor";
import AIResponse from "./components/AIResponse";
import TaskBoard from "./components/TaskBoard";
import type { Task } from "./types/types";
import { ensureSessionId } from "./utils/session";

// TODO: set this to your deployed backend later
const BACKEND_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const sessionId = useMemo(() => ensureSessionId(), []);
  const [aiMsg, setAiMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([
    // mock seed (looks good while wiring)
    {
      id: 1, text: "Finish API doc", category: "work", priority: 4,
      due_dt: null, status: "open", created_at: new Date().toISOString()
    },
    {
      id: 2, text: "Buy groceries", category: "personal", priority: 3,
      due_dt: null, status: "open", created_at: new Date().toISOString()
    },
  ]);

  // fetch tasks (will replace mock once backend is ready)
  async function fetchTasks() {
    const res = await fetch(`${BACKEND_URL}/tasks`, {
      headers: { "X-Session-Id": sessionId },
    });
    if (res.ok) {
      const data = await res.json();
      setTasks(data);
    }
  }

  useEffect(() => {
    // comment out this call until backend is running locally
    // fetchTasks();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleInteractor(text: string) {
    setLoading(true);
    setAiMsg("");
    try {
      // naive rule: everything goes to /tasks add for now
      const res = await fetch(`${BACKEND_URL}/tasks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Session-Id": sessionId,
        },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || "Failed to add");
      }

      const created: Task = await res.json();
      // show a tiny AI message from created task details
      setAiMsg(`✅ Added to ${created.category} — ${created.due_dt ? `due ${new Date(created.due_dt).toLocaleString()}, ` : ""}priority ${created.priority}`);
      // optimistically add to UI
      setTasks((prev) => [created, ...prev]);
    } catch (e: any) {
      setAiMsg(`⚠️ ${e.message || "Something went wrong"}`);
    } finally {
      setLoading(false);
    }
  }

  function openCategory(cat: Task["category"]) {
    // Placeholder: in v2 you can route to /category/:cat or open a modal
    setAiMsg(`Showing all in ${cat.toUpperCase()}`);
  }

  return (
    <div className="h-screen bg-gray-50">
      {/* Header */}
      <header className="px-6 py-4 bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold">Smart AI Task Manager</h1>
          <div className="text-xs text-gray-500">Session: {sessionId.slice(0, 8)}…</div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: Interactor + AI message */}
        <section>
          <Interactor onSubmit={handleInteractor} loading={loading} />
          <AIResponse message={aiMsg} />
        </section>

        {/* Right: Dynamic board */}
        <section>
          <TaskBoard tasks={tasks} onOpenCategory={openCategory} />
        </section>
      </main>
    </div>
  );
}