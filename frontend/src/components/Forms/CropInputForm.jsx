import React from 'react';
import { Sprout, Calendar, Clock, Droplets, Target, History, Sparkles, Loader2, Info } from 'lucide-react';

const CROPS_BY_SEASON = {
  RABI: [
    { value: 'WHEAT', label: 'Wheat (गेहूं)' },
    { value: 'MUSTARD', label: 'Mustard (सरसों)' },
    { value: 'POTATO', label: 'Potato (आलू)' },
    { value: 'ONION', label: 'Onion (प्याज)' },
    { value: 'CHICKPEA', label: 'Chickpea (चना)' },
    { value: 'LENTIL', label: 'Lentil / Masoor (मसूर)' },
  ],
  KHARIF: [
    { value: 'RICE', label: 'Rice / Paddy (धान)' },
    { value: 'MAIZE', label: 'Maize (मक्का)' },
    { value: 'SUGARCANE', label: 'Sugarcane (गन्ना)' },
    { value: 'ARHAR', label: 'Arhar / Pigeonpea (अरहर)' },
    { value: 'BAJRA', label: 'Bajra / Pearl Millet (बाजरा)' },
    { value: 'SOYBEAN', label: 'Soybean (सोयाबीन)' },
  ],
  ZAID: [
    { value: 'MOONG', label: 'Moong Bean (मूंग)' },
    { value: 'WATERMELON', label: 'Watermelon (तरबूज)' },
    { value: 'FODDER_MAIZE', label: 'Fodder Maize (चारा मक्का)' },
  ],
};

const GROWTH_STAGES = [
  { value: 'GERMINATION', label: 'Germination / Emergence (0–10 DAS)' },
  { value: 'VEGETATIVE', label: 'Early Vegetative (10–35 DAS)' },
  { value: 'TILLERING', label: 'Tillering (Cereals, 25–55 DAS)' },
  { value: 'BOOTING', label: 'Booting / Panicle (45–70 DAS)' },
  { value: 'FLOWERING', label: 'Flowering / Anthesis (50–90 DAS)' },
  { value: 'GRAIN_FILL', label: 'Grain Fill / Bulbing (70–110 DAS)' },
  { value: 'MATURITY', label: 'Maturity / Pre-Harvest' },
];

const PREVIOUS_CROPS = [
  { value: 'RICE', label: 'Rice (No credit)' },
  { value: 'WHEAT', label: 'Wheat (No credit)' },
  { value: 'MAIZE', label: 'Maize (No credit)' },
  { value: 'ARHAR', label: 'Arhar / Pigeon Pea (+35 kg N credit)' },
  { value: 'SOYBEAN', label: 'Soybean (+30 kg N credit)' },
  { value: 'CHICKPEA', label: 'Chickpea (+25 kg N credit)' },
  { value: 'MOONG', label: 'Moong / Lentil (+20 kg N credit)' },
  { value: 'FALLOW', label: 'Fallow Land (+10 kg N credit)' },
];

export default function CropInputForm({ formData, onChange, onSubmit, isLoading }) {
  const currentCrops = CROPS_BY_SEASON[formData.crop_season] || CROPS_BY_SEASON.RABI;

  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange({
      ...formData,
      [name]: name === 'days_after_sowing' || name === 'target_yield_tha' ? Number(value) : value,
    });
  };

  const handleSeasonChange = (season) => {
    const crops = CROPS_BY_SEASON[season];
    onChange({
      ...formData,
      crop_season: season,
      crop_type: crops[0].value,
    });
  };

  return (
    <form onSubmit={onSubmit} className="bg-white rounded-2xl shadow-card border border-slate-200/90 p-4 sm:p-5 space-y-4">
      <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-display font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <Sprout className="w-4 h-4" />
            </span>
            Agronomic Field Profile
          </h2>
          <p className="text-xs text-slate-500 font-sans mt-0.5">
            Calibrate phenological nitrogen demand curve and soil carryover credits.
          </p>
        </div>
      </div>

      {/* Season Selector Tabs */}
      <div>
        <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1.5 flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5 text-slate-400" /> Crop Season
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'RABI', label: 'Rabi', sub: 'Winter (Oct–Mar)' },
            { id: 'KHARIF', label: 'Kharif', sub: 'Monsoon (Jun–Nov)' },
            { id: 'ZAID', label: 'Zaid', sub: 'Summer (Mar–Jun)' },
          ].map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => handleSeasonChange(s.id)}
              className={`py-2 px-2.5 rounded-xl border text-center transition-all ${
                formData.crop_season === s.id
                  ? 'bg-emerald-50 border-emerald-500 text-emerald-900 font-bold shadow-xs'
                  : 'border-slate-200 text-slate-600 hover:bg-slate-50 font-medium'
              }`}
            >
              <div className="text-xs font-display">{s.label}</div>
              <div className="text-[10px] text-slate-400 font-sans leading-tight mt-0.5">{s.sub}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Crop Type & Growth Stage */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1">
            Crop Variety
          </label>
          <select
            name="crop_type"
            value={formData.crop_type}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          >
            {currentCrops.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1">
            Phenological Stage
          </label>
          <select
            name="growth_stage"
            value={formData.growth_stage}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          >
            {GROWTH_STAGES.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Days After Sowing & Target Yield */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Clock className="w-3 h-3 text-slate-400" /> Days After Sowing (DAS)
          </label>
          <input
            type="number"
            min="1"
            max="250"
            name="days_after_sowing"
            value={formData.days_after_sowing}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          />
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Target className="w-3 h-3 text-slate-400" /> Target Yield (Tonnes / Ha)
          </label>
          <input
            type="number"
            step="0.1"
            min="0.5"
            max="120"
            name="target_yield_tha"
            value={formData.target_yield_tha}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          />
        </div>
      </div>

      {/* Previous Crop & Irrigation */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1 flex items-center gap-1">
            <History className="w-3 h-3 text-slate-400" /> Predecessor Crop
          </label>
          <select
            name="previous_crop"
            value={formData.previous_crop}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          >
            {PREVIOUS_CROPS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-slate-600 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Droplets className="w-3 h-3 text-slate-400" /> Irrigation System
          </label>
          <select
            name="irrigation_type"
            value={formData.irrigation_type}
            onChange={handleChange}
            className="w-full text-xs font-sans rounded-xl border border-slate-200 px-3 py-2 bg-slate-50/60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition"
          >
            <option value="FLOOD">Flood Irrigation (Typical UP)</option>
            <option value="SPRINKLER">Sprinkler System</option>
            <option value="DRIP">Drip Fertigation (Precision)</option>
            <option value="RAINFED">Rainfed (No Supplemental)</option>
          </select>
        </div>
      </div>

      {/* Action Button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-4 rounded-xl font-display font-bold text-sm text-white bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99] shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 transition disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Running Safety & Dosage Pipeline...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Calculate Precision Nitrogen Dosage
            </>
          )}
        </button>
      </div>
    </form>
  );
}
