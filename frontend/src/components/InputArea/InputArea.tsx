// src/components/InputArea/InputArea.tsx
import { useState } from "react";

interface InputAreaProps {
  onTaskSubmit: (text: string) => void;
  onSummarizeToday?: () => void;
  onSummarizeWeek?: () => void;
}

const InputArea: React.FC<InputAreaProps> = ({
  onTaskSubmit,
  onSummarizeToday,
  onSummarizeWeek,
}) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = input.trim();
    if (!text) return;
    onTaskSubmit(text);
    setInput("");
  };

  return (
    <div className="w-full max-w-xl px-4">
      <div className="w-full border-black border-2 rounded-md bg-white hover:shadow-[8px_8px_0px_rgba(0,0,0,1)] transition-shadow">
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Input row */}
          <div className="flex items-start gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder='Type your task… (e.g., "call mom at 6", "summarize today")'
              rows={3}
              className="flex-1 w-full min-h-[72px] resize-y border-black border-2 p-2.5
                         focus:outline-none focus:shadow-[2px_2px_0px_rgba(0,0,0,1)]
                         focus:bg-[#FFA6F6] rounded-md"
            />
            {/* Pink round + button */}
            <button
              type="submit"
              aria-label="Add task"
              onClick={() => handleSubmit()}
              className="border-black border-2 rounded-full bg-[#FFA6F6]
                         hover:bg-[#fa8cef] active:bg-[#f774ea]
                         w-12 h-12 flex items-center justify-center shrink-0"
            >
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M10.8425 24V0H13.1575V24H10.8425ZM0 13.1664V10.8336H24V13.1664H0Z"
                  fill="black"
                />
              </svg>
            </button>
          </div>

          {/* Summarize actions */}
          {(onSummarizeToday || onSummarizeWeek) && (
            <div className="flex items-center gap-3 pt-1">
              {onSummarizeToday && (
                <button
                  type="button"
                  onClick={onSummarizeToday}
                  className="h-10 px-4 border-black border-2 bg-[#A6FAFF]
                             hover:bg-[#79F7FF] hover:shadow-[2px_2px_0px_rgba(0,0,0,1)]
                             active:bg-[#00E1EF] rounded-md font-semibold"
                >
                  Summarize Today
                </button>
              )}
              {onSummarizeWeek && (
                <button
                  type="button"
                  onClick={onSummarizeWeek}
                  className="h-10 px-4 border-black border-2 bg-[#A6FAFF]
                             hover:bg-[#79F7FF] hover:shadow-[2px_2px_0px_rgba(0,0,0,1)]
                             active:bg-[#00E1EF] rounded-md font-semibold"
                >
                  Summarize Week
                </button>
              )}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default InputArea;