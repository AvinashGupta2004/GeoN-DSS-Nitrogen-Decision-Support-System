import React from 'react';
import { Package, Split, Info } from 'lucide-react';

export default function DosageCard({ result }) {
  if (!result || result.status !== 'GO' || !result.dosage_schedule) {
    return (
      <div className="bg-slate-50/80 rounded-2xl p-6 border border-dashed border-slate-300 text-center text-slate-400">
        <Package className="w-9 h-9 mx-auto mb-2 opacity-50" />
        <p className="text-sm font-bold text-slate-600">Dosage Locked</p>
        <p className="text-xs text-slate-400 mt-0.5">
          Nitrogen dosage will appear here once conditions are safe (GO status).
        </p>
      </div>
    );
  }

  const { dosage_schedule, recommended_N_kg_ha } = result;
  const ureaBags = (dosage_schedule.urea_total_kg / 45.0).toFixed(1);
  const dapBags  = (dosage_schedule.dap_total_kg / 50.0).toFixed(1);

  return (
    <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-sm space-y-5">
      {/* Header — Total Recommended Dosage */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3.5">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <Package className="w-4 h-4" />
            </span>
            Recommended Nitrogen Dosage
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Calculated by the XGBoost model based on your crop, soil, and weather conditions.
          </p>
        </div>
        <div className="sm:text-right">
          <div className="text-2xl sm:text-3xl font-black text-emerald-700 tracking-tight">
            {recommended_N_kg_ha}{' '}
            <span className="text-sm font-semibold text-slate-500">kg N / ha</span>
          </div>
        </div>
      </div>

      {/* How to Apply — Split Application */}
      <div>
        <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
          <Split className="w-3.5 h-3.5 text-slate-400" /> How to Apply (Split into 2 doses)
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Dose 1 */}
          <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200/80">
            <div className="flex items-center justify-between text-xs font-bold text-emerald-900 mb-1">
              <span>Dose 1 — Apply Now (40%)</span>
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-800">
              {dosage_schedule.immediate_kg_ha}{' '}
              <span className="text-xs font-semibold text-slate-500">kg N/ha</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-0.5">
              Spread evenly on the field before light watering or top-dressing.
            </p>
          </div>

          {/* Dose 2 */}
          <div className="p-3.5 rounded-xl bg-sky-50/50 border border-sky-200/80">
            <div className="flex items-center justify-between text-xs font-bold text-sky-900 mb-1">
              <span>Dose 2 — After Irrigation (60%)</span>
            </div>
            <div className="text-xl sm:text-2xl font-black text-slate-800">
              {dosage_schedule.post_irrigation_kg_ha}{' '}
              <span className="text-xs font-semibold text-slate-500">kg N/ha</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-0.5">
              Apply 3–5 days after irrigation when soil has absorbed water.
            </p>
          </div>
        </div>
      </div>

      {/* Fertilizer Bags to Purchase */}
      <div>
        <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2.5">
          How Many Bags to Buy (for your whole field — {dosage_schedule.field_area_ha} ha)
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Urea */}
          <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="text-xs font-semibold text-slate-600">Urea (46% N) — Neem Coated</div>
            <div className="mt-1 flex items-baseline justify-between gap-2">
              <span className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                {dosage_schedule.urea_total_kg}{' '}
                <span className="text-xs font-normal text-slate-500">kg total</span>
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-200/90 text-slate-800">
                ≈ {ureaBags} bags (45 kg each)
              </span>
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              Rate: {dosage_schedule.urea_total_kg_ha} kg/ha
            </div>
          </div>

          {/* DAP */}
          <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="text-xs font-semibold text-slate-600">DAP (18% N + Phosphorus)</div>
            <div className="mt-1 flex items-baseline justify-between gap-2">
              <span className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                {dosage_schedule.dap_total_kg}{' '}
                <span className="text-xs font-normal text-slate-500">kg total</span>
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-200/90 text-slate-800">
                ≈ {dapBags} bags (50 kg each)
              </span>
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              Rate: {dosage_schedule.dap_total_kg_ha} kg/ha
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
