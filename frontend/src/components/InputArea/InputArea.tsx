import { useState } from "react";
import { Textarea, Button, Toast } from "flowbite-react";

interface InputAreaProps {
  onTaskSubmit: (text: string) => void;
}

const InputArea: React.FC<InputAreaProps> = ({ onTaskSubmit }) => {
  const [input, setInput] = useState("");
  const [feedback, setFeedback] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    onTaskSubmit(input.trim());

    setFeedback("✅ Task added successfully!");
    setInput("");

    setTimeout(() => setFeedback(""), 2000);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-2">
        <Textarea
          placeholder="Type your task in natural language..."
          rows={3}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="resize-none"
        />
        <Button type="submit" className="w-full">
          Add Task
        </Button>
      </form>

      {/* Feedback message (Toast) */}
      {feedback && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2">
          <Toast>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {feedback}
            </div>
          </Toast>
        </div>
      )}
    </div>
  );
};

export default InputArea;