import React, { useEffect, useRef, useState } from "react";

type Dir = "n" | "s" | "e" | "w" | "ne" | "nw" | "se" | "sw";

export const TerminalWindow: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [size, setSize] = useState({ width: 720, height: 420 });
  const [resizing, setResizing] = useState<{ dir: Dir | null; sx: number; sy: number; sw: number; sh: number }>({
    dir: null, sx: 0, sy: 0, sw: 720, sh: 420,
  });

  useEffect(() => {
    function onMove(e: MouseEvent) {
      if (!resizing.dir) return;
      const dx = e.clientX - resizing.sx;
      const dy = e.clientY - resizing.sy;
      const minW = 420, minH = 240;
      const maxW = Math.min(window.innerWidth * 0.9, 900);
      const maxH = Math.min(window.innerHeight * 0.5, 520);

      let w = resizing.sw, h = resizing.sh;
      if (resizing.dir.includes("e")) w = Math.min(Math.max(minW, resizing.sw + dx), maxW);
      if (resizing.dir.includes("w")) w = Math.min(Math.max(minW, resizing.sw - dx), maxW);
      if (resizing.dir.includes("s")) h = Math.min(Math.max(minH, resizing.sh + dy), maxH);
      if (resizing.dir.includes("n")) h = Math.min(Math.max(minH, resizing.sh - dy), maxH);

      setSize({ width: Math.round(w), height: Math.round(h) });
    }
    const onUp = () => setResizing((r) => ({ ...r, dir: null }));
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [resizing]);

  const start = (dir: Dir) => (e: React.MouseEvent) => {
    e.preventDefault();
    setResizing({ dir, sx: e.clientX, sy: e.clientY, sw: size.width, sh: size.height });
  };

  return (
    <div className="h-full w-full flex items-start justify-center p-8">
      <div
        className="relative rounded-2xl overflow-hidden border border-[rgba(255,255,255,0.1)] shadow-2xl"
        style={{ width: size.width, height: size.height, maxHeight: "50vh" }}
      >
        {/* Title bar */}
        <div className="h-10 bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-600 flex items-center px-3">
          <div className="flex items-center gap-2">
            <span className="h-3.5 w-3.5 rounded-full bg-[#ff5f56]" />
            <span className="h-3.5 w-3.5 rounded-full bg-[#ffbd2e]" />
            <span className="h-3.5 w-3.5 rounded-full bg-[#27c93f]" />
          </div>
          <div className="text-zinc-200 text-xs ml-3 tracking-wide">smart-todo — zsh</div>
        </div>

        {/* Terminal body */}
        <div className="absolute inset-x-0 bottom-0 top-10 bg-[#0d1117] text-zinc-200 font-mono text-[13px] leading-6">
          {children}
        </div>

        {/* Resize handles */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 h-3 w-14 cursor-ns-resize" onMouseDown={start("n")} />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-3 w-14 cursor-ns-resize" onMouseDown={start("s")} />
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-3 h-14 cursor-ew-resize" onMouseDown={start("w")} />
        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-14 cursor-ew-resize" onMouseDown={start("e")} />
        <div className="absolute top-0 left-0 w-3 h-3 cursor-nwse-resize" onMouseDown={start("nw")} />
        <div className="absolute top-0 right-0 w-3 h-3 cursor-nesw-resize" onMouseDown={start("ne")} />
        <div className="absolute bottom-0 left-0 w-3 h-3 cursor-nesw-resize" onMouseDown={start("sw")} />
        <div className="absolute bottom-0 right-0 w-3 h-3 cursor-nwse-resize" onMouseDown={start("se")} />
      </div>
    </div>
  );
};