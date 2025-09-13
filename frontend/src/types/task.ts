// src/types/task.ts

// A single task item from backend
export interface Task {
  id: number;               // backend uses integer primary key
  text: string;             // task description
  category?: string;        // e.g. "Work", "Health"
  priority?: number;        // 1–5 (optional for now)
  due_dt?: string | null;   // ISO string from backend, or null
  status: "open" | "done";  // backend status
  created_at: string;       // ISO string from backend
}

// Category grouping for UI
export interface Category {
  name: string;
  tasks: Task[];
}