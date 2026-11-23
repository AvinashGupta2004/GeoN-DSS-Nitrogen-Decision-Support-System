import React from 'react';
import { ShieldCheck, ShieldAlert, CloudRain, Flame, Info } from 'lucide-react';

export default function DecisionCard({ result }) {
  if (!result) return null;

  const isGo    = result.status === 'GO';
  const isLeach = result.window_class === 0;
  // window_class === 1 → burn risk

  // User-friendly plain English titles
  const title = isGo
    ? '✅ Safe to Apply Nitrogen'
    : isLeach
    ? '🚫 Not Safe — Rain Risk Detected'
    : '🚫 Not Safe — Heat / Burn Risk Detected';

  const badge = isGo ? 'APPLY NOW' : 'WAIT — DO NOT APPLY';

  // Strip internal prefix tags like "[ALERT]" from alert_message
  const alertMsg = (result.alert_message || '').replace(/^\[.*?\]\s*/i, '');

  return (
    <div
      className={`rounded-2xl p-4 sm:p-5 border transition-all ${
        isGo
          ? 'bg-emerald-50/70 border-emerald-300 shadow-sm'
          : isLeach
          ? 'bg-rose-50/80 border-rose-300 shadow-sm'
          : 'bg-amber-50/80 border-amber-300 shadow-sm'
      }`}
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Icon + Title */}
        <div className="flex items-center gap-3">
          <div
            className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
              isGo
                ? 'bg-emerald-600 text-white'
                : isLeach
                ? 'bg-rose-600 text-white'
                : 'bg-amber-600 text-white'
            }`}
          >
            {isGo ? <ShieldCheck className="w-6 h-6" /> : isLeach ? <CloudRain className="w-6 h-6" /> : <Flame className="w-6 h-6" />}
          </div>

          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5">
              Decision  ·  {result.centroid_lat?.toFixed(3)}°N, {result.centroid_lon?.toFixed(3)}°E
            </div>
            <h3 className={`text-base sm:text-lg font-bold tracking-tight ${
              isGo ? 'text-emerald-950' : isLeach ? 'text-rose-950' : 'text-amber-950'
            }`}>
              {title}
            </h3>
          </div>
        </div>

        {/* Right badge */}
        <div className="sm:text-right shrink-0">
          <div className={`text-lg sm:text-xl font-black tracking-tight ${
            isGo ? 'text-emerald-700' : 'text-rose-700'
          }`}>
            {badge}
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            Field: <span className="font-semibold text-slate-700">{result.field_area_ha} ha</span>{' '}
            ({(result.field_area_ha * 2.471).toFixed(1)} acres)
          </div>
        </div>
      </div>

      {/* Advisory note */}
      <div className="mt-3 pt-3 border-t border-slate-200/60 text-xs sm:text-sm text-slate-700 leading-relaxed flex items-start gap-2">
        <Info className={`w-4 h-4 shrink-0 mt-0.5 ${isGo ? 'text-emerald-600' : isLeach ? 'text-rose-600' : 'text-amber-600'}`} />
        <span>{alertMsg}</span>
      </div>
    </div>
  );
}
