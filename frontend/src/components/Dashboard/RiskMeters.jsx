import React from 'react';
import { CloudDrizzle, Flame, Wind, Thermometer, Droplets, Gauge } from 'lucide-react';

export default function RiskMeters({ result }) {
  if (!result || !result.risk_scores) return null;

  const { risk_scores, weather_data } = result;

  const leachPct = Math.min(100, Math.max(0, (risk_scores.rain_leach_score / 8.0) * 100));
  const burnPct = Math.min(100, Math.max(0, (risk_scores.burn_risk_score / 10.0) * 100));

  const isLeachAlert = risk_scores.rain_leach_score > 4.0;
  const isBurnAlert = risk_scores.burn_risk_score > 5.0;

  return (
    <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-card space-y-4">
      <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-display font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <Gauge className="w-4 h-4" />
            </span>
            Environmental Risk Gauges
          </h3>
          <p className="text-xs text-slate-500 font-sans">Evaluated by Risk Engine before LightGBM classification</p>
        </div>

        <span className="px-2.5 py-1 rounded-full text-[11px] font-display font-bold bg-slate-100 text-slate-700 border border-slate-200/60">
          State: {risk_scores.weather_state_label}
        </span>
      </div>

      {/* Leaching Risk Gauge */}
      <div>
        <div className="flex justify-between items-center text-xs mb-1 font-sans font-medium">
          <span className="flex items-center gap-1.5 text-slate-700 font-semibold">
            <CloudDrizzle className="w-3.5 h-3.5 text-blue-500" />
            Rain Leaching Score
          </span>
          <span className={`font-display font-bold ${isLeachAlert ? 'text-rose-600' : 'text-slate-800'}`}>
            {risk_scores.rain_leach_score.toFixed(2)} / 10.0{' '}
            <span className="text-[10px] text-slate-400 font-normal font-sans">(Limit: 4.0)</span>
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isLeachAlert ? 'bg-rose-500' : 'bg-blue-500'
            }`}
            style={{ width: `${leachPct}%` }}
          />
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
            style={{ left: '50%' }}
            title="Threshold: 4.0"
          />
        </div>
        <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-sans">
          <span>Safe (0.0)</span>
          <span>Threshold: 4.0</span>
          <span>High Leaching</span>
        </div>
      </div>

      {/* Burn Risk Gauge */}
      <div>
        <div className="flex justify-between items-center text-xs mb-1 font-sans font-medium">
          <span className="flex items-center gap-1.5 text-slate-700 font-semibold">
            <Flame className="w-3.5 h-3.5 text-amber-500" />
            Fertilizer Burn Risk Score
          </span>
          <span className={`font-display font-bold ${isBurnAlert ? 'text-amber-600' : 'text-slate-800'}`}>
            {risk_scores.burn_risk_score.toFixed(2)} / 10.0{' '}
            <span className="text-[10px] text-slate-400 font-normal font-sans">(Limit: 5.0)</span>
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isBurnAlert ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${burnPct}%` }}
          />
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
            style={{ left: '50%' }}
            title="Threshold: 5.0"
          />
        </div>
        <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-sans">
          <span>Safe (0.0)</span>
          <span>Threshold: 5.0</span>
          <span>Severe Burn Risk</span>
        </div>
      </div>

      {/* Weather Snapshot Grid */}
      {weather_data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100">
          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Thermometer className="w-3.5 h-3.5 mx-auto text-rose-500 mb-0.5" />
            <div className="text-[10px] text-slate-400 font-sans">Max Temp</div>
            <div className="text-xs font-display font-bold text-slate-800">{weather_data.temp_max_c}°C</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Droplets className="w-3.5 h-3.5 mx-auto text-blue-500 mb-0.5" />
            <div className="text-[10px] text-slate-400 font-sans">Humidity</div>
            <div className="text-xs font-display font-bold text-slate-800">{weather_data.humidity_pct}%</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <CloudDrizzle className="w-3.5 h-3.5 mx-auto text-indigo-500 mb-0.5" />
            <div className="text-[10px] text-slate-400 font-sans">Rain 48h Cast</div>
            <div className="text-xs font-display font-bold text-slate-800">{weather_data.rainfall_forecast_48h_mm} mm</div>
          </div>

          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Wind className="w-3.5 h-3.5 mx-auto text-emerald-500 mb-0.5" />
            <div className="text-[10px] text-slate-400 font-sans">Wind Speed</div>
            <div className="text-xs font-display font-bold text-slate-800">{weather_data.wind_speed_ms} m/s</div>
          </div>
        </div>
      )}
    </div>
  );
}
