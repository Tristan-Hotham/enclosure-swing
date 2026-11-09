/* Enclosure and the Swing riots: map page. MapLibre + OpenFreeMap Positron. Data: data/page.json, data/england_wales.geojson */
(function () {
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const COL = { 2: '#A3261B', 1: '#C8922E', 3: '#2F6DB0', 0: '#CDBF9F' };
  const CATN = { 2: 'Enclosure Act 1790 to 1830', 1: 'Enclosure Acts before 1790 only', 3: 'First enclosure Act 1831 or later', 0: 'No enclosure Act linked' };
  const root = document.documentElement;
  const tb = document.getElementById('theme');
  try { const t = localStorage.getItem('es-theme'); if (t) root.dataset.theme = t; } catch (e) {}
  tb.addEventListener('click', () => { const d = root.dataset.theme === 'dark' || (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches); root.dataset.theme = d ? 'light' : 'dark'; try { localStorage.setItem('es-theme', root.dataset.theme); } catch (e) {} });
  const cart = document.getElementById('cart');
  document.getElementById('fold').addEventListener('click', () => cart.classList.add('folded'));
  cart.addEventListener('click', e => { if (cart.classList.contains('folded') && e.target.id !== 'fold') cart.classList.remove('folded'); });
  if (innerWidth < 600) cart.classList.add('folded');
  const lb = document.getElementById('lyrBtn'), lp = document.getElementById('lp');
  lb.addEventListener('click', () => { const o = lp.classList.toggle('open'); lb.setAttribute('aria-expanded', o); });
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const map = new maplibregl.Map({ container: 'map', style: STYLE, bounds: [[-5.8, 49.9], [1.8, 55.9]], fitBoundsOptions: { padding: 20 }, maxZoom: 14, attributionControl: { compact: true }, renderWorldCopies: false });
  window.__map = map;
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
  let D = null, year = 1830;
  Promise.all([fetch('data/page.json').then(r => r.json()), fetch('data/england_wales.geojson').then(r => r.json()), new Promise(r => map.on('load', r))]).then(([d, ew]) => {
    D = d;
    const feats = d.parishes.map((p, i) => ({ type: 'Feature', id: i, geometry: { type: 'Point', coordinates: [p[1], p[0]] },
      properties: { i, cat: p[8], swing: p[4], first: p[9] || 9999, sample: p[10] } }));
    map.addSource('ew', { type: 'geojson', data: ew });
    map.addLayer({ id: 'ew-line', type: 'line', source: 'ew', paint: { 'line-color': '#8C7B5E', 'line-width': 1.2, 'line-opacity': .8 } });
    map.addSource('p', { type: 'geojson', data: { type: 'FeatureCollection', features: feats } });
    const r0 = ['interpolate', ['linear'], ['zoom'], 5, 2.2, 8, 4, 11, 8];
    map.addLayer({ id: 'pts', type: 'circle', source: 'p', paint: {
      'circle-radius': r0, 'circle-color': ['case', ['<=', ['get', 'first'], 1830], ['match', ['get', 'cat'], 2, COL[2], 1, COL[1], 3, COL[3], COL[0]], COL[0]],
      'circle-stroke-color': '#FFFFFF', 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 5, .3, 9, 1] } });
    map.addLayer({ id: 'swing', type: 'circle', source: 'p', filter: ['>', ['get', 'swing'], 0], paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, ['+', 2.6, ['*', 0.7, ['sqrt', ['get', 'swing']]]], 8, ['+', 5, ['*', 1.6, ['sqrt', ['get', 'swing']]]], 11, ['+', 10, ['*', 3, ['sqrt', ['get', 'swing']]]]],
      'circle-color': 'rgba(0,0,0,0)', 'circle-stroke-color': '#2B2119', 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 5, .7, 10, 1.8], 'circle-stroke-opacity': .85 } });
    setYear(1830); applyLayers();
    map.on('click', e => {
      const f = map.queryRenderedFeatures([[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]], { layers: ['pts', 'swing'] });
      if (f.length) popup(f[0].properties.i);
    });
    ['pts', 'swing'].forEach(l => { map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
    const at = new URLSearchParams(location.search).get('at');
    if (at) { const [a, b, z] = at.split(',').map(Number); map.jumpTo({ center: [b, a], zoom: z }); }
  });

  function filterExpr() {
    const on = {}; lp.querySelectorAll('input[data-l]').forEach(c => on[c.dataset.l] = c.checked);
    const cats = []; if (on.recent) cats.push(2); if (on.old) cats.push(1); if (on.future) cats.push(3); if (on.never) cats.push(0);
    const f = ['all', ['in', ['get', 'cat'], ['literal', cats]]];
    if (!on.outside) f.push(['==', ['get', 'sample'], 1]);
    return { f, swing: on.swing, outside: on.outside };
  }
  function applyLayers() {
    if (!map.getLayer('pts')) return;
    const { f, swing, outside } = filterExpr();
    map.setFilter('pts', f);
    const sf = ['all', ['>', ['get', 'swing'], 0]]; if (!outside) sf.push(['==', ['get', 'sample'], 1]);
    map.setFilter('swing', sf);
    map.setLayoutProperty('swing', 'visibility', swing ? 'visible' : 'none');
    const st = map.getStyle();
    const bo = {}; lp.querySelectorAll('input[data-b]').forEach(c => bo[c.dataset.b] = c.checked);
    st.layers.forEach(l => {
      if (l.id === 'pts' || l.id === 'swing' || l.id === 'ew-line') return;
      if (l.type === 'symbol') map.setLayoutProperty(l.id, 'visibility', bo.labels ? 'visible' : 'none');
      else if (/highway|road|bridge|tunnel|railway|aeroway/.test(l.id)) map.setLayoutProperty(l.id, 'visibility', bo.roads ? 'visible' : 'none');
    });
    map.setLayoutProperty('ew-line', 'visibility', bo.outline ? 'visible' : 'none');
  }
  lp.addEventListener('change', applyLayers);

  const rng = document.getElementById('rng'), yr = document.getElementById('yr'), play = document.getElementById('play');
  function setYear(y) {
    year = +y; yr.textContent = year; rng.value = year;
    if (map.getLayer('pts')) map.setPaintProperty('pts', 'circle-color', ['case', ['<=', ['get', 'first'], year], ['match', ['get', 'cat'], 2, COL[2], 1, COL[1], 3, COL[3], COL[0]], COL[0]]);
  }
  rng.addEventListener('input', () => setYear(rng.value));
  let timer = null;
  play.addEventListener('click', () => {
    if (timer) { clearInterval(timer); timer = null; play.textContent = 'Play'; return; }
    if (year >= 1870) setYear(1750);
    play.textContent = 'Pause';
    timer = setInterval(() => { if (year >= 1870) { clearInterval(timer); timer = null; play.textContent = 'Play'; return; } setYear(year + 1); }, 140);
  });

  function popup(i) {
    const p = D.parishes[i];
    const acts = p[11].map(k => D.acts[k]);
    let h = `<b class="t">${esc(p[2])}</b><div>${esc(p[3])}</div><table>`;
    h += `<tr><td>Swing incidents</td><td>${p[4]}${p[4] ? ` (${p[5]} machine attack${p[5] === 1 ? '' : 's'}, ${p[6]} other)` : ''}</td></tr>`;
    h += `<tr><td>Threshing machines</td><td>${p[7]} recorded before 1830</td></tr>`;
    h += `<tr><td>Enclosure</td><td>${CATN[p[8]]}</td></tr>`;
    if (!p[10]) h += `<tr><td>Sample</td><td>outside the main sample</td></tr>`;
    h += `</table>`;
    if (acts.length) {
      h += `<div>Acts linked to this parish:</div><ul>` + acts.map(a => `<li><b>${a[0]}</b> ${esc(a[1])} <span style="color:#7A6A52">(${a[4] === 'L' ? 'local' : 'private'} Act; place "${esc(a[2])}", linked by ${a[3] === 'n' ? 'name' : 'map point'})</span></li>`).join('') + `</ul>`;
    }
    h += `<p class="nt">Sources: Caprettini and Voth (2020) parish data; Chronological Tables of Private and Local Acts, legislation.gov.uk.</p>`;
    new maplibregl.Popup(Object.assign({ maxWidth: '330px' }, innerWidth < 600 ? { anchor: 'bottom' } : {})).setLngLat([p[1], p[0]]).setHTML(h).addTo(map);
  }

  const q = document.getElementById('q'), sug = document.getElementById('sug');
  let hits = [], sel = -1;
  function go(h) {
    sug.style.display = 'none'; q.value = h.label;
    if (h.kind === 'p') { const p = D.parishes[h.i]; map.flyTo({ center: [p[1], p[0]], zoom: 11, duration: 1500, offset: [0, innerWidth < 600 ? 170 : 0] }); map.once('moveend', () => popup(h.i)); }
    else { const ps = D.parishes.filter(p => p[3] === h.label); const xs = ps.map(p => p[1]), ys = ps.map(p => p[0]); map.fitBounds([[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]], { padding: 40 }); }
  }
  q.addEventListener('input', () => {
    if (!D) return;
    const s = q.value.trim().toLowerCase(); sel = -1;
    if (s.length < 2) { sug.style.display = 'none'; return; }
    const counties = [...new Set(D.parishes.map(p => p[3]))].filter(c => c.toLowerCase().startsWith(s)).map(c => ({ kind: 'c', label: c }));
    const ps = [];
    D.parishes.forEach((p, i) => { const n = p[2].toLowerCase(); if (n.startsWith(s)) ps.push({ kind: 'p', i, label: p[2], sub: p[3], r: 0 }); else if (n.includes(s) && ps.length < 60) ps.push({ kind: 'p', i, label: p[2], sub: p[3], r: 1 }); });
    ps.sort((a, b) => a.r - b.r || a.label.localeCompare(b.label));
    hits = counties.concat(ps).slice(0, 12);
    sug.innerHTML = hits.map((h, k) => `<li role="option" data-k="${k}">${esc(h.label)} <span>${h.kind === 'c' ? 'county' : esc(h.sub)}</span></li>`).join('');
    sug.style.display = hits.length ? 'block' : 'none';
    [...sug.children].forEach(li => li.addEventListener('mousedown', e => { e.preventDefault(); go(hits[+li.dataset.k]); }));
  });
  q.addEventListener('keydown', e => {
    if (!hits.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + hits.length) % hits.length; [...sug.children].forEach((li, k) => li.setAttribute('aria-selected', k === sel)); }
    else if (e.key === 'Enter') { e.preventDefault(); go(hits[Math.max(sel, 0)]); }
    else if (e.key === 'Escape') sug.style.display = 'none';
  });
})();
