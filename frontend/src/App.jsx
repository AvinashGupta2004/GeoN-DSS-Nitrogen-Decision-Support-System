import React, { useState, useEffect, useCallback, useRef } from 'react';
import FieldMap from './components/Map/FieldMap';
import CropInputForm from './components/Forms/CropInputForm';
import DecisionCard from './components/Dashboard/DecisionCard';
import DosageCard from './components/Dashboard/DosageCard';
import RiskMeters from './components/Dashboard/RiskMeters';
import SpectralCard from './components/Dashboard/SpectralCard';
import { predictNitrogen, checkHealth } from './services/api';
import { Sprout, Activity, Cpu, Sparkles, AlertTriangle, WifiOff } from 'lucide-react';

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
  const [apiOnline, setApiOnline] = useState(null); // null = checking, true/false = known
  const requestSequenceRef = useRef(0);

  // Check backend health on mount
  useEffect(() => {
    checkHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  // Stable callback so FieldMap doesn't re-render unnecessarily
  const handlePolygonChange = useCallback((geo) => {
    requestSequenceRef.current += 1;
    setPolygon(geo);
    // Clear old result when field changes so user knows they need to re-predict
    setResult(null);
    setError(null);
  }, []);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();

    if (!polygon) {
      setError('Please draw a field on the map first (click "Draw New Field", place at least 3 points, then click "Finish Drawing").');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    const requestSequence = ++requestSequenceRef.current;
    const payload = {
      field_polygon: polygon,
      crop_type: formData.crop_type,
      crop_season: formData.crop_season,
      growth_stage: formData.growth_stage,
      days_after_sowing: Number(formData.days_after_sowing),
      previous_crop: formData.previous_crop,
      irrigation_type: formData.irrigation_type,
      target_yield_tha: Number(formData.target_yield_tha),
    };

    try {
      const data = await predictNitrogen(payload);
      if (requestSequence !== requestSequenceRef.current) return;
      if (!data || typeof data.status === 'undefined') {
        throw new Error('Invalid response from server.');
      }
      setResult(data);
      setApiOnline(true);
    } catch (err) {
      if (requestSequence !== requestSequenceRef.current) return;
      console.error('Prediction failed:', err);
      setApiOnline(err.response ? true : false); // server responded = online, even if error
      const detail = err.response?.data?.detail;
      if (!err.response) {
        setError('⚠️ Cannot connect to the backend. Please start the server: run "python start_backend.py" in the project folder, then try again.');
      } else {
        setError(detail || `Server error (${err.response.status}): ${err.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/70 text-slate-800 font-sans selection:bg-emerald-500 selection:text-white pb-12">
      {/* ── Top Navigation Bar ── */}
      <header className="bg-white/95 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 shadow-sm">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-sm shrink-0">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight text-slate-900">GeoN-DSS</h1>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200/60">
                  Gorakhpur Pilot
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Precision Nitrogen Recommendation for Uttar Pradesh Farmers
              </p>
            </div>
          </div>

          {/* Status badges */}
          <div className="flex items-center gap-2.5">
            {/* Backend status */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
              {apiOnline === null ? (
                <div className="w-2 h-2 rounded-full bg-slate-300 animate-pulse" />
              ) : apiOnline ? (
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              ) : (
                <WifiOff className="w-3.5 h-3.5 text-amber-500" />
              )}
              <span className="text-slate-600 font-medium">
                {apiOnline === null ? 'Connecting...' : apiOnline ? 'Server Online' : 'Server Offline'}
              </span>
            </div>

            {/* Model badge */}
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200/80">
              <Cpu className="w-3.5 h-3.5" />
              LightGBM + XGBoost
            </div>
          </div>
        </div>
      </header>

      {/* ── Offline Warning Banner ── */}
      {apiOnline === false && (
        <div className="bg-amber-50 border-b border-amber-200 px-4 sm:px-6 py-2.5 flex items-center gap-2 text-amber-800 text-xs sm:text-sm font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500" />
          <span>
            Backend server is not running. Open a terminal in the project folder and run{' '}
            <code className="bg-amber-100 px-1.5 py-0.5 rounded font-mono text-xs">python start_backend.py</code>
            , then refresh this page.
          </span>
        </div>
      )}

      {/* ── Main Layout ── */}
      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-5">

        {/* Error banner */}
        {error && (
          <div className="mb-4 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm font-sans flex items-start justify-between gap-3 shadow-sm">
            <span className="leading-relaxed">{error}</span>
            <button
              onClick={() => setError(null)}
              className="text-xs font-bold text-rose-600 hover:text-rose-900 underline cursor-pointer shrink-0 mt-0.5"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Two-column grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">

          {/* ── Left column: Map + Form ── */}
          <div className="lg:col-span-5 space-y-4">
            <FieldMap
              onPolygonChange={handlePolygonChange}
              selectedPolygon={polygon}
            />
            <CropInputForm
              formData={formData}
              onChange={setFormData}
              onSubmit={handleSubmit}
              isLoading={isLoading}
              hasPolygon={!!polygon}
            />
          </div>

          {/* ── Right column: Results ── */}
          <div className="lg:col-span-7 space-y-4">
            {isLoading ? (
              /* Loading state */
              <div className="bg-white rounded-2xl border border-slate-200/90 p-12 text-center shadow-sm">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-4">
                  <Cpu className="w-7 h-7 animate-pulse" />
                </div>
                <h3 className="text-base font-bold text-slate-900">Analysing your field…</h3>
                <p className="text-sm text-slate-500 mt-1.5">
                  Checking weather, soil data, and running the ML models. This takes a few seconds.
                </p>
                <div className="mt-5 space-y-2 text-left max-w-xs mx-auto text-xs text-slate-500">
                  {['Fetching weather forecast (48 h)', 'Reading soil properties', 'Running Safety Check (LightGBM)', 'Calculating Nitrogen Dosage (XGBoost)'].map((step, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" style={{ animationDelay: `${i * 0.3}s` }} />
                      {step}
                    </div>
                  ))}
                </div>
              </div>
            ) : result ? (
              <>
                <DecisionCard result={result} />
                <DosageCard result={result} />
                <RiskMeters result={result} />
                <SpectralCard result={result} />

                {/* Why this result — simple explanation */}
                {result.shap_explanation && (
                  <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-sm">
                    <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                      Why this recommendation?
                    </h4>
                    <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                      {result.shap_explanation.summary}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {result.shap_explanation.top_features.map((f, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-medium border border-slate-200/60"
                        >
                          {f.feature}:{' '}
                          <span className={
                            f.direction === 'UP' ? 'text-emerald-700 font-bold'
                            : f.direction === 'DOWN' ? 'text-sky-700 font-bold'
                            : 'text-rose-700 font-bold'
                          }>
                            {f.direction}
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              /* Empty / waiting state */
              <div className="bg-white rounded-2xl border border-slate-200/90 p-8 sm:p-12 text-center shadow-sm">
                <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
                  <Activity className="w-7 h-7" />
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">
                  Ready to Analyse Your Field
                </h3>
                <p className="text-sm text-slate-500 max-w-md mx-auto mt-2 leading-relaxed">
                  {!polygon
                    ? 'Draw your field boundary on the map (or pick a sample plot), fill in crop details, then click the green button.'
                    : 'Field selected! Fill in crop details on the left, then click the green button to get your nitrogen recommendation.'}
                </p>

                {/* Step guide */}
                <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3 text-left border-t border-slate-100 pt-5">
                  {[
                    { step: 1, title: 'Mark Your Field', desc: 'Draw the boundary on the map or pick a sample plot.' },
                    { step: 2, title: 'Enter Crop Info', desc: 'Select crop, season, growth stage, and irrigation type.' },
                    { step: 3, title: 'Get Recommendation', desc: 'Click the green button to get nitrogen dosage advice.' },
                  ].map(({ step, title, desc }) => (
                    <div key={step} className="p-3 rounded-xl bg-slate-50/80 border border-slate-100">
                      <div className="text-xs font-bold text-slate-800 flex items-center gap-1.5 mb-1">
                        <span className="w-4 h-4 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[10px] font-black">{step}</span>
                        {title}
                      </div>
                      <p className="text-[11px] text-slate-500">{desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
