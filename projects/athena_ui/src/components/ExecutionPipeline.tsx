import { Zap, RotateCcw, Crosshair, MapPin } from "lucide-react";

interface ExecutionPipelineProps {
    isArmed: boolean;
}

export default function ExecutionPipeline({ isArmed }: ExecutionPipelineProps) {
    const progressPercent = isArmed ? 45.8 : 0;

    return (
        <>
            <div className="absolute left-0 top-0 w-1.5 h-full bg-gradient-to-b from-transparent via-cyan-900/40 to-transparent"></div>

            <div className="flex items-center gap-3 mb-8 pb-3 relative">
                <Zap className="text-amber-400 w-6 h-6 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)] relative z-10" />
                <h2 className="uppercase tracking-[0.2em] text-sm font-bold text-slate-100">Execution</h2>
            </div>

            <div className="flex flex-col gap-8 flex-grow">

                {/* Master Progress */}
                <div className="flex flex-col gap-3">
                    <div className="flex justify-between items-center text-xs">
                        <span className="uppercase text-slate-400 font-bold tracking-[0.1em]">Mission Yield</span>
                        <span className="font-mono text-cyan-400 text-lg font-black drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]">{progressPercent.toFixed(1)}%</span>
                    </div>

                    {/* Tiered Progress Bar */}
                    <div className="relative h-4 w-full bg-slate-900/80 rounded-full overflow-hidden border border-slate-700 shadow-inner">
                        {/* Background glow */}
                        <div
                            className="absolute top-0 left-0 h-full bg-cyan-500 blur-sm opacity-50 transition-all duration-[2000ms] ease-out"
                            style={{ width: `${progressPercent}%` }}
                        ></div>

                        {/* Actual Bar */}
                        <div
                            className="relative h-full bg-gradient-to-r from-cyan-600 via-cyan-400 to-cyan-300 transition-all duration-[2000ms] ease-out border-r border-white/50"
                            style={{ width: `${progressPercent}%` }}
                        >
                            {/* Diagonal stripes overlay */}
                            <div className="absolute inset-0 bg-[repeating-linear-gradient(45deg,transparent,transparent_5px,rgba(255,255,255,0.1)_5px,rgba(255,255,255,0.1)_10px)] opacity-50"></div>
                        </div>
                    </div>

                    <div className="flex justify-between text-[10px] text-slate-500 font-mono font-bold uppercase tracking-widest mt-1">
                        <span>0 ha</span>
                        <span>2.0 ha (Total Bounds)</span>
                    </div>
                </div>

                {/* Tactical Data Cards */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="glass-card p-4 rounded-xl flex flex-col relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-16 h-16 bg-rose-500/10 rounded-bl-full transition-transform group-hover:scale-110"></div>
                        <Crosshair className="text-slate-400 w-5 h-5 mb-3" />
                        <span className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Anomalies</span>
                        <span className="text-3xl font-mono text-rose-400 font-black neon-text-cyan drop-shadow-[0_0_8px_rgba(244,63,94,0.6)]">14</span>
                    </div>

                    <div className="glass-card p-4 rounded-xl flex flex-col relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/10 rounded-bl-full transition-transform group-hover:scale-110"></div>
                        <MapPin className="text-slate-400 w-5 h-5 mb-3" />
                        <span className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">Waypoints</span>
                        <div className="flex items-baseline gap-1">
                            <span className="text-3xl font-mono text-blue-400 font-black drop-shadow-[0_0_8px_rgba(96,165,250,0.6)]">32</span>
                            <span className="text-sm font-mono text-slate-500 font-bold">/75</span>
                        </div>
                    </div>
                </div>

                {/* Command Actions */}
                <div className="mt-auto flex flex-col gap-4">
                    <button
                        disabled={!isArmed}
                        className={`w-full py-4 rounded-lg text-xs font-black uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all duration-300
                ${isArmed ? 'bg-slate-900 border border-slate-700 text-slate-200 hover:bg-slate-800 hover:border-slate-500 shadow-lg'
                                : 'bg-slate-950/40 text-slate-700 border border-slate-900 cursor-not-allowed'}`}
                    >
                        <RotateCcw className={`w-4 h-4 ${isArmed ? 'text-cyan-400' : ''}`} />
                        Regenerate Path
                    </button>

                    <button
                        disabled={!isArmed}
                        className={`w-full py-5 rounded-xl text-sm font-black uppercase tracking-[0.2em] flex items-center justify-center gap-3 transition-all duration-300 relative overflow-hidden group
                ${isArmed ? 'bg-gradient-to-br from-rose-700 to-rose-900 border border-rose-500 text-white shadow-[0_0_30px_rgba(225,29,72,0.4)] hover:shadow-[0_0_40px_rgba(225,29,72,0.6)] hover:-translate-y-1'
                                : 'bg-slate-900 text-slate-800 border-none cursor-not-allowed'}`}
                    >
                        {isArmed && (
                            <>
                                <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/50 to-transparent"></div>
                                <div className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-[150%] group-hover:animate-[shimmer_2s_infinite]"></div>
                            </>
                        )}
                        <Zap className={`w-6 h-6 ${isArmed ? 'animate-pulse drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]' : ''}`} />
                        "Zeus" Override
                    </button>
                </div>
            </div>
        </>
    );
}
