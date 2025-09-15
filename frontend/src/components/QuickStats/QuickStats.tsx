import React from "react";
import ProgressBar from "../ProgressBar/ProgressBar";

type BarColor = "violet" | "pink" | "red" | "orange" | "yellow" | "lime" | "cyan";

interface QuickStatsProps {
  total: number;
  completed: number;
  pending: number;
}

const pickColor = (pct: number): BarColor => {
  if (pct === 0) return "red";
  if (pct < 40) return "orange";
  if (pct < 70) return "yellow";
  return "lime";
};

const QuickStats: React.FC<QuickStatsProps> = ({ total, completed, pending }) => {
  const pct = total > 0 ? (completed / total) * 100 : 0;
  const color = pickColor(pct);

  return (
    <div className="border-2 border-black rounded-md bg-white p-4 hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]">
      <h3 className="text-sm font-extrabold mb-3">Quick Stats</h3>

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="border-2 border-black rounded-md p-2 text-center">
          <div className="text-xs">Total</div>
          <div className="text-lg font-extrabold">{total}</div>
        </div>
        <div className="border-2 border-black rounded-md p-2 text-center">
          <div className="text-xs">Done</div>
          <div className="text-lg font-extrabold">{completed}</div>
        </div>
        <div className="border-2 border-black rounded-md p-2 text-center">
          <div className="text-xs">Open</div>
          <div className="text-lg font-extrabold">{pending}</div>
        </div>
      </div>

      <ProgressBar
        currentValue={completed}
        maxValue={total || 1}
        color={color}
        rounded="md"
      />
    </div>
  );
};

export default QuickStats;