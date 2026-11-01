import React, { useState, useEffect } from 'react';
import FieldMap from './components/Map/FieldMap';
import CropInputForm from './components/Forms/CropInputForm';
import DecisionCard from './components/Dashboard/DecisionCard';
import DosageCard from './components/Dashboard/DosageCard';
import RiskMeters from './components/Dashboard/RiskMeters';
import SpectralCard from './components/Dashboard/SpectralCard';
import { predictNitrogen, checkHealth } from './services/api';
import { Sprout, Activity, Cpu, Sparkles, BookOpen, Layers, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [polygon, setPolygon] = useState(null);
  const [formData, setFormData] = useState({
    crop_season: 'RABI',
    crop_type: 'WHEAT',
    growth_stage: 'TILLERING',
    days_after_sowing: 35,
    previous_crop: 'RICE',
    irrigation_type: 'FLOOD',
    target_yield_tha: 4.5,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!polygon) {
      setError('Please draw or select a field boundary on the map first.');
      return;
    }

    setIsLoading(true);
    setError(null);

    const payload = {
      field_polygon: polygon,
      crop_type: formData.crop_type,
      crop_season: formData.crop_season,
      growth_stage: formData.growth_stage,
      days_after_sowing: formData.days_after_sowing,
      previous_crop: formData.previous_crop,
      irrigation_type: formData.irrigation_type,
      target_yield_tha: formData.target_yield_tha,
    };

    try {
      const data = await predictNitrogen(payload);
      setResult(data);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(
        err.response?.data?.detail ||
          'Failed to reach prediction backend. Please ensure the FastAPI server is running on port 8000.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/70 text-slate-800 font-sans selection:bg-emerald-500 selection:text-white pb-12">
      {/* 1. Top Navigation Bar */}
      <header className="bg-white/95 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 shadow-subtle">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-sm shadow-emerald-600/20 shrink-0">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-display font-black tracking-tight text-slate-900">
                  GeoN-DSS
                </h1>
                <span className="text-[10px] font-display font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200/60">
                  Uttar Pradesh Pilot
                </span>
              </div>
              <p className="text-xs text-slate-500 font-sans hidden sm:block">
                Satellite Spectral & Climate-Gated Precision Nitrogen Decision Support System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-sans">
              <div
                className={`w-2 h-2 rounded-full shrink-0 ${
                  apiOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <span className="text-slate-600 font-medium">
                {apiOnline ? 'Backend Online' : 'Standby / Local'}
              </span>
            </div>

            <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-display font-bold border border-emerald-200/80">
              <Cpu className="w-3.5 h-3.5" />
              LightGBM + XGBoost
            </div>
          </div>
        </div>
      </header>

      {/* 2. Main Responsive Grid */}
      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-5">
        {/* Error notification banner */}
        {error && (
          <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm font-sans flex items-center justify-between shadow-xs">
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-xs font-bold text-rose-600 hover:text-rose-900 ml-4 underline cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* 2-Column Responsive Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Column: Interactive Map & Agronomic Form (5 cols on desktop) */}
          <div className="lg:col-span-5 space-y-4">
            {/* Interactive Leaflet Map (Self-sizing, no clipped headers) */}
            <FieldMap
              onPolygonChange={(geo) => setPolygon(geo)}
              selectedPolygon={polygon}
            />

            {/* Input Parameters Form */}
            <CropInputForm
              formData={formData}
              onChange={setFormData}
              onSubmit={handleSubmit}
              isLoading={isLoading}
            />
          </div>

          {/* Right Column: Intelligent Output Dashboard (7 cols on desktop) */}
          <div className="lg:col-span-7 space-y-4">
            {result ? (
              <>
                {/* 1. Gatekeeper Decision Banner */}
                <DecisionCard result={result} />

                {/* 2. Dosage Schedule (if GO) */}
                <DosageCard result={result} />

                {/* 3. Environmental Risk Meters */}
                <RiskMeters result={result} />

                {/* 4. Spectral Vegetation Indices */}
                <SpectralCard result={result} />

                {/* 5. SHAP Explainability Note */}
                {result.shap_explanation && (
                  <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-card">
                    <h4 className="text-xs font-display font-bold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-600" /> Agronomic Model Explainability (SHAP Rationale)
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-700 font-sans leading-relaxed">
                      {result.shap_explanation.summary}
                    </p>
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {result.shap_explanation.top_features.map((f, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] font-sans px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-medium border border-slate-200/60"
                        >
                          {f.feature}:{' '}
                          <span
                            className={
                              f.direction === 'UP'
                                ? 'text-emerald-700 font-bold'
                                : f.direction === 'DOWN'
                                ? 'text-sky-700 font-bold'
                                : 'text-rose-700 font-bold'
                            }
                          >
                            {f.direction} ({f.shap_value > 0 ? `+${f.shap_value}` : f.shap_value})
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              /* Empty Initial State Card */
              <div className="bg-white rounded-2xl border border-slate-200/90 p-8 sm:p-12 text-center shadow-card">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3 shadow-xs">
                  <Activity className="w-7 h-7" />
                </div>
                <h3 className="text-base sm:text-lg font-display font-bold text-slate-900">
                  Ready for Nitrogen Analysis
                </h3>
                <p className="text-xs sm:text-sm text-slate-500 font-sans max-w-md mx-auto mt-1.5 leading-relaxed">
                  Select a sample plot or draw your field boundary on the map, set crop parameters on the left, and click{' '}
                  <span className="font-semibold text-emerald-700">"Calculate Precision Nitrogen Dosage"</span>.
                </p>

                <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3 text-left border-t border-slate-100 pt-5">
                  <div className="p-3 rounded-xl bg-slate-50/80 border border-slate-100">
                    <div className="text-xs font-display font-bold text-slate-800 flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-black">1</span>
                      Spatial Polygon
                    </div>
                    <p className="text-[11px] text-slate-500 font-sans mt-1">
                      Computes acreage and maps coordinates to UP agro-climatic zones.
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50/80 border border-slate-100">
                    <div className="text-xs font-display font-bold text-slate-800 flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-black">2</span>
                      LightGBM Guard
                    </div>
                    <p className="text-[11px] text-slate-500 font-sans mt-1">
                      Screens 48h rainfall and temp to prevent rain leaching or foliar burn.
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50/80 border border-slate-100">
                    <div className="text-xs font-display font-bold text-slate-800 flex items-center gap-1.5">
                      <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-black">3</span>
                      XGBoost Dosage
                    </div>
                    <p className="text-[11px] text-slate-500 font-sans mt-1">
                      Calculates exact kg N/ha, split schedule, and 45kg commercial Urea bags.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
