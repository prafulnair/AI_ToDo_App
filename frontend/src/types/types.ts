export type Category = "work" | "personal" | "health" | "career" | "errand";

export interface Task {
  id: number;
  text: string;
  category: Category;
  priority: 1 | 2 | 3 | 4 | 5;
  due_dt?: string | null; // ISO string
  status: "open" | "done";
  created_at: string; // ISO
}