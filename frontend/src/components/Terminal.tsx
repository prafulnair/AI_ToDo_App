import React, { useEffect, useRef, useState } from "react";

type Line = { kind: "input" | "output" | "banner"; text: string };

export const Terminal: React.FC<{ onCommand: (cmd: string) => string[] }> = ({ onCommand }) => {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [lines, setLines] = useState<Line[]>([]);
  const [buf, setBuf] = useState("");
  const [hist, setHist] = useState<string[]>([]);
  const [idx, setIdx] = useState(-1);

  useEffect(() => {
    hostRef.current?.focus();
    const now = new Date();
    const banner =
`   ______                  _      _______         _         
  / ___/____ ___  ____ _ (_)____/ / ___/______ (_)___ _    
  \\__ \\/ __ \`__ \\/ __ \`// // __  /\\__ \\/ ___/ / / __ \`/    
 ___/ / / / / / / /_/ // // /_/ /___/ / /__/ / / /_/ /     
/____/_/ /_/ /_/\\__,_//_/ \\__,_//____/\\___/_/ /\\__,_/  `;
    setLines([
      { kind: "banner", text: banner },
      { kind: "output", text: `Last login: ${now.toDateString()} ${now.toLocaleTimeString()}` },
    ]);
  }, []);

  useEffect(() => { hostRef.current?.scrollTo({ top: hostRef.current.scrollHeight }); }, [lines]);

  const Prompt = ({ text }: { text: string }) => (
    <div className="whitespace-pre-wrap">
      <span className="text-emerald-400">➜</span>{" "}
      <span className="text-sky-400">~</span>{" "}
      <span className="text-zinc-100">{text}</span>
    </div>
  );

  const onKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const k = e.key;

    if (k === "ArrowUp") { e.preventDefault(); if (hist.length) { const i = idx < 0 ? hist.length - 1 : Math.max(0, idx - 1); setIdx(i); setBuf(hist[i] ?? ""); } return; }
    if (k === "ArrowDown") { e.preventDefault(); if (hist.length) { const i = idx < hist.length - 1 ? idx + 1 : -1; setIdx(i); setBuf(i === -1 ? "" : (hist[i] ?? "")); } return; }
    if (k === "Backspace") { e.preventDefault(); setBuf((b) => b.slice(0, -1)); return; }
    if (k === "Enter") {
      e.preventDefault();
      const cmd = buf.trim();
      const batch: Line[] = [];
      batch.push({ kind: "input", text: cmd });

      if (cmd.toLowerCase() === "clear") {
        setLines([]);
        setBuf("");
        setIdx(-1);
        setHist((h) => (cmd ? [...h, cmd] : h));
        return;
      }
      const outs = onCommand(cmd);
      outs.forEach((t) => batch.push({ kind: "output", text: t }));

      setLines((prev) => [...prev, ...batch]);
      setHist((h) => (cmd ? [...h, cmd] : h));
      setIdx(-1);
      setBuf("");
      return;
    }

    if (k.length === 1) { e.preventDefault(); setBuf((b) => b + k); return; }
    if (k === " ") { e.preventDefault(); setBuf((b) => b + " "); return; }
    if (k === "Tab") { e.preventDefault(); setBuf((b) => b + "  "); return; }
  };

  return (
    <div
      ref={hostRef}
      tabIndex={0}
      onKeyDown={onKey}
      className="w-full h-full overflow-y-auto px-4 py-3 scroll-snap"
      aria-label="interactive terminal"
    >
      {lines.map((l, i) => (
        <div key={i} className="mb-1">
          {l.kind === "banner" ? (
            <pre className="text-[11px] leading-4 text-zinc-400">{l.text}</pre>
          ) : l.kind === "input" ? (
            <Prompt text={l.text} />
          ) : (
            <div className="text-zinc-300">{l.text}</div>
          )}
        </div>
      ))}
      <div className="relative">
        <Prompt text={buf} />
        <span className="blink absolute left-[2.25rem] -translate-y-1.5 top-1/2 inline-block w-2 h-5 bg-zinc-200" />
      </div>
    </div>
  );
};