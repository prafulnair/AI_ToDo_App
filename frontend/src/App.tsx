// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <div>
//         <a href="https://vite.dev" target="_blank">
//           <img src={viteLogo} className="logo" alt="Vite logo" />
//         </a>
//         <a href="https://react.dev" target="_blank">
//           <img src={reactLogo} className="logo react" alt="React logo" />
//         </a>
//       </div>
//       <h1>Vite + React</h1>
//       <div className="card">
//         <button onClick={() => setCount((count) => count + 1)}>
//           count is {count}
//         </button>
//         <p>
//           Edit <code>src/App.tsx</code> and save to test HMR
//         </p>
//       </div>
//       <p className="read-the-docs">
//         Click on the Vite and React logos to learn more
//       </p>
//     </>
//   )
// }

// export default App
// src/App.tsx
import React, { useState } from "react";

function App() {
  const [response, setResponse] = useState<string>("");

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setResponse("✅ Added to Work — due tomorrow 2pm, priority 4"); // mock AI response
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Left column: Assistant input */}
      <div className="w-1/3 border-r border-gray-200 p-6 flex flex-col">
        <h1 className="text-2xl font-bold mb-6">Smart AI Task Manager</h1>

        <form onSubmit={handleSubmit} className="flex mb-4">
          <input
            type="text"
            placeholder="Type a task..."
            className="flex-1 px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700"
          >
            Add
          </button>
        </form>

        {response && (
          <div className="bg-green-50 border border-green-300 text-green-800 px-3 py-2 rounded-md text-sm">
            {response}
          </div>
        )}
      </div>

      {/* Right column: Task Board */}
      <div className="flex-1 p-6 grid grid-cols-3 gap-4">
        <div className="bg-white shadow rounded-lg p-4">
          <h2 className="font-semibold text-lg mb-2">Work</h2>
          <ul className="space-y-2 text-sm">
            <li className="border rounded px-2 py-1">Finish API doc</li>
          </ul>
        </div>

        <div className="bg-white shadow rounded-lg p-4">
          <h2 className="font-semibold text-lg mb-2">Personal</h2>
          <ul className="space-y-2 text-sm">
            <li className="border rounded px-2 py-1">Buy groceries</li>
          </ul>
        </div>

        <div className="bg-white shadow rounded-lg p-4">
          <h2 className="font-semibold text-lg mb-2">Health</h2>
          <ul className="space-y-2 text-sm">
            <li className="border rounded px-2 py-1">Gym at 7am</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;