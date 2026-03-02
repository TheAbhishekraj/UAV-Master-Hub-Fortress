import { Map as MapIcon, Navigation, Target } from "lucide-react";

interface MissionMapProps {
    isArmed: boolean;
}

export default function MissionMap({ isArmed }: MissionMapProps) {
    return (
        <>
            <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-start z-10 bg-gradient-to-b from-slate-950/90 via-slate-900/50 to-transparent pointer-events-none h-32">
                <div className="flex items-center gap-3">
                    <MapIcon className="text-cyan-400 w-6 h-6 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
                    <h2 className="uppercase tracking-[0.2em] text-sm font-bold text-slate-100">Tactical Map (A*)</h2>
                </div>

                <div className="flex flex-col items-end gap-2">
                    <div className="bg-slate-900/80 backdrop-blur-xl px-4 py-2 rounded-lg border border-rose-500/30 flex items-center gap-3 pointer-events-auto shadow-[0_4px_20px_rgba(225,29,72,0.15)]">
                        <div className="relative flex items-center justify-center w-3 h-3">
                            <div className="absolute w-full h-full rounded-full bg-rose-500 animate-ping opacity-75"></div>
                            <div className="relative w-1.5 h-1.5 rounded-full bg-rose-400 shadow-[0_0_5px_rgba(244,63,94,1)]"></div>
                        </div>
                        <span className="text-[10px] uppercase font-bold text-rose-100 tracking-wider">Phase 2 Isolate</span>
                    </div>

                    <div className="bg-slate-900/80 backdrop-blur-xl px-4 py-2 rounded-lg border border-emerald-500/30 flex items-center gap-3 pointer-events-auto shadow-[0_4px_20px_rgba(16,185,129,0.15)] group cursor-crosshair hover:bg-emerald-950/30 transition-colors">
                        <Target className="w-4 h-4 text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.8)]" />
                        <span className="text-xs text-emerald-400 font-mono font-bold neon-text-emerald">45.241°N, 12.834°E</span>
                    </div>
                </div>
            </div>

            {/* Map Background with Deep Gradients */}
            <div className="w-full h-full relative overflow-hidden bg-slate-950 flex items-center justify-center">

                {/* Core Glowing Orb behind map */}
                <div className="absolute w-[80%] h-[80%] bg-blue-900/20 rounded-full blur-[100px]"></div>

                {/* High-Tech Grid pattern */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]">
                    {/* Finer sub-grid */}
                    <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:10px_10px]"></div>
                </div>

                {/* Radar Sweep Effect */}
                <div className="absolute inset-x-0 top-0 h-[20%] bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent -translate-y-full animate-scanline pointer-events-none z-20"></div>

                {/* Vector SVG Overlays */}
                <svg className="absolute inset-0 w-full h-full opacity-80" viewBox="0 0 100 100" preserveAspectRatio="none">

                    {/* Geo-fence Area */}
                    <rect x="15" y="15" width="70" height="70" fill="rgba(16, 185, 129, 0.02)" stroke="rgba(16, 185, 129, 0.3)" strokeWidth="0.2" strokeDasharray="1 1" />

                    {/* A* Flight Path - Muted Base */}
                    <polyline
                        points="15,20 85,20 15,30 85,30 15,40 85,40 15,50 60,50"
                        fill="none"
                        stroke="rgba(34, 211, 238, 0.2)"
                        strokeWidth="0.5"
                    />

                    {/* Active Flight Path - Bright & Dashed */}
                    {isArmed && (
                        <line x1="15" y1="50" x2="60" y2="50" stroke="rgba(34, 211, 238, 0.9)" strokeWidth="0.8" strokeDasharray="3 1.5" className="animate-[dash_1.5s_linear_infinite]" />
                    )}
                </svg>

                {/* Thermal Hit Markers (Anomalies) */}
                <div className="absolute top-[39%] left-[30%]">
                    <div className="w-6 h-6 bg-rose-500/10 rounded-full animate-ping absolute -translate-x-1/2 -translate-y-1/2"></div>
                    <div className="w-2 h-2 bg-gradient-to-br from-rose-400 to-rose-600 rounded-full cursor-pointer hover:scale-[2] transition-transform shadow-[0_0_15px_rgba(244,63,94,1)] relative z-20 border border-rose-300"></div>
                    <div className="absolute top-3 -left-4 text-[8px] font-mono text-rose-400 uppercase drop-shadow-md">T-Anom</div>
                </div>

                <div className="absolute top-[29%] left-[65%]">
                    <div className="w-6 h-6 bg-amber-500/10 rounded-full animate-ping absolute -translate-x-1/2 -translate-y-1/2"></div>
                    <div className="w-2 h-2 bg-gradient-to-br from-amber-400 to-amber-600 rounded-full cursor-pointer hover:scale-[2] transition-transform shadow-[0_0_15px_rgba(245,158,11,1)] relative z-20 border border-amber-300"></div>
                </div>

                {/* GPS Denied VIO Bubble */}
                <div className="absolute top-[49%] left-[58%] w-40 h-40 bg-rose-500/5 rounded-full border border-rose-500/30 flex items-center justify-center z-10 pointer-events-none shadow-[inset_0_0_30px_rgba(225,29,72,0.1)] backdrop-blur-[1px]">
                    <span className="absolute -top-5 text-[9px] font-mono text-rose-400 uppercase tracking-widest font-bold">Max Drift: 0.92%</span>
                </div>

                {/* Drone Icon & Vectors */}
                <div className="absolute top-[50%] left-[60%] -translate-x-1/2 -translate-y-1/2 z-30 filter drop-shadow-[0_10px_15px_rgba(0,0,0,0.5)]">
                    <div className="relative group">
                        {/* Heading Vector Arc */}
                        <div className="absolute -top-8 left-1/2 -translate-x-1/2 w-16 h-16 border-t border-cyan-500/50 rounded-full opacity-50 rotate-90"></div>

                        {/* Drone glow */}
                        <div className="absolute inset-0 bg-emerald-400 blur-xl opacity-50 rounded-full scale-150"></div>

                        {/* Core Icon */}
                        <div className="relative w-10 h-10 bg-emerald-950 border border-emerald-500/50 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(52,211,153,0.4)]">
                            <Navigation className="text-emerald-400 fill-emerald-500 w-5 h-5 rotate-90" />
                        </div>
                    </div>
                </div>

                {/* Scale/Compass Legend Overlay */}
                <div className="absolute bottom-6 left-6 flex flex-col gap-1 z-20 pointer-events-none">
                    <div className="w-32 h-[1px] bg-slate-600 relative">
                        <div className="absolute left-0 -top-1 w-[1px] h-2.5 bg-slate-500"></div>
                        <div className="absolute right-0 -top-1 w-[1px] h-2.5 bg-slate-500"></div>
                        <div className="absolute left-1/2 -top-0.5 w-[1px] h-1.5 bg-slate-600"></div>
                    </div>
                    <span className="text-[9px] font-mono text-slate-500 font-bold tracking-widest uppercase">100 Meters</span>
                </div>

            </div>
        </>
    );
}
