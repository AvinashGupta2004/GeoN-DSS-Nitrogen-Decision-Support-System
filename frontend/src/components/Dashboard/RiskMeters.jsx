import React from 'react';
import { CloudDrizzle, Flame, Wind, Thermometer, Droplets, Gauge } from 'lucide-react';

export default function RiskMeters({ result }) {
  if (!result || !result.risk_scores) return null;

  const { risk_scores, weather_data } = result;

  const leachPct = Math.min(100, Math.max(0, (risk_scores.rain_leach_score / 8.0) * 100));
  const burnPct  = Math.min(100, Math.max(0, (risk_scores.burn_risk_score / 10.0) * 100));

  const isLeachAlert = risk_scores.rain_leach_score > 4.0;
  const isBurnAlert  = risk_scores.burn_risk_score > 5.0;

  // Human-readable weather state
  const weatherLabels = {
    SUNNY: '☀️ Sunny', PARTLY_CLOUDY: '⛅ Partly Cloudy',
    OVERCAST: '☁️ Overcast', RAINFALL: '🌧️ Raining',
    THUNDERSTORM: '⛈️ Thunderstorm', FOGGY: '🌫️ Foggy',
  };
  const weatherLabel = weatherLabels[risk_scores.weather_state_label] || risk_scores.weather_state_label;

  return (
    <div className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/90 shadow-sm space-y-4">
      {/* Header */}
      <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <Gauge className="w-4 h-4" />
            </span>
            Weather &amp; Risk Check
          </h3>
          <p className="text-xs text-slate-500">Conditions checked before giving nitrogen advice</p>
        </div>
        <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200/60">
          {weatherLabel}
        </span>
      </div>

      {/* Rain / Leaching Risk */}
      <div>
        <div className="flex justify-between items-center text-xs mb-1 font-medium">
          <span className="flex items-center gap-1.5 text-slate-700 font-semibold">
            <CloudDrizzle className="w-3.5 h-3.5 text-blue-500" />
            Rain Washout Risk
          </span>
          <span className={`font-bold ${isLeachAlert ? 'text-rose-600' : 'text-slate-800'}`}>
            {isLeachAlert ? '⚠️ HIGH' : '✓ LOW'}
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ${isLeachAlert ? 'bg-rose-500' : 'bg-blue-400'}`}
            style={{ width: `${leachPct}%` }}
          />
          <div className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10" style={{ left: '50%' }} />
        </div>
        <div className="flex justify-between text-[10px] text-slate-400 mt-1">
          <span>Safe</span>
          <span>Danger Zone →</span>
        </div>
      </div>

      {/* Burn Risk */}
      <div>
        <div className="flex justify-between items-center text-xs mb-1 font-medium">
          <span className="flex items-center gap-1.5 text-slate-700 font-semibold">
            <Flame className="w-3.5 h-3.5 text-amber-500" />
            Leaf Burn Risk (Heat + Wind)
          </span>
          <span className={`font-bold ${isBurnAlert ? 'text-amber-600' : 'text-slate-800'}`}>
            {isBurnAlert ? '⚠️ HIGH' : '✓ LOW'}
          </span>
        </div>
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ${isBurnAlert ? 'bg-amber-500' : 'bg-emerald-400'}`}
            style={{ width: `${burnPct}%` }}
          />
          <div className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10" style={{ left: '50%' }} />
        </div>
        <div className="flex justify-between text-[10px] text-slate-400 mt-1">
          <span>Safe</span>
          <span>Danger Zone →</span>
        </div>
      </div>

      {/* Weather snapshot */}
      {weather_data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100">
          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Thermometer className="w-3.5 h-3.5 mx-auto text-rose-500 mb-0.5" />
            <div className="text-[10px] text-slate-400">Max Temp</div>
            <div className="text-xs font-bold text-slate-800">{weather_data.temp_max_c}°C</div>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Droplets className="w-3.5 h-3.5 mx-auto text-blue-500 mb-0.5" />
            <div className="text-[10px] text-slate-400">Humidity</div>
            <div className="text-xs font-bold text-slate-800">{weather_data.humidity_pct}%</div>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <CloudDrizzle className="w-3.5 h-3.5 mx-auto text-indigo-500 mb-0.5" />
            <div className="text-[10px] text-slate-400">Rain (48h)</div>
            <div className="text-xs font-bold text-slate-800">{weather_data.rainfall_forecast_48h_mm} mm</div>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 text-center">
            <Wind className="w-3.5 h-3.5 mx-auto text-emerald-500 mb-0.5" />
            <div className="text-[10px] text-slate-400">Wind</div>
            <div className="text-xs font-bold text-slate-800">{weather_data.wind_speed_ms} m/s</div>
          </div>
        </div>
      )}
    </div>
  );
}
