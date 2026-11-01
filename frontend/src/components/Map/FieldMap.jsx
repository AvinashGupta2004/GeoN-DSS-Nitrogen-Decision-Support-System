import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polygon, CircleMarker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Trash2, Edit3, CheckCircle2, Navigation, Layers, Sparkles } from 'lucide-react';

const DISTRICT_PRESETS = [
  { name: 'Lucknow', center: [26.8467, 80.9462], zoom: 12 },
  { name: 'Kanpur', center: [26.4499, 80.3319], zoom: 12 },
  { name: 'Amethi', center: [26.1554, 81.8143], zoom: 12 },
  { name: 'Gorakhpur', center: [26.7606, 83.3732], zoom: 12 },
];

const SAMPLE_FIELDS = [
  {
    label: 'Wheat (Kanpur)',
    district: 'Kanpur',
    center: [26.452, 80.328],
    coords: [
      [26.450, 80.325],
      [26.455, 80.325],
      [26.456, 80.332],
      [26.451, 80.331],
    ],
  },
  {
    label: 'Rice Paddy (Gorakhpur)',
    district: 'Gorakhpur',
    center: [26.762, 83.375],
    coords: [
      [26.758, 83.370],
      [26.765, 83.371],
      [26.766, 83.380],
      [26.759, 83.379],
    ],
  },
  {
    label: 'Sugarcane (Lucknow)',
    district: 'Lucknow',
    center: [26.848, 80.948],
    coords: [
      [26.845, 80.943],
      [26.852, 80.944],
      [26.853, 80.952],
      [26.846, 80.951],
    ],
  },
];

// Helper to handle smooth camera moves and map resizing
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
    // Invalidate size ensures no grey tiles or misaligned layers occur
    setTimeout(() => map.invalidateSize(), 150);
  }, [center, zoom, map]);
  return null;
}

// Sub-component to capture vertex clicks during drawing
function MapClickHandler({ isDrawing, onAddPoint }) {
  useMapEvents({
    click(e) {
      if (isDrawing) {
        onAddPoint([e.latlng.lat, e.latlng.lng]);
      }
    },
  });
  return null;
}

