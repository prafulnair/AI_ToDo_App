import React from "react";

const WindowButtons: React.FC = () => {
  return (
    <div className="flex space-x-2 ml-2">
      <span className="w-3 h-3 bg-red-500 rounded-full border border-black/20"></span>
      <span className="w-3 h-3 bg-yellow-400 rounded-full border border-black/20"></span>
      <span className="w-3 h-3 bg-green-500 rounded-full border border-black/20"></span>
    </div>
  );
};

export default WindowButtons;