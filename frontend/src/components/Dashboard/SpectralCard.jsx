import React from 'react';
import { Satellite, TrendingDown, TrendingUp, Layers } from 'lucide-react';

export default function SpectralCard({ result }) {
  if (!result || !result.spectral_data) return null;

  const { spectral_data } = result;

  const Trend = ({ val }) =>
    val < 0
      ? <span className="text-rose-600 flex items-center gap-0.5 font-bold"><TrendingDown className="w-3 h-3" /> {val}</span>
      : <span className="text-emerald-600 flex items-center gap-0.5 font-bold"><TrendingUp className="w-3 h-3" /> +{val}</span>;

  return (
    <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-sm space-y-3.5">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-indigo-100 text-indigo-700">
              <Satellite className="w-4 h-4" />
            </span>
            Satellite Crop Health Readings
          </h3>
          <p className="text-xs text-slate-500">{spectral_data.image_date}</p>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
          Sentinel-2 (10m)
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* NDRE — Nitrogen status */}
        <div className="p-3 rounded-xl border border-amber-200/90 bg-amber-50/40">
          <div className="text-[11px] font-bold text-amber-900 flex items-center justify-between">
            <span>NDRE — Nitrogen Level</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded-md bg-amber-200 text-amber-900 font-black">Key</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{spectral_data.ndre.toFixed(3)}</div>
          <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
            <Trend val={spectral_data.ndre_15d_trend} />
            <span className="text-[10px] text-slate-400">15-day trend</span>
          </div>
        </div>

        {/* NDVI — Plant Greenness */}
        <div className="p-3 rounded-xl border border-emerald-200/90 bg-emerald-50/40">
          <div className="text-[11px] font-bold text-emerald-900 flex items-center justify-between">
            <span>NDVI — Plant Greenness</span>
            <span className="text-[9px] text-emerald-700 font-medium">Biomass</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{spectral_data.ndvi.toFixed(3)}</div>
          <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
            <Trend val={spectral_data.ndvi_15d_trend} />
            <span className="text-[10px] text-slate-400">15-day trend</span>
          </div>
        </div>

        {/* GNDVI — Chlorophyll */}
        <div className="p-3 rounded-xl border border-teal-200/90 bg-teal-50/40">
          <div className="text-[11px] font-bold text-teal-900 flex items-center justify-between">
            <span>GNDVI — Chlorophyll</span>
            <span className="text-[9px] text-teal-700 font-medium">Leaf cover</span>
          </div>
          <div className="text-xl sm:text-2xl font-black text-slate-900 mt-1">{spectral_data.gndvi.toFixed(3)}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            LAI: <span className="font-semibold">{spectral_data.lai} m²/m²</span>
          </div>
        </div>
      </div>
    </div>
  );
}
