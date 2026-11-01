import React from 'react';
import { Package, Split, CheckCheck, Info, Sparkles } from 'lucide-react';

export default function DosageCard({ result }) {
  if (!result || result.status !== 'GO' || !result.dosage_schedule) {
    return (
      <div className="bg-slate-50/80 rounded-2xl p-6 border border-dashed border-slate-300 text-center text-slate-400">
        <Package className="w-9 h-9 mx-auto mb-2 opacity-50" />
        <p className="text-sm font-display font-bold text-slate-600">Nitrogen Dosage Output is Locked</p>
        <p className="text-xs text-slate-400 font-sans mt-0.5">
          Dosage calculations unlock automatically when the Gatekeeper verifies a GO (Safe) window.
        </p>
      </div>
    );
  }

  const { dosage_schedule, recommended_N_kg_ha } = result;
  const ureaBags = (dosage_schedule.urea_total_kg / 45.0).toFixed(1);
  const dapBags = (dosage_schedule.dap_total_kg / 50.0).toFixed(1);

  return (
    <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-card space-y-5">
      {/* Top Total Recommended Dosage */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3.5">
        <div>
          <h3 className="text-sm font-display font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <Package className="w-4 h-4" />
            </span>
            Precision Nitrogen Dosage
          </h3>
          <p className="text-xs text-slate-500 font-sans">
            Calibrated by XGBoost Dosage Regressor from red-edge spectral deficiency.
          </p>
        </div>

        <div className="sm:text-right">
          <div className="text-2xl sm:text-3xl font-display font-black text-emerald-700 tracking-tight">
            {recommended_N_kg_ha} <span className="text-sm font-semibold text-slate-500">kg N / ha</span>
          </div>
        </div>
      </div>

      {/* Split Application Protocol (40% Immediate / 60% Post-Irrigation) */}
      <div>
        <h4 className="text-[11px] font-display font-bold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
          <Split className="w-3.5 h-3.5 text-slate-400" /> Split Application Protocol (40% / 60%)
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200/80">
            <div className="flex items-center justify-between text-xs font-display font-bold text-emerald-900 mb-1">
              <span>Immediate Application</span>
              <span className="px-2 py-0.5 rounded-md bg-emerald-200 text-emerald-900 font-extrabold text-[10px]">
                40% Initial
              </span>
            </div>
            <div className="text-xl sm:text-2xl font-display font-black text-slate-800">
              {dosage_schedule.immediate_kg_ha}{' '}
              <span className="text-xs font-semibold text-slate-500">kg N/ha</span>
            </div>
            <p className="text-[11px] text-slate-600 font-sans mt-0.5">
              Broadcast immediately before light harrowing or top-dress.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-sky-50/50 border border-sky-200/80">
            <div className="flex items-center justify-between text-xs font-display font-bold text-sky-900 mb-1">
              <span>Post-Irrigation Application</span>
              <span className="px-2 py-0.5 rounded-md bg-sky-200 text-sky-900 font-extrabold text-[10px]">
                60% Stage 2
              </span>
            </div>
            <div className="text-xl sm:text-2xl font-display font-black text-slate-800">
              {dosage_schedule.post_irrigation_kg_ha}{' '}
              <span className="text-xs font-semibold text-slate-500">kg N/ha</span>
            </div>
            <p className="text-[11px] text-slate-600 font-sans mt-0.5">
              Apply 3–5 days post-irrigation at field capacity moisture.
            </p>
          </div>
        </div>
      </div>

      {/* Commercial Bag Quantities (Total for Field) */}
      <div>
        <h4 className="text-[11px] font-display font-bold text-slate-500 uppercase tracking-wider mb-2.5">
          Commercial Bag Quantities (Total for Field)
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Urea Card */}
          <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="text-xs font-sans font-semibold text-slate-600">Neem-Coated Urea (46% N)</div>
            <div className="mt-1 flex items-baseline justify-between gap-2">
              <span className="text-xl sm:text-2xl font-display font-black text-slate-900 tracking-tight">
                {dosage_schedule.urea_total_kg}{' '}
                <span className="text-xs font-normal text-slate-500">kg</span>
              </span>
              <span className="text-xs font-display font-bold px-2 py-0.5 rounded-md bg-slate-200/90 text-slate-800">
                ≈ {ureaBags} bags (45kg)
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-sans mt-1">
              Rate: {dosage_schedule.urea_total_kg_ha} kg/ha
            </div>
          </div>

          {/* DAP Card */}
          <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50">
            <div className="text-xs font-sans font-semibold text-slate-600">DAP Supplement (18% N, 46% P₂O₅)</div>
            <div className="mt-1 flex items-baseline justify-between gap-2">
              <span className="text-xl sm:text-2xl font-display font-black text-slate-900 tracking-tight">
                {dosage_schedule.dap_total_kg}{' '}
                <span className="text-xs font-normal text-slate-500">kg</span>
              </span>
              <span className="text-xs font-display font-bold px-2 py-0.5 rounded-md bg-slate-200/90 text-slate-800">
                ≈ {dapBags} bags (50kg)
              </span>
            </div>
            <div className="text-[10px] text-slate-400 font-sans mt-1">
              Rate: {dosage_schedule.dap_total_kg_ha} kg/ha
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
