import { useState, useEffect } from "react";
import InnerEarDiagnostic from "./components/InnerEarDiagnostic";
import PreFlightChecklist from "./components/PreFlightChecklist";
import MissionMap from "./components/MissionMap";
import ExecutionPipeline from "./components/ExecutionPipeline";
import { ShieldCheck, RadioTower } from "lucide-react";

export default function App() {
  const [isArmed, setIsArmed] = useState(false);
  const [flightTime, setFlightTime] = useState(0);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isArmed) {
      interval = setInterval(() => {
        setFlightTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isArmed]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 p-6 font-sans flex flex-col relative overflow-hidden">

      {/* Background Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-900/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-900/10 blur-[120px] pointer-events-none"></div>

      {/* Header */}
      <header className="flex justify-between items-center pb-6 mb-4 relative z-10 w-full">
        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-emerald-500/0 via-emerald-500/50 to-emerald-500/0"></div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <ShieldCheck className="text-emerald-400 w-10 h-10 drop-shadow-[0_0_15px_rgba(52,211,153,0.5)]" />
            {isArmed && <div className="absolute -top-1 -right-1 w-3 h-3 bg-rose-500 rounded-full animate-ping"></div>}
          </div>
          <div className="flex flex-col">
            <h1 className="text-3xl font-black tracking-widest text-white uppercase drop-shadow-md">
              Athena <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Command</span>
            </h1>
            <span className="text-xs text-slate-400 font-mono tracking-[0.2em] uppercase">V5 Golden // Fortress Architecture</span>
          </div>
        </div>

        <div className="flex gap-8 items-center bg-slate-900/50 backdrop-blur-xl border border-slate-700/50 px-6 py-3 rounded-2xl shadow-lg">
          <div className="flex flex-col items-center">
            <RadioTower className="w-5 h-5 text-emerald-400 mb-1 drop-shadow-[0_0_8px_rgba(52,211,153,0.6)]" />
            <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">DDS Link</span>
          </div>
          <div className="w-[1px] h-10 bg-slate-700/50"></div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-bold mb-1">Mission Time</span>
            <span className="text-3xl font-mono text-emerald-400 font-bold tracking-widest drop-shadow-[0_0_10px_rgba(52,211,153,0.5)] leading-none">{formatTime(flightTime)}</span>
          </div>
        </div>
      </header>

      {/* 4 Quadrant Grid layout */}
      <main className="grid grid-cols-12 gap-6 flex-grow relative z-10 h-[calc(100vh-140px)]">

        {/* Left Column (Quadrants 1 & 2) */}
        <div className="col-span-3 flex flex-col gap-6 h-full">
          <div className="h-[55%] glass-panel rounded-2xl p-5 flex flex-col relative overflow-hidden group">
            <InnerEarDiagnostic />
          </div>
          <div className="h-[45%] glass-panel rounded-2xl p-5 flex flex-col relative overflow-hidden">
            <PreFlightChecklist onArm={() => setIsArmed(true)} isArmed={isArmed} />
          </div>
        </div>

        {/* Middle Column (Quadrant 3 - Map) */}
        <div className="col-span-6 glass-panel rounded-2xl overflow-hidden flex flex-col relative shadow-[0_0_40px_rgba(0,0,0,0.5)] border-slate-600/50 h-full">
          <MissionMap isArmed={isArmed} />
        </div>

        {/* Right Column (Quadrant 4 - Pipeline/Tactics) */}
        <div className="col-span-3 flex flex-col gap-6 h-full">
          <div className="h-full glass-panel rounded-2xl p-5 flex flex-col relative overflow-hidden">
            <ExecutionPipeline isArmed={isArmed} />
          </div>
        </div>

      </main>
    </div>
  );
}
