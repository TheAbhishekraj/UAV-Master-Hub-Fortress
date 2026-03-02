import { Activity, Compass, Cpu, LocateFixed } from "lucide-react";

export default function InnerEarDiagnostic() {
    return (
        <>
            <div className="absolute -right-10 -top-10 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all duration-700"></div>

            <div className="flex items-center gap-3 mb-5 pb-3">
                <Activity className="text-emerald-400 w-6 h-6 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                <h2 className="uppercase tracking-[0.2em] text-sm font-bold text-slate-100">Inner Ear</h2>
            </div>

            <div className="flex-grow flex flex-col gap-5 justify-between">

                {/* Z-Variance Gage */}
                <div className="glass-card rounded-xl p-4 relative overflow-hidden group-hover:border-emerald-500/30 transition-colors duration-500">
                    <div className="flex justify-between items-center mb-3">
                        <span className="text-[11px] text-slate-300 font-bold tracking-widest uppercase">Z-Variance (Pos)</span>
                        <span className="font-mono text-emerald-400 text-lg font-black drop-shadow-[0_0_5px_rgba(52,211,153,0.8)]">0.02m</span>
                    </div>
                    <div className="h-2.5 w-full bg-slate-900/80 rounded-full overflow-hidden flex shadow-inner border border-slate-800/80">
                        <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 w-1/4 shadow-[0_0_10px_rgba(52,211,153,0.8)] relative">
                            <div className="absolute right-0 top-0 bottom-0 w-1 bg-white/50"></div>
                        </div>
                    </div>
                    <div className="mt-2 flex justify-between text-[10px] text-slate-500 font-mono font-semibold">
                        <span>0.0</span>
                        <span>0.05 (GOLD)</span>
                        <span>0.20</span>
                    </div>
                </div>

                {/* Multi-Sensor Lock Status */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="glass-card p-3 rounded-xl flex flex-col items-center justify-center text-center relative overflow-hidden group-hover:border-cyan-500/30 transition-colors">
                        <div className="absolute inset-x-0 bottom-0 h-1 bg-emerald-500 shadow-[0_0_10px_rgba(52,211,153,0.8)]"></div>
                        <LocateFixed className="w-5 h-5 text-slate-300 mb-2 opacity-80" />
                        <span className="text-emerald-400 font-mono font-black text-xl mb-1 neon-text-emerald">3DFIX</span>
                        <span className="text-[9px] uppercase tracking-widest text-slate-400 font-bold">GNSS • <span className="text-slate-200">14 Sats</span></span>
                    </div>

                    <div className="glass-card p-3 rounded-xl flex flex-col items-center justify-center text-center relative overflow-hidden group-hover:border-cyan-500/30 transition-colors">
                        <div className="absolute inset-x-0 bottom-0 h-1 bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></div>
                        <Compass className="w-5 h-5 text-slate-300 mb-2 opacity-80" />
                        <span className="text-cyan-400 font-mono font-black text-xl mb-1 neon-text-cyan">LOCKED</span>
                        <span className="text-[9px] uppercase tracking-widest text-slate-400 font-bold">VIO • <span className="text-slate-200">184 Feat</span></span>
                    </div>
                </div>

                {/* IMU Bias */}
                <div className="glass-card rounded-xl p-4 flex-grow flex flex-col justify-center relative cursor-crosshair">
                    <div className="flex justify-between items-center w-full absolute top-3 left-0 px-4">
                        <span className="flex items-center gap-1.5 text-[10px] text-slate-300 uppercase tracking-widest font-bold">
                            <Cpu className="w-3.5 h-3.5 text-fuchsia-400" /> ES-EKF Core
                        </span>
                        <div className="px-2 py-0.5 rounded bg-fuchsia-500/10 border border-fuchsia-500/30">
                            <span className="text-fuchsia-400 font-mono text-[10px] font-bold shadow-fuchsia-400 drop-shadow-md">400Hz</span>
                        </div>
                    </div>

                    <div className="flex justify-between items-end mt-8 relative z-10">
                        <div className="flex flex-col">
                            <span className="text-[9px] text-slate-400 uppercase tracking-widest font-bold mb-1">Accel Bias</span>
                            <span className="font-mono text-slate-200 text-[11px] bg-slate-900/80 px-2 py-1 rounded border border-slate-700">[ 0.01, -0.02, 0.00 ]</span>
                        </div>
                        <div className="flex flex-col text-right">
                            <span className="text-[9px] text-slate-400 uppercase tracking-widest font-bold mb-1">Gyro Bias</span>
                            <span className="font-mono text-slate-200 text-[11px] bg-slate-900/80 px-2 py-1 rounded border border-slate-700">[ 0.00, 0.01, 0.00 ]</span>
                        </div>
                    </div>

                    {/* Animated Sparklines */}
                    <div className="absolute inset-x-0 bottom-2 h-10 overflow-hidden opacity-40">
                        <svg className="w-full h-full absolute animate-[shimmer_5s_linear_infinite]" preserveAspectRatio="none" viewBox="0 0 100 20">
                            <path d="M0 10 Q 10 2, 20 15 T 40 8 T 60 16 T 80 5 T 100 10" fill="transparent" stroke="rgb(16 185 129)" strokeWidth="0.8" />
                            <path d="M0 15 Q 15 15, 30 5 T 50 12 T 70 8 T 90 14 T 100 12" fill="transparent" stroke="rgb(192 38 211)" strokeWidth="0.5" strokeDasharray="2 1" />
                        </svg>
                    </div>
                </div>
            </div>
        </>
    );
}