export default function FieldMap({ onPolygonChange, selectedPolygon }) {
  const [points, setPoints] = useState(
    selectedPolygon?.geometry?.coordinates?.[0]?.map(p => [p[1], p[0]]) || SAMPLE_FIELDS[0].coords
  );
  const [isDrawing, setIsDrawing] = useState(false);
  const [activeCenter, setActiveCenter] = useState(DISTRICT_PRESETS[1].center); // default Kanpur
  const [activeZoom, setActiveZoom] = useState(13);

  // Sync valid polygons (3+ vertices) back to parent
  useEffect(() => {
    if (points.length >= 3) {
      const geoCoords = points.map(p => [Number(p[1].toFixed(5)), Number(p[0].toFixed(5))]);
      const closedCoords = [...geoCoords, geoCoords[0]];
      onPolygonChange({
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [closedCoords],
        },
      });
    }
  }, [points]);

  const handleAddPoint = (latlng) => {
    setPoints(prev => [...prev, latlng]);
  };

  const handleClear = () => {
    setPoints([]);
    setIsDrawing(false);
  };

  const handleSelectPreset = (district) => {
    const preset = DISTRICT_PRESETS.find(d => d.name === district);
    if (preset) {
      setActiveCenter(preset.center);
      setActiveZoom(preset.zoom);
    }
  };

  const handleLoadSample = (sample) => {
    setPoints(sample.coords);
    setActiveCenter(sample.center);
    setActiveZoom(14);
    setIsDrawing(false);
  };

  return (
    <div className="bg-white rounded-2xl shadow-card border border-slate-200/90 overflow-hidden flex flex-col transition-all">
      {/* 1. Header Toolbar */}
      <div className="p-3.5 sm:p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 bg-slate-50/60">
        <div>
          <h2 className="text-sm font-display font-bold text-slate-800 flex items-center gap-2">
            <span className="p-1 rounded-lg bg-emerald-100 text-emerald-700">
              <MapPin className="w-4 h-4" />
            </span>
            Field Boundary & Satellite Area
          </h2>
          <p className="text-xs text-slate-500 font-sans mt-0.5">
            {isDrawing ? (
              <span className="text-amber-600 font-semibold flex items-center gap-1 animate-pulse">
                Click on the map to place boundary points (3 or more)
              </span>
            ) : (
              `${points.length} boundary points set. Click "Draw" or pick a sample plot.`
            )}
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={() => setIsDrawing(!isDrawing)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow-xs ${
              isDrawing
                ? 'bg-amber-500 text-white hover:bg-amber-600'
                : 'bg-emerald-600 text-white hover:bg-emerald-700'
            }`}
          >
            {isDrawing ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" /> Finish Drawing
              </>
            ) : (
              <>
                <Edit3 className="w-3.5 h-3.5" /> Draw New Field
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="px-2.5 py-1.5 rounded-xl text-xs font-semibold bg-white text-slate-600 border border-slate-200 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-200 transition flex items-center gap-1 shadow-2xs"
            title="Clear current polygon"
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear
          </button>
        </div>
      </div>

      {/* 2. District Quick-Jump & Sample Plots Bar */}
      <div className="px-3 sm:px-4 py-2 border-b border-slate-100 flex items-center gap-2 text-xs bg-white overflow-x-auto no-scrollbar">
        <span className="text-slate-400 font-semibold tracking-wider uppercase text-[10px] shrink-0 flex items-center gap-1">
          <Navigation className="w-3 h-3 text-slate-400" /> UP Districts:
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {DISTRICT_PRESETS.map(d => (
            <button
              key={d.name}
              type="button"
              onClick={() => handleSelectPreset(d.name)}
              className="px-2.5 py-1 rounded-lg bg-slate-100/90 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 font-medium transition text-[11px]"
            >
              {d.name}
            </button>
          ))}
        </div>

        <div className="h-4 w-px bg-slate-200 mx-1 shrink-0" />

        <span className="text-slate-400 font-semibold tracking-wider uppercase text-[10px] shrink-0 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-emerald-500" /> Presets:
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {SAMPLE_FIELDS.map(s => (
            <button
              key={s.label}
              type="button"
              onClick={() => handleLoadSample(s)}
              className="px-2.5 py-1 rounded-lg border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 hover:text-emerald-700 text-slate-600 font-medium transition text-[11px] shrink-0"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* 3. Interactive Leaflet Map Canvas */}
      <div className="relative w-full h-[320px] sm:h-[350px]">
        <MapContainer
          center={activeCenter}
          zoom={activeZoom}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <MapController center={activeCenter} zoom={activeZoom} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapClickHandler isDrawing={isDrawing} onAddPoint={handleAddPoint} />

          {/* Render Green Polygon Overlay */}
          {points.length >= 3 && (
            <Polygon
              positions={points}
              pathOptions={{
                color: '#059669',
                fillColor: '#10b981',
                fillOpacity: 0.35,
                weight: 2.5,
                dashArray: isDrawing ? '4, 4' : null,
              }}
            />
          )}

          {/* Clean sleek vertex markers instead of giant pin icons */}
          {points.map((pt, idx) => (
            <CircleMarker
              key={idx}
              center={pt}
              radius={idx === 0 ? 6 : 5}
              pathOptions={{
                color: idx === 0 ? '#047857' : '#0284c7',
                fillColor: idx === 0 ? '#10b981' : '#38bdf8',
                fillOpacity: 0.9,
                weight: 2,
              }}
            />
          ))}
        </MapContainer>

        {/* Floating helper badges */}
        {isDrawing && (
          <div className="absolute top-3 left-12 z-[1000] bg-slate-900/90 backdrop-blur-xs text-white px-3 py-1.5 rounded-xl text-xs font-medium shadow-lg flex items-center gap-2 pointer-events-none">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
            Click on map to add vertex ({points.length} points)
          </div>
        )}

        <div className="absolute bottom-2 left-2 z-[1000] bg-white/90 backdrop-blur-xs px-2.5 py-1 rounded-lg text-[10px] font-semibold text-slate-600 shadow-xs border border-slate-200/60 pointer-events-none">
          {points.length >= 3 ? `${points.length} Vertices Locked` : 'Polygon Incomplete'}
        </div>
      </div>
    </div>
  );
}
