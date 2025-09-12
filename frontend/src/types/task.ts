// A single task item
export interface Task {
  id: string;                // unique identifier
  title: string;             // e.g. "Meeting with Stephanie at 4"
  category?: string;         // e.g. "Work", "Health" (optional if uncategorized)
  isDone: boolean;           // whether the task is marked done
  createdAt: Date;           // timestamp
}

// Category structure returned by AI
export interface Category {
  name: string;              // e.g. "Work"
  tasks: Task[];             // tasks belonging to this category
}