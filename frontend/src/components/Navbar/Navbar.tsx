// src/components/Navbar/Navbar.tsx
import React from "react";

interface NavbarProps {
  onToggleSidebar: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onToggleSidebar }) => {
  return (
    <div
      className="w-full h-20 border-b-2 border-black bg-white 
                 flex items-center justify-between px-4"
    >
      {/* Left: Branding + Toggle Button */}
      <div className="flex items-center space-x-3">
        {/* Sidebar toggle button */}
        <button
          onClick={onToggleSidebar}
          className="border-black border-2 rounded-md 
                     bg-[#B8FF9F] hover:bg-[#9dfc7c] active:bg-[#7df752] 
                     w-10 h-10 flex items-center justify-center"
        >
          {/* Gear-like Icon */}
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M15.31 21.03C15.21 21.71 14.59 22.25 13.85 22.25H10.15C9.40999 22.25 8.78999 21.71 8.69999 20.98L8.42999 19.09C8.15999 18.95 7.89999 18.8 7.63999 18.63L5.83999 19.35C5.13999 19.61 4.36999 19.32 4.02999 18.7L2.19999 15.53C1.84999 14.87 1.99999 14.09 2.55999 13.65L4.08999 12.46C4.07999 12.31 4.06999 12.16 4.06999 12C4.06999 11.85 4.07999 11.69 4.08999 11.54L2.56999 10.35C1.97999 9.9 1.82999 9.09 2.19999 8.47L4.04999 5.28C4.38999 4.66 5.15999 4.38 5.83999 4.65L7.64999 5.38C7.90999 5.21 8.16999 5.06 8.42999 4.92L8.69999 3.01C8.78999 2.31 9.40999 1.76 10.14 1.76H13.84C14.58 1.76 15.2 2.3 15.29 3.03L15.56 4.92C15.83 5.06 16.09 5.21 16.35 5.38L18.15 4.66C18.86 4.4 19.63 4.69 19.97 5.31L21.81 8.49C22.17 9.15 22.01 9.93 21.45 10.37L19.93 11.56C19.94 11.71 19.95 11.86 19.95 12.02C19.95 12.18 19.94 12.33 19.93 12.48L21.45 13.67C22.01 14.12 22.17 14.9 21.82 15.53L19.96 18.75C19.62 19.37 18.85 19.65 18.16 19.38L16.36 18.66C16.1 18.83 15.84 18.98 15.58 19.12L15.31 21.03ZM12 15.5C13.933 15.5 15.5 13.933 15.5 12C15.5 10.067 13.933 8.5 12 8.5C10.067 8.5 8.49999 10.067 8.49999 12C8.49999 13.933 10.067 15.5 12 15.5Z"
              fill="black"
            />
          </svg>
        </button>

        <h1 className="font-bold text-lg">Momentum - Keep your work in motion</h1>
      </div>

      {/* Right: Links */}
      <div className="flex items-center space-x-4">
        <a href="#" className="text-sm font-medium hover:underline">
          About
        </a>
        <a href="#" className="text-sm font-medium hover:underline">
          Tech Stack
        </a>
      </div>
    </div>
  );
};

export default Navbar;