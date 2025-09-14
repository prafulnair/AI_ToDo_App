// src/components/SummaryPanel/SummaryPanel.tsx
import { Card, Badge, Button } from "flowbite-react";
import type { Task } from "../../types/task";

interface SummaryData {
  headline: string;
  kpis: { open: number; completed: number; overdue: number; due_today: number };
  highlights: string[];
  by_category: { name: string; open: number; done: number }[];
  urgent_ids: number[];
  overdue_ids: number[];
  markdown: string;
}

interface Props {
  summary: SummaryData;
  tasks: Task[];
  onClose: () => void;
  onTaskClick: (task: Task) => void;
}

const SummaryPanel: React.FC<Props> = ({ summary, tasks, onClose, onTaskClick }) => {
  const copyMarkdown = () => {
    navigator.clipboard.writeText(summary.markdown);
  };

  const findTask = (id: number) => tasks.find((t) => t.id === id);

  return (
    <Card className="max-w-2xl mx-auto shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">{summary.headline}</h3>
        <Button size="xs" color="light" onClick={onClose}>
          Close
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-2 text-center mb-4">
        <div><p className="text-sm">Open</p><p className="font-bold">{summary.kpis.open}</p></div>
        <div><p className="text-sm">Completed</p><p className="font-bold">{summary.kpis.completed}</p></div>
        <div><p className="text-sm">Overdue</p><p className="font-bold text-red-500">{summary.kpis.overdue}</p></div>
        <div><p className="text-sm">Due Today</p><p className="font-bold text-amber-500">{summary.kpis.due_today}</p></div>
      </div>

      {/* Highlights */}
      <div className="mb-4">
        <h4 className="font-semibold">Highlights</h4>
        <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300">
          {summary.highlights.map((h, idx) => <li key={idx}>{h}</li>)}
        </ul>
      </div>

      {/* Categories */}
      <div className="mb-4 flex flex-wrap gap-2">
        {summary.by_category.map((c) => (
          <Badge key={c.name} color="info">
            {c.name}: {c.open} open / {c.done} done
          </Badge>
        ))}
      </div>

      {/* Urgent & Overdue */}
      <div className="mb-4">
        {summary.urgent_ids.length > 0 && (
          <>
            <h4 className="font-semibold mb-1">Urgent</h4>
            <ul className="text-sm">
              {summary.urgent_ids.map((id) => {
                const t = findTask(id);
                return (
                  t && (
                    <li
                      key={id}
                      className="cursor-pointer hover:underline"
                      onClick={() => onTaskClick(t)}
                    >
                      {t.text}
                    </li>
                  )
                );
              })}
            </ul>
          </>
        )}
        {summary.overdue_ids.length > 0 && (
          <>
            <h4 className="font-semibold mt-2 mb-1">Overdue</h4>
            <ul className="text-sm text-red-500">
              {summary.overdue_ids.map((id) => {
                const t = findTask(id);
                return (
                  t && (
                    <li
                      key={id}
                      className="cursor-pointer hover:underline"
                      onClick={() => onTaskClick(t)}
                    >
                      {t.text}
                    </li>
                  )
                );
              })}
            </ul>
          </>
        )}
      </div>

      <div className="flex justify-end">
        <Button size="xs" onClick={copyMarkdown}>
          Copy Narrative
        </Button>
      </div>
    </Card>
  );
};

export default SummaryPanel;