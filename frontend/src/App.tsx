import React, { useMemo, useState } from "react";
import { TerminalWindow } from "./components/TerminalWindow";
import { Terminal } from "./components/Terminal";
import { TaskBoard } from "./components/TaskBoard";
import type { Task, Category } from "./types";
import { getOrCreateSessionId } from "./utils/session";

let nextId = 1;

function mockCategorize(text: string): { category: Category | "isolated"; priority: number; due?: string | null } {
  const t = text.toLowerCase();
  const has = (arr: string[]) => arr.some((k) => t.includes(k));
  if (has(["meeting", "report", "api", "doc", "deploy"])) return { category: "work", priority: 4, due: extractDue(t) };
  if (has(["gym", "run", "workout", "yoga"])) return { category: "health", priority: 3, due: extractDue(t) };
  if (has(["resume", "interview", "leetcode", "career"])) return { category: "career", priority: 4, due: extractDue(t) };
  if (has(["buy", "grocery", "groceries", "errand", "renew", "pay"])) return { category: "errands", priority: 2, due: extractDue(t) };
  if (has(["show"])) return { category: "isolated", priority: 3 };
  return { category: "personal", priority: 3, due: extractDue(t) };
}
function extractDue(t: string): string | null {
  if (t.includes("tomorrow") && t.match(/\b\d{1,2}(?::\d{2})?\s?(am|pm)\b/)) return `tomorrow ${t.match(/\b\d{1,2}(?::\d{2})?\s?(am|pm)\b/)![0]}`;
  if (t.match(/\b\d{1,2}(?::\d{2})?\s?(am|pm)\b/)) return t.match(/\b\d{1,2}(?::\d{2})?\s?(am|pm)\b/)![0];
  if (t.includes("tomorrow")) return "tomorrow";
  return null;
}

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([
    { id: nextId++, text: "Finish API doc", category: "work", priority: 4, due: "17:30", createdAt: new Date().toISOString() },
    { id: nextId++, text: "Buy groceries", category: "errands", priority: 2, due: null, createdAt: new Date().toISOString() },
    { id: nextId++, text: "Gym at 7am", category: "health", priority: 3, due: "7:00am", createdAt: new Date().toISOString() },
  ]);
  const [isolated, setIsolated] = useState<Task | null>(null);
  const sessionId = useMemo(() => getOrCreateSessionId(), []);

  const onCommand = (cmd: string): string[] => {
    const lower = cmd.toLowerCase().trim();
    if (lower === "help") {
      return [
        "Commands:",
        "  add <text>           → create a task",
        "  show                 → show all tasks",
        "  clear                → clear the terminal",
        "Examples:",
        "  add meeting tomorrow at 2pm",
        "  add gym at 7am",
        "  show",
      ];
    }
    if (lower.startsWith("add ")) {
      const text = cmd.slice(4).trim();
      const meta = mockCategorize(text);
      if (meta.category === "isolated") return ["Could not categorize. Try again."];
      const t: Task = { id: nextId++, text, category: meta.category, priority: meta.priority, due: meta.due || null, createdAt: new Date().toISOString() };
      setTasks((p) => [t, ...p]);
      setIsolated(meta.category === "personal" && !meta.due ? t : null);
      return [`✅ Added to ${t.category[0].toUpperCase() + t.category.slice(1)} — ${t.due ? `due ${t.due}, ` : ""}priority ${t.priority}`];
    }
    if (lower === "show" || lower.startsWith("show ")) {
      setIsolated(null);
      return [`📋 Showing tasks for session ${sessionId.slice(0, 8)}…`];
    }
    const meta = mockCategorize(cmd);
    if (meta.category === "isolated") { setIsolated(null); return ["Showing tasks…"]; }
    const t: Task = { id: nextId++, text: cmd, category: meta.category, priority: meta.priority, due: meta.due || null, createdAt: new Date().toISOString() };
    setTasks((p) => [t, ...p]);
    setIsolated(meta.category === "personal" && !meta.due ? t : null);
    return [`✅ Added to ${t.category[0].toUpperCase() + t.category.slice(1)} — ${t.due ? `due ${t.due}, ` : ""}priority ${t.priority}`];
  };

  return (
    <div className="h-screen w-screen bg-[linear-gradient(180deg,#0b1020,#0b0f1a)]">
      <div className="h-full w-full flex">
        {/* Left: terminal */}
        <div className="w-1/2 h-full flex">
          <TerminalWindow>
            <Terminal onCommand={onCommand} />
          </TerminalWindow>
        </div>
        {/* Right: task board */}
<div className="w-1/2 h-full bg-slate-50">
  <TaskBoard tasks={tasks} isolatedTask={isolated} />
</div>
      </div>
    </div>
  );
};

export default App;