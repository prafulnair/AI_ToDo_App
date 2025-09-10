import React, { useState, useRef } from "react";

interface Props {
  onSubmit: (input: string) => void;
}

const SearchBar: React.FC<Props> = ({ onSubmit }) => {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const v = value.trim();
    if (!v) return;
    onSubmit(v);
    setValue("");
    ref.current?.blur();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div
        className="
          relative flex items-center
          h-12 w-full
          rounded-full
          bg-neutral-800 border border-neutral-700
          focus-within:ring-2 focus-within:ring-blue-500
          transition-all
        "
      >
        <input
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Type anything… e.g. “Coffee with Brian at 5”"
          className="
            w-full h-full rounded-full
            bg-transparent outline-none
            px-4 pr-12 text-sm text-neutral-100
            placeholder:text-neutral-400
          "
        />
        <button
          type="submit"
          aria-label="Submit"
          className="
            absolute right-1.5 h-9 w-9
            rounded-full bg-blue-600 hover:bg-blue-700
            text-white text-sm grid place-items-center
            transition
          "
        >
          ↵
        </button>
      </div>
      <p className="mt-2 text-xs text-neutral-400">
        Try: <span className="text-neutral-300">“Add Monica’s meeting today at 4”</span> · <span className="text-neutral-300">“Show my meetings today”</span> · <span className="text-neutral-300">“Delete task id 4”</span>
      </p>
    </form>
  );
};

export default SearchBar;