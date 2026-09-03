import React, { useEffect, useRef, useState } from 'react';
import { MapPin, Info, Layers } from 'lucide-react';

// We use vanilla Leaflet via CDN (loaded in index.html) to avoid react-leaflet SSR issues
export default function NetworkMapPage({ networkData }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [selectedSection, setSelectedSection] = useState(null);
  const [selectedStation, setSelectedStation] = useState(null);

  useEffect(() => {
    if (!networkData || !window.L) return;

    // Destroy previous map instance if exists
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const L = window.L;

    // Center on corridor midpoint (Kanpur area)
    const map = L.map(mapRef.current, {
      center: [26.8, 81.5],
      zoom: 7,
      zoomControl: true,
      attributionControl: true
    });

    mapInstanceRef.current = map;

    // Dark tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a> | Synthetic data for prototype only',
      maxZoom: 14
    }).addTo(map);

    // Draw section lines
    const sectionLines = {};
    (networkData.sections || []).forEach(sec => {
      const from = sec.station_from;
      const to = sec.station_to;
      if (!from || !to || !from.lat || !to.lat) return;

      const color = sec.is_blocked ? '#ef4444' : sec.electrified ? '#3b82f6' : '#64748b';
      const weight = sec.active_blocks_count > 0 ? 4 : 2;

      const line = L.polyline(
        [[from.lat, from.lng], [to.lat, to.lng]],
        { color, weight, opacity: sec.is_blocked ? 0.95 : 0.7 }
      ).addTo(map);

      line.bindPopup(`
        <div style="font-family:Inter,sans-serif;font-size:12px;min-width:180px;">
          <div style="font-weight:700;color:#e2e8f0;margin-bottom:6px;">${sec.section_code}</div>
          <div style="color:#94a3b8;">${from.code} → ${to.code}</div>
          <div style="color:#94a3b8;">${sec.distance_km} km · ${sec.max_speed_kmh} km/h</div>
          <div style="color:#94a3b8;">${sec.tracks_count} track(s) · ${sec.electrified ? '⚡ Electrified' : 'Non-electrified'}</div>
          ${sec.is_blocked ? `<div style="color:#f87171;font-weight:600;margin-top:6px;">⚠️ ${sec.active_blocks_count} Active Maintenance Block(s)</div>` : ''}
          <div style="color:#64748b;margin-top:4px;">Asset Condition: ${sec.average_asset_condition || '—'}%</div>
        </div>
      `, { maxWidth: 240 });

      sectionLines[sec.id] = { line, sec };
    });

    // Draw station markers
    (networkData.stations || []).forEach(st => {
      if (!st.latitude || !st.longitude) return;

      // Bigger marker for junctions
      const isJunction = st.lines_count >= 3;
      const radius = isJunction ? 8 : 5;
      const fillColor = isJunction ? '#f59e0b' : '#3b82f6';

      const circle = L.circleMarker([st.latitude, st.longitude], {
        radius,
        fillColor,
        color: '#0f172a',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(map);

      circle.bindPopup(`
        <div style="font-family:Inter,sans-serif;font-size:12px;min-width:160px;">
          <div style="font-weight:700;color:#e2e8f0;margin-bottom:4px;">${st.name}</div>
          <div style="color:#94a3b8;font-size:11px;">Code: ${st.code}</div>
          <div style="color:#94a3b8;font-size:11px;">Zone: ${st.zone} · Division: ${st.division}</div>
          <div style="color:#94a3b8;font-size:11px;">${st.lines_count} Platform Line(s)</div>
        </div>
      `, { maxWidth: 200 });
    });

    // Legend
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = () => {
      const div = L.DomUtil.create('div', '');
      div.style.cssText = 'background:#0f172a;border:1px solid #334155;border-radius:10px;padding:10px;font-family:Inter,sans-serif;font-size:11px;color:#94a3b8;';
      div.innerHTML = `
        <div style="font-weight:700;color:#e2e8f0;margin-bottom:8px;">LEGEND (Synthetic)</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><div style="height:3px;width:24px;background:#3b82f6;border-radius:2px;"></div>Electrified Section</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><div style="height:3px;width:24px;background:#64748b;border-radius:2px;"></div>Non-electrified Section</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><div style="height:3px;width:24px;background:#ef4444;border-radius:2px;"></div>Active Maintenance Block</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><div style="height:8px;width:8px;background:#f59e0b;border-radius:50%;"></div>Junction Station</div>
        <div style="display:flex;align-items:center;gap:6px;"><div style="height:5px;width:8px;background:#3b82f6;border-radius:50%;"></div>Regular Station</div>
      `;
      return div;
    };
    legend.addTo(map);

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [networkData]);

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <MapPin className="h-5 w-5 text-emerald-400" />
            Synthetic Railway Network Map
          </h2>
          <p className="text-xs text-slate-400">
            Delhi – Kanpur – Prayagraj – DDU Trunk Route · {networkData?.total_stations || '—'} Stations · {networkData?.total_sections || '—'} Sections
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 px-4 py-2.5 text-xs text-amber-300 flex items-center gap-2">
        <Info className="h-4 w-4 text-amber-400 flex-shrink-0" />
        <span><strong>Prototype Disclaimer:</strong> Station coordinates and sections are synthetically generated for algorithm testing. They do not represent actual IR network geography.</span>
      </div>

      {/* Stats */}
      {networkData && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Stations', value: networkData.total_stations },
            { label: 'Track Sections', value: networkData.total_sections },
            { label: 'Active Blocks', value: (networkData.sections || []).filter(s => s.is_blocked).length, color: 'text-rose-400' },
            { label: 'Corridor', value: '~630 km' },
          ].map(s => (
            <div key={s.label} className="rounded-xl border border-slate-800 bg-slate-900 p-3 text-xs">
              <div className="text-slate-400">{s.label}</div>
              <div className={`text-xl font-bold text-white mt-0.5 ${s.color || ''}`}>{s.value}</div>
            </div>
          ))}
        </div>
      )}

      {/* Leaflet Map Container */}
      {networkData ? (
        <div
          ref={mapRef}
          className="rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden"
          style={{ height: 'calc(100vh - 380px)', minHeight: 360 }}
        />
      ) : (
        <div className="rounded-2xl border border-slate-800 bg-slate-950 flex items-center justify-center"
          style={{ height: 360 }}>
          <div className="text-center text-slate-500">
            <Layers className="h-12 w-12 mb-3 opacity-30 mx-auto" />
            <p>Loading network topology from backend...</p>
          </div>
        </div>
      )}
    </div>
  );
}
