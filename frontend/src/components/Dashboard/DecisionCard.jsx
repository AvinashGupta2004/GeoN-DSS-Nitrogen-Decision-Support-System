import React from 'react';
import { ShieldCheck, ShieldAlert, CloudRain, Flame, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function DecisionCard({ result }) {
  if (!result) return null;

  const isGo = result.status === 'GO';
  const isLeach = result.window_class === 0;
  const isBurn = result.window_class === 1;

  return (
    <div
      className={`rounded-2xl p-4 sm:p-5 border transition-all ${
        isGo
          ? 'bg-emerald-50/70 border-emerald-300 shadow-card'
          : isLeach
          ? 'bg-rose-50/80 border-rose-300 shadow-card'
          : 'bg-amber-50/80 border-amber-300 shadow-card'
      }`}
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 shadow-xs ${
              isGo
                ? 'bg-emerald-600 text-white'
                : isLeach
                ? 'bg-rose-600 text-white'
                : 'bg-amber-600 text-white'
            }`}
          >
            {isGo ? (
              <ShieldCheck className="w-6 h-6" />
            ) : isLeach ? (
              <CloudRain className="w-6 h-6" />
            ) : (
              <Flame className="w-6 h-6" />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className={`text-[10px] font-display font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                  isGo
                    ? 'bg-emerald-200/90 text-emerald-900'
                    : isLeach
                    ? 'bg-rose-200/90 text-rose-900'
                    : 'bg-amber-200/90 text-amber-900'
                }`}
              >
                Gatekeeper Decision: {result.status}
              </span>
              <span className="text-xs text-slate-500 font-sans font-medium">
                Centroid: {result.centroid_lat?.toFixed(3)}°N, {result.centroid_lon?.toFixed(3)}°E
              </span>
            </div>

            <h3
              className={`text-lg sm:text-xl font-display font-extrabold tracking-tight mt-0.5 ${
                isGo
                  ? 'text-emerald-950'
                  : isLeach
                  ? 'text-rose-950'
                  : 'text-amber-950'
              }`}
            >
              {isGo
                ? 'GO: Safe Nitrogen Application Window'
                : isLeach
                ? 'NO-GO: High Nitrogen Leaching Risk'
                : 'NO-GO: High Fertilizer Burn Risk'}
            </h3>
          </div>
        </div>

        {/* Status Badge */}
        <div className="sm:text-right shrink-0">
          <div
            className={`text-xl sm:text-2xl font-display font-black tracking-tight ${
              isGo
                ? 'text-emerald-700'
                : isLeach
                ? 'text-rose-700'
                : 'text-amber-700'
            }`}
          >
            {isGo ? 'UNLOCKED' : 'LOCKED'}
          </div>
          <div className="text-[11px] text-slate-500 font-sans">
            Area: <span className="font-semibold text-slate-700">{result.field_area_ha} ha</span> ({(result.field_area_ha * 2.471).toFixed(1)} acres)
          </div>
        </div>
      </div>

      {/* Advisory Message */}
      <div className="mt-3 pt-3 border-t border-slate-200/60 text-xs sm:text-sm text-slate-700 font-sans leading-relaxed flex items-start gap-2">
        <AlertTriangle
          className={`w-4 h-4 shrink-0 mt-0.5 ${
            isGo ? 'text-emerald-600' : isLeach ? 'text-rose-600' : 'text-amber-600'
          }`}
        />
        <span>{result.alert_message}</span>
      </div>
    </div>
  );
}
