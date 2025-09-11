export type Category = 'work' | 'career' | 'health' | 'errands' | 'personal';

export interface Task {
  id: number;
  text: string;
  category: Category | 'isolated';
  priority: number;        // 1..5
  due?: string | null;     // ISO string or null
  createdAt: string;       // ISO
}