import { CheckSquare, Power, ShieldAlert, Cpu, Route, Lock } from "lucide-react";
import { useState } from "react";

interface PreFlightChecklistProps {
    onArm: () => void;
    isArmed: boolean;
}

export default function PreFlightChecklist({ onArm, isArmed }: PreFlightChecklistProps) {
    const [checking, setChecking] = useState(false);

    const handleArmClick = () => {
        if (isArmed) return;
        setChecking(true);
        setTimeout(() => {
            setChecking(false);
            onArm();
        }, 2000);
    };

    const CheckItem = ({ icon: Icon, label, status }: { icon: any, label: string, status: "pending" | "checking" | "ok" }) => (
        <div className={`flex items-center justify-between p-3 rounded-lg border transition-all duration-300
        ${status === 'ok' ? 'bg-emerald-950/20 border-emerald-900/50 shadow-[inset_0_0_10px_rgba(52,211,153,0.05)]' :
                status === 'checking' ? 'bg-amber-950/20 border-amber-900/50 shadow-[inset_0_0_10px_rgba(245,158,11,0.05)]' :
                    'bg-slate-900/40 border-slate-800'}`}>
            <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 
            ${status === 'ok' ? 'text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.8)]' :
                        status === 'checking' ? 'text-amber-400 drop-shadow-[0_0_5px_rgba(245,158,11,0.8)] animate-pulse' :
                            'text-slate-500'}`} />
                <span className={`text-[11px] uppercase font-bold tracking-widest 
             ${status === 'ok' ? 'text-slate-100' : 'text-slate-400'}`}>{label}</span>
            </div>
            <div className="font-mono text-[10px] font-bold pr-1">
                {status === 'pending' && <span className="text-slate-600">WAITING</span>}
                {status === 'checking' && <span className="text-amber-400 tracking-wider">VERIFYING</span>}
                {status === 'ok' && <span className="text-emerald-500 tracking-wider">SEALED</span>}
            </div>
        </div>
    );

    return (
        <>
            <div className="flex items-center gap-3 mb-5 pb-3">
                <CheckSquare className="text-amber-400 w-6 h-6 drop-shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
                <h2 className="uppercase tracking-[0.2em] text-sm font-bold text-slate-100">Auth Matrix</h2>
            </div>

            <div className="flex flex-col gap-3 flex-grow justify-center">
                <CheckItem icon={Power} label="Power Profile" status={isArmed ? "ok" : (checking ? "checking" : "pending")} />
                <CheckItem icon={Cpu} label="5-Layer Node Sync" status={isArmed ? "ok" : (checking ? "checking" : "pending")} />
                <CheckItem icon={ShieldAlert} label="Spoof Variance" status={isArmed ? "ok" : (checking ? "checking" : "pending")} />
                <CheckItem icon={Route} label="A* Geofence Bounds" status={isArmed ? "ok" : (checking ? "checking" : "pending")} />
            </div>

            <button
                onClick={handleArmClick}
                disabled={isArmed || checking}
                className={`mt-6 w-full py-4 rounded-xl font-black tracking-[0.2em] text-sm uppercase transition-all duration-500 relative overflow-hidden flex items-center justify-center gap-3
          ${isArmed
                        ? 'bg-emerald-950/40 text-emerald-500 border border-emerald-900 cursor-default shadow-[inset_0_0_20px_rgba(16,185,129,0.1)]'
                        : checking
                            ? 'bg-amber-600 text-white border-none scale-[0.98]'
                            : 'bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white shadow-[0_0_25px_rgba(245,158,11,0.4)] hover:shadow-[0_0_35px_rgba(245,158,11,0.6)] hover:-translate-y-0.5 border border-amber-400/50'
                    }`}
            >
                {isArmed ? (
                    <>
                        <Lock className="w-5 h-5" />
                        System Armed
                    </>
                ) : (
                    checking ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            Processing...
                        </>
                    ) : 'Authorize Liftoff'
                )}
            </button>
        </>
    );
}
