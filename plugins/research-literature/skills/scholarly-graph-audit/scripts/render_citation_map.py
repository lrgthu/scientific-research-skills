#!/usr/bin/env python3
"""Compiles a lineage graph JSON into a CSP-compliant interactive HTML citation map.

Follows Antigravity Generative UI conventions:
- Zero external JS CDNs (only allowlisted gstatic Tailwind CSS)
- Semantic CSS theme tokens (`--background`, `--card`, `--border`, `--foreground`, `--muted-foreground`, `--primary`)
- Live `themechange` Canvas redraw listener
- Supports both `standalone` (side-pane full explorer) and `inline` (<=430px chat embed) modes
- Dual layout toggle: Chronological Timeline (Litmaps-style X=Year) vs. Force Network (ResearchRabbit-style)
"""

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
from pathlib import Path


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__TITLE__</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Offline / standalone browser fallback utility styles (yields cleanly when Tailwind is loaded) */
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; line-height: 1.45; }
    .flex { display: flex; } .inline-flex { display: inline-flex; } .inline-block { display: inline-block; } .block { display: block; }
    .flex-wrap { flex-wrap: wrap; } .items-center { align-items: center; } .justify-between { justify-content: space-between; }
    .gap-1 { gap: 0.25rem; } .gap-1\.5 { gap: 0.375rem; } .gap-2 { gap: 0.5rem; } .gap-3 { gap: 0.75rem; }
    .grid { display: grid; }
    @media (min-width: 768px) {
      .md\:grid-cols-3, .lg\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .md\:col-span-2, .lg\:col-span-2 { grid-column: span 2 / span 2; }
    }
    .relative { position: relative; } .absolute { position: absolute; } .bottom-2 { bottom: 0.5rem; } .left-2 { left: 0.5rem; }
    .w-full { width: 100%; } .h-full { height: 100%; } .max-w-7xl { max-width: 80rem; } .mx-auto { margin-left: auto; margin-right: auto; }
    .p-0 { padding: 0; } .p-2 { padding: 0.5rem; } .p-3 { padding: 0.75rem; } .p-4 { padding: 1rem; } .m-0 { margin: 0; }
    .px-2 { padding-left: 0.5rem; padding-right: 0.5rem; } .px-2\.5 { padding-left: 0.625rem; padding-right: 0.625rem; }
    .py-0\.5 { padding-top: 0.125rem; padding-bottom: 0.125rem; } .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
    .pb-2 { padding-bottom: 0.5rem; } .pt-1 { padding-top: 0.25rem; } .pt-2 { padding-top: 0.5rem; }
    .rounded { border-radius: 0.375rem; } .rounded-full { border-radius: 9999px; }
    .border { border: 1px solid var(--border); } .border-b { border-bottom: 1px solid var(--card-border); }
    .border-y { border-top: 1px solid var(--card-border); border-bottom: 1px solid var(--card-border); }
    .overflow-hidden { overflow: hidden; } .overflow-y-auto { overflow-y: auto; }
    .text-xs { font-size: 12px; } .text-sm { font-size: 14px; } .font-medium { font-weight: 500; } .font-semibold { font-weight: 600; }
    .font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    .pointer-events-none { pointer-events: none; }
    .space-y-2 > * + * { margin-top: 0.5rem; } .space-y-2\.5 > * + * { margin-top: 0.625rem; } .space-y-3 > * + * { margin-top: 0.75rem; }
    [class*="bg-[var(--background)]"] { background-color: var(--background); }
    [class*="bg-[var(--card)]"] { background-color: var(--card); }
    [class*="bg-[var(--primary)]"] { background-color: var(--primary); }
    [class*="text-[var(--foreground)]"] { color: var(--foreground); }
    [class*="text-[var(--muted-foreground)]"] { color: var(--muted-foreground); }
    [class*="text-[var(--primary-foreground)]"] { color: var(--primary-foreground); }
    button, input { font: inherit; color: inherit; background: transparent; cursor: pointer; }
    input { cursor: text; }
    a { text-decoration: none; }
  </style>
  <script>
    // Inject standalone theme tokens ONLY when opened outside an IDE host container (never overrides host tokens)
    (function () {
      const root = document.documentElement;
      if (!getComputedStyle(root).getPropertyValue('--foreground').trim()) {
        const dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const vars = dark ? {
          '--background': '#0b1120', '--card': '#111827', '--card-border': '#1f2937', '--border': '#334155',
          '--foreground': '#f8fafc', '--muted-foreground': '#94a3b8', '--placeholder': '#64748b',
          '--primary': '#38bdf8', '--primary-foreground': '#0f172a'
        } : {
          '--background': '#f8fafc', '--card': '#ffffff', '--card-border': '#e2e8f0', '--border': '#cbd5e1',
          '--foreground': '#0f172a', '--muted-foreground': '#475569', '--placeholder': '#94a3b8',
          '--primary': '#0284c7', '--primary-foreground': '#ffffff'
        };
        if (!dark) root.classList.add('light');
        Object.entries(vars).forEach(([k, v]) => root.style.setProperty(k, v));
      }
    })();
  </script>
</head>
<body class="__BODY_CLASS__">
  <div class="__WRAPPER_CLASS__">
    <!-- Top Control Bar -->
    <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[var(--card-border)] text-xs">
      <div class="flex flex-wrap items-center gap-1.5" id="roleFilters">
        <button data-role="all" class="role-btn px-2.5 py-1 rounded font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">All (__TOTAL_NODES__)</button>
        <button data-role="seed" class="role-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--card)]">★ Seeds</button>
        <button data-role="ancestor" class="role-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--card)]">← Roots (Co-Cited)</button>
        <button data-role="frontier" class="role-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--card)]">→ Frontier</button>
        <button data-role="semantic_sibling" class="role-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--card)]">≈ SPECTER2</button>
      </div>
      <div class="flex items-center gap-2">
        <input id="searchBox" type="text" placeholder="Filter title / author / year..."
          class="px-2 py-1 rounded bg-[var(--card)] border border-[var(--border)] text-[var(--foreground)] placeholder-[var(--placeholder)] text-xs w-44 focus:outline-none" />
        <div class="inline-flex rounded border border-[var(--border)] overflow-hidden">
          <button id="btnTimeline" class="px-2 py-1 bg-[var(--primary)] text-[var(--primary-foreground)] font-medium">Timeline</button>
          <button id="btnForce" class="px-2 py-1 bg-[var(--card)] text-[var(--muted-foreground)]">Force</button>
        </div>
        <button id="btnReset" class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--card)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]" title="Reset Zoom">Reset</button>
      </div>
    </div>

    <!-- Main Interactive Split Area -->
    <div class="grid __GRID_CLASS__ gap-3 pt-2">
      <!-- Canvas Stage -->
      <div class="relative rounded border border-[var(--card-border)] bg-[var(--card)] overflow-hidden" style="height: __CANVAS_HEIGHT__px;">
        <canvas id="graphCanvas" class="w-full h-full cursor-grab active:cursor-grabbing block"></canvas>
        <!-- Legend Overlay -->
        <div class="absolute bottom-2 left-2 flex flex-wrap items-center gap-3 px-2.5 py-1 rounded bg-[var(--background)]/85 border border-[var(--card-border)] text-xs pointer-events-none">
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#E69F00"></span>Seed</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#56B4E9"></span>Co-Cited Root</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#009E73"></span>Active Frontier</span>
          <span class="inline-flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#CC79A7"></span>SPECTER2 Sibling</span>
        </div>
      </div>

      <!-- Inspector Panel -->
      <div id="inspector" class="rounded border border-[var(--card-border)] bg-[var(--card)] p-3 overflow-y-auto space-y-2.5 text-xs" style="height: __CANVAS_HEIGHT__px;">
        <div id="inspectorContent"></div>
      </div>
    </div>
  </div>

  <script>
    const GRAPH = __GRAPH_JSON__;

    // Okabe-Ito CVD-safe role palette
    const ROLE_COLORS = {
      seed: '#E69F00',
      ancestor: '#56B4E9',
      frontier: '#009E73',
      semantic_sibling: '#CC79A7'
    };
    const ROLE_LABELS = {
      seed: 'Seed Paper',
      ancestor: 'Foundational Ancestor (Co-Cited)',
      frontier: 'Active Frontier (Citing Seed)',
      semantic_sibling: 'Semantic Sibling (SPECTER2)'
    };

    const canvas = document.getElementById('graphCanvas');
    const ctx = canvas.getContext('2d');
    const inspectorContent = document.getElementById('inspectorContent');

    let layoutMode = 'timeline'; // 'timeline' | 'force'
    let activeRole = 'all';
    let searchQuery = '';
    let selectedId = (GRAPH.seeds && GRAPH.seeds[0]) ? GRAPH.seeds[0].canonical_id : (GRAPH.nodes[0] ? GRAPH.nodes[0].canonical_id : null);
    let hoveredId = null;

    // Camera state
    let cam = { x: 0, y: 0, k: 1 };
    let isDragging = false;
    let dragNode = null;
    let lastMouse = { x: 0, y: 0 };

    const nodes = GRAPH.nodes.map((n, idx) => {
      const cit = Math.max(0, n.citation_count || 0);
      const rBase = n.role === 'seed' ? 11 : Math.min(13, Math.max(5.5, 4.5 + Math.log10(cit + 1) * 2.2));
      return {
        ...n,
        idx,
        r: rBase,
        x: 0, y: 0,
        tx: 0, ty: 0,
        fx: 0, fy: 0
      };
    });
    const nodeMap = new Map(nodes.map(n => [n.canonical_id, n]));
    const edges = (GRAPH.edges || []).filter(e => nodeMap.has(e.source) && nodeMap.has(e.target));

    function computeLayouts() {
      const w = canvas.clientWidth || 680;
      const h = canvas.clientHeight || 360;
      const padX = 64, padY = 42;

      // 1. Chronological Timeline Layout (X = Year, Y = Role band + deterministic spread)
      const years = nodes.map(n => n.year).filter(y => y && y > 1950);
      const minY = years.length ? Math.min(...years) : 2018;
      const maxY = years.length ? Math.max(...years) : 2026;
      const spanY = Math.max(1, maxY - minY);

      const byYear = new Map();
      nodes.forEach(n => {
        const y = (n.year && n.year > 1950) ? n.year : Math.round((minY + maxY) / 2);
        if (!byYear.has(y)) byYear.set(y, []);
        byYear.get(y).push(n);
      });
      byYear.forEach((bucket, yr) => {
        bucket.sort((a, b) => (b.seed_overlap || 0) - (a.seed_overlap || 0) || (b.citation_count || 0) - (a.citation_count || 0));
        bucket.forEach((n, i) => {
          n.tx = padX + ((yr - minY) / spanY) * Math.max(120, w - 2 * padX);
          const slots = bucket.length;
          const frac = slots === 1 ? 0.5 : (i + 0.5) / slots;
          n.ty = padY + frac * Math.max(100, h - 2 * padY - 18);
        });
      });

      // 2. Force-Directed Layout (deterministic seeded spring-electrical relaxation)
      nodes.forEach((n, i) => {
        const angle = (i / Math.max(1, nodes.length)) * Math.PI * 2;
        const ring = n.role === 'seed' ? 28 : (n.role === 'ancestor' ? 115 : 145);
        n.fx = w / 2 + Math.cos(angle) * ring;
        n.fy = h / 2 + Math.sin(angle) * ring * 0.78;
      });
      for (let iter = 0; iter < 140; iter++) {
        const alpha = 1 - iter / 140;
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i], b = nodes[j];
            let dx = b.fx - a.fx, dy = b.fy - a.fy;
            let d2 = dx * dx + dy * dy + 1;
            let rep = (1100 * alpha) / d2;
            a.fx -= dx * rep; a.fy -= dy * rep;
            b.fx += dx * rep; b.fy += dy * rep;
          }
        }
        edges.forEach(e => {
          const s = nodeMap.get(e.source), t = nodeMap.get(e.target);
          let dx = t.fx - s.fx, dy = t.fy - s.fy;
          let dist = Math.sqrt(dx * dx + dy * dy) || 1;
          let targetDist = e.type === 'specter2_similar' ? 120 : 85;
          let k = (dist - targetDist) * 0.04 * alpha;
          s.fx += (dx / dist) * k; s.fy += (dy / dist) * k;
          t.fx -= (dx / dist) * k; t.fy -= (dy / dist) * k;
        });
        nodes.forEach(n => {
          const cx = w / 2, cy = h / 2;
          const pull = n.role === 'seed' ? 0.08 : 0.015;
          n.fx += (cx - n.fx) * pull * alpha;
          n.fy += (cy - n.fy) * pull * alpha;
          n.fx = Math.max(36, Math.min(w - 36, n.fx));
          n.fy = Math.max(32, Math.min(h - 36, n.fy));
        });
      }

      applyActiveCoords();
    }

    function applyActiveCoords() {
      nodes.forEach(n => {
        n.x = layoutMode === 'timeline' ? n.tx : n.fx;
        n.y = layoutMode === 'timeline' ? n.ty : n.fy;
      });
    }

    function isNodeVisible(n) {
      if (activeRole !== 'all' && n.role !== activeRole) return false;
      if (!searchQuery) return true;
      const hay = ((n.title || '') + ' ' + (n.authors || []).join(' ') + ' ' + (n.year || '') + ' ' + (n.venue || '')).toLowerCase();
      return hay.includes(searchQuery);
    }

    function getThemeColors() {
      const cs = getComputedStyle(document.documentElement);
      const isLight = document.documentElement.classList.contains('light');
      const fg = cs.getPropertyValue('--foreground').trim() || (isLight ? '#0f172a' : '#f8fafc');
      const muted = cs.getPropertyValue('--muted-foreground').trim() || (isLight ? '#64748b' : '#94a3b8');
      const border = cs.getPropertyValue('--border').trim() || (isLight ? '#cbd5e1' : '#334155');
      return { fg, muted, border, isLight };
    }

    function worldToScreen(wx, wy) {
      return { x: wx * cam.k + cam.x, y: wy * cam.k + cam.y };
    }
    function screenToWorld(sx, sy) {
      return { x: (sx - cam.x) / cam.k, y: (sy - cam.y) / cam.k };
    }

    function draw() {
      const dpr = window.devicePixelRatio || 1;
      const w = canvas.clientWidth || 680;
      const h = canvas.clientHeight || 360;
      if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
      }
      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      const theme = getThemeColors();
      const visSet = new Set(nodes.filter(isNodeVisible).map(n => n.canonical_id));
      const focusId = hoveredId || selectedId;
      const neighborSet = new Set();
      if (focusId) {
        neighborSet.add(focusId);
        edges.forEach(e => {
          if (e.source === focusId) neighborSet.add(e.target);
          if (e.target === focusId) neighborSet.add(e.source);
        });
      }

      // Draw subtle year ticks in timeline mode
      if (layoutMode === 'timeline') {
        const years = nodes.map(n => n.year).filter(y => y && y > 1950);
        if (years.length) {
          const minY = Math.min(...years), maxY = Math.max(...years);
          const spanY = Math.max(1, maxY - minY);
          const step = spanY > 14 ? 3 : (spanY > 7 ? 2 : 1);
          ctx.font = '10px ui-monospace, SFMono-Regular, monospace';
          ctx.fillStyle = theme.muted;
          ctx.textAlign = 'center';
          for (let yr = minY; yr <= maxY; yr += step) {
            const wx = 64 + ((yr - minY) / spanY) * Math.max(120, w - 128);
            const sx = worldToScreen(wx, 0).x;
            ctx.save();
            ctx.strokeStyle = theme.border;
            ctx.globalAlpha = 0.25;
            ctx.beginPath();
            ctx.moveTo(sx, 8);
            ctx.lineTo(sx, h - 24);
            ctx.stroke();
            ctx.restore();
            ctx.fillText(String(yr), sx, h - 8);
          }
        }
      }

      // Draw edges
      edges.forEach(e => {
        if (!visSet.has(e.source) || !visSet.has(e.target)) return;
        const s = nodeMap.get(e.source), t = nodeMap.get(e.target);
        const ps = worldToScreen(s.x, s.y), pt = worldToScreen(t.x, t.y);
        const isHighlighted = focusId && (e.source === focusId || e.target === focusId);

        ctx.save();
        ctx.beginPath();
        if (e.type === 'specter2_similar') {
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = '#CC79A7';
        } else {
          ctx.strokeStyle = isHighlighted ? (s.role === 'frontier' ? '#009E73' : '#56B4E9') : theme.muted;
        }
        ctx.globalAlpha = isHighlighted ? 0.9 : (focusId ? 0.14 : 0.32);
        ctx.lineWidth = isHighlighted ? 2.0 : 1.0;

        const mx = (ps.x + pt.x) / 2;
        const my = (ps.y + pt.y) / 2 - 12;
        ctx.moveTo(ps.x, ps.y);
        ctx.quadraticCurveTo(mx, my, pt.x, pt.y);
        ctx.stroke();
        ctx.restore();
      });

      // Draw nodes
      nodes.forEach(n => {
        if (!visSet.has(n.canonical_id)) return;
        const p = worldToScreen(n.x, n.y);
        const rad = n.r * Math.min(1.6, Math.max(0.8, Math.sqrt(cam.k)));
        const isSel = n.canonical_id === selectedId;
        const isHov = n.canonical_id === hoveredId;
        const dimmed = focusId && !neighborSet.has(n.canonical_id);

        ctx.save();
        ctx.globalAlpha = dimmed ? 0.28 : 1.0;

        // Outer ring for seeds, multi-seed overlap, or selection
        if (isSel || isHov || n.role === 'seed' || (n.seed_overlap || 0) >= 2) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, rad + (isSel ? 4 : 2.5), 0, Math.PI * 2);
          ctx.strokeStyle = isSel ? theme.fg : (n.is_retracted ? '#D55E00' : ROLE_COLORS[n.role] || '#56B4E9');
          ctx.lineWidth = isSel ? 2.5 : 1.5;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, rad, 0, Math.PI * 2);
        ctx.fillStyle = n.is_retracted ? '#D55E00' : (ROLE_COLORS[n.role] || '#56B4E9');
        ctx.fill();

        // Compact direct label for seeds, hovered/selected, or high-overlap roots
        if (isSel || isHov || n.role === 'seed' || (n.seed_overlap || 0) >= 2) {
          const firstAuthor = (n.authors && n.authors[0]) ? n.authors[0].split(' ').slice(-1)[0] : 'Paper';
          const shortTitle = (n.title || '').slice(0, 24) + ((n.title || '').length > 24 ? '…' : '');
          const label = `${firstAuthor} ${n.year || ''}`.trim();
          ctx.font = (isSel || n.role === 'seed') ? '600 11px sans-serif' : '10px sans-serif';
          ctx.fillStyle = theme.fg;
          ctx.textAlign = 'center';
          ctx.fillText(label, p.x, p.y - rad - 5);
          if (isSel || isHov) {
            ctx.font = '10px sans-serif';
            ctx.fillStyle = theme.muted;
            ctx.fillText(shortTitle, p.x, p.y + rad + 12);
          }
        }
        ctx.restore();
      });

      ctx.restore();
    }

    function escapeHtml(s) {
      return String(s || '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    function renderInspector() {
      const n = nodeMap.get(selectedId);
      if (!n) {
        inspectorContent.innerHTML = '<p class="text-[var(--muted-foreground)]">Click any paper node to inspect lineage role, citations, TLDR, and links.</p>';
        return;
      }
      const roleColor = ROLE_COLORS[n.role] || '#56B4E9';
      const authorsStr = (n.authors || []).slice(0, 6).join(', ') + ((n.authors || []).length > 6 ? ' et al.' : '');
      const surname = (n.authors && n.authors[0]) ? n.authors[0].split(' ').slice(-1)[0].toLowerCase().replace(/[^a-z]/g, '') : 'paper';
      const firstWord = ((n.title || 'work').toLowerCase().match(/[a-z0-9]+/) || ['work'])[0];
      const bibKey = `${surname}${n.year || ''}${firstWord}`;
      const extUrl = n.doi ? `https://doi.org/${n.doi}` : (n.arxiv_id ? `https://arxiv.org/abs/${n.arxiv_id}` : (n.url || ''));

      const connectedSeeds = [];
      edges.forEach(e => {
        if (e.source === n.canonical_id && nodeMap.get(e.target)?.role === 'seed') connectedSeeds.push(nodeMap.get(e.target).title);
        if (e.target === n.canonical_id && nodeMap.get(e.source)?.role === 'seed') connectedSeeds.push(nodeMap.get(e.source).title);
      });

      let html = `
        <div class="flex items-center justify-between gap-2">
          <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded font-medium text-[11px]" style="background:${roleColor}22; color:${roleColor}; border:1px solid ${roleColor}66">
            ${escapeHtml(ROLE_LABELS[n.role] || n.role)}
          </span>
          ${n.is_retracted ? '<span class="px-2 py-0.5 rounded bg-red-600 text-white font-bold text-[11px]">RETRACTED</span>' : ''}
        </div>
        <h3 class="font-semibold text-sm leading-snug text-[var(--foreground)] pt-1">${escapeHtml(n.title)}</h3>
        <p class="text-[var(--muted-foreground)]">${escapeHtml(authorsStr || 'Authors unavailable')}</p>
        <div class="flex flex-wrap gap-x-3 gap-y-1 py-1.5 border-y border-[var(--card-border)] font-mono text-[11px]">
          <span>Year: <strong>${escapeHtml(n.year || 'N/A')}</strong></span>
          <span>Citations: <strong>${Number(n.citation_count || 0).toLocaleString()}</strong></span>
          ${n.influential_citation_count ? `<span>Influential: <strong>${n.influential_citation_count}</strong></span>` : ''}
          ${n.seed_overlap ? `<span>Seed Links: <strong>${n.seed_overlap}</strong></span>` : ''}
        </div>
        <div class="text-[11px] space-y-1">
          <div><span class="text-[var(--muted-foreground)]">Venue:</span> <span class="font-medium">${escapeHtml(n.venue || 'Preprint / Unspecified')}</span> ${n.is_published_venue ? '✓' : '(Preprint)'}</div>
          ${n.doi ? `<div><span class="text-[var(--muted-foreground)]">DOI:</span> <span class="font-mono">${escapeHtml(n.doi)}</span></div>` : ''}
          ${n.arxiv_id ? `<div><span class="text-[var(--muted-foreground)]">arXiv:</span> <span class="font-mono">${escapeHtml(n.arxiv_id)}</span></div>` : ''}
          <div><span class="text-[var(--muted-foreground)]">Suggested Key:</span> <code class="px-1 py-0.5 rounded bg-[var(--background)] font-mono">${escapeHtml(bibKey)}</code></div>
        </div>
      `;
      if (n.tldr) {
        html += `<div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] leading-relaxed"><strong class="text-[var(--foreground)]">TLDR:</strong> <span class="text-[var(--muted-foreground)]">${escapeHtml(n.tldr)}</span></div>`;
      } else if (n.abstract) {
        const shortAbs = n.abstract.length > 340 ? n.abstract.slice(0, 340) + '…' : n.abstract;
        html += `<div class="p-2 rounded bg-[var(--background)] border border-[var(--card-border)] leading-relaxed"><strong class="text-[var(--foreground)]">Abstract:</strong> <span class="text-[var(--muted-foreground)]">${escapeHtml(shortAbs)}</span></div>`;
      }
      if (connectedSeeds.length) {
        html += `<div class="text-[11px] text-[var(--muted-foreground)]"><strong>Connected Seed(s):</strong> ${connectedSeeds.map(escapeHtml).join(' · ')}</div>`;
      }
      const bibType = n.is_published_venue ? ((/conference|proceedings|neurips|iclr|icml|cvpr|acl|emnlp/i).test(n.venue || '') ? 'inproceedings' : 'article') : 'misc';
      const venueLine = n.is_published_venue ? `  ${bibType === 'inproceedings' ? 'booktitle' : 'journal'} = {${n.venue}},\n` : (n.arxiv_id ? `  howpublished = {arXiv preprint arXiv:${n.arxiv_id}},\n` : '');
      const doiLine = n.doi ? `  doi = {${n.doi}},\n` : '';
      const bibTexStr = `@${bibType}{${bibKey},\n  title = {${n.title || ''}},\n  author = {${(n.authors || ['Unknown']).join(' and ')}},\n${venueLine}  year = {${n.year || ''}},\n${doiLine}}`;

      html += `<div class="pt-1 flex flex-wrap items-center gap-2">`;
      if (extUrl) {
        html += `<a href="${escapeHtml(extUrl)}" target="_blank" rel="noopener noreferrer" class="inline-block px-2.5 py-1 rounded bg-[var(--primary)] text-[var(--primary-foreground)] font-medium hover:opacity-90">Open Paper ↗</a>`;
      }
      html += `<button id="btnCopyBib" type="button" class="px-2 py-1 rounded border border-[var(--border)] bg-[var(--background)] text-[var(--foreground)] hover:opacity-90">Copy BibTeX</button></div>`;
      inspectorContent.innerHTML = html;

      const copyBtn = document.getElementById('btnCopyBib');
      if (copyBtn && navigator.clipboard) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(bibTexStr).then(() => {
            copyBtn.textContent = 'Copied ✓';
            setTimeout(() => { copyBtn.textContent = 'Copy BibTeX'; }, 1400);
          });
        });
      }
    }

    function hitTest(sx, sy) {
      const visSet = new Set(nodes.filter(isNodeVisible).map(n => n.canonical_id));
      for (let i = nodes.length - 1; i >= 0; i--) {
        const n = nodes[i];
        if (!visSet.has(n.canonical_id)) continue;
        const p = worldToScreen(n.x, n.y);
        const rad = n.r * Math.min(1.6, Math.max(0.8, Math.sqrt(cam.k))) + 4;
        const dx = sx - p.x, dy = sy - p.y;
        if (dx * dx + dy * dy <= rad * rad) return n;
      }
      return null;
    }

    canvas.addEventListener('mousedown', e => {
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      lastMouse = { x: sx, y: sy };
      const hit = hitTest(sx, sy);
      if (hit) {
        selectedId = hit.canonical_id;
        dragNode = hit;
        renderInspector();
        draw();
      } else {
        isDragging = true;
      }
    });

    window.addEventListener('mousemove', e => {
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      if (dragNode) {
        const wPos = screenToWorld(sx, sy);
        dragNode.x = wPos.x;
        dragNode.y = wPos.y;
        draw();
        return;
      }
      if (isDragging) {
        cam.x += sx - lastMouse.x;
        cam.y += sy - lastMouse.y;
        lastMouse = { x: sx, y: sy };
        draw();
        return;
      }
      if (sx >= 0 && sy >= 0 && sx <= rect.width && sy <= rect.height) {
        const hit = hitTest(sx, sy);
        const nextHov = hit ? hit.canonical_id : null;
        if (nextHov !== hoveredId) {
          hoveredId = nextHov;
          canvas.style.cursor = hoveredId ? 'pointer' : 'grab';
          draw();
        }
      }
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
      dragNode = null;
    });

    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
      const zoom = e.deltaY < 0 ? 1.12 : 0.89;
      const nextK = Math.max(0.45, Math.min(3.5, cam.k * zoom));
      cam.x = sx - ((sx - cam.x) / cam.k) * nextK;
      cam.y = sy - ((sy - cam.y) / cam.k) * nextK;
      cam.k = nextK;
      draw();
    }, { passive: false });

    document.querySelectorAll('.role-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        activeRole = btn.dataset.role;
        document.querySelectorAll('.role-btn').forEach(b => {
          const on = b.dataset.role === activeRole;
          b.className = on
            ? 'role-btn px-2.5 py-1 rounded font-medium bg-[var(--primary)] text-[var(--primary-foreground)]'
            : 'role-btn px-2 py-1 rounded border border-[var(--border)] text-[var(--foreground)] hover:bg-[var(--card)]';
        });
        draw();
      });
    });

    document.getElementById('searchBox').addEventListener('input', e => {
      searchQuery = e.target.value.trim().toLowerCase();
      draw();
    });

    const btnTimeline = document.getElementById('btnTimeline');
    const btnForce = document.getElementById('btnForce');
    btnTimeline.addEventListener('click', () => {
      layoutMode = 'timeline';
      cam = { x: 0, y: 0, k: 1 };
      btnTimeline.className = 'px-2 py-1 bg-[var(--primary)] text-[var(--primary-foreground)] font-medium';
      btnForce.className = 'px-2 py-1 bg-[var(--card)] text-[var(--muted-foreground)]';
      applyActiveCoords();
      draw();
    });
    btnForce.addEventListener('click', () => {
      layoutMode = 'force';
      cam = { x: 0, y: 0, k: 1 };
      btnForce.className = 'px-2 py-1 bg-[var(--primary)] text-[var(--primary-foreground)] font-medium';
      btnTimeline.className = 'px-2 py-1 bg-[var(--card)] text-[var(--muted-foreground)]';
      applyActiveCoords();
      draw();
    });
    document.getElementById('btnReset').addEventListener('click', () => {
      cam = { x: 0, y: 0, k: 1 };
      computeLayouts();
      draw();
    });

    window.addEventListener('resize', () => { computeLayouts(); draw(); });
    window.addEventListener('themechange', draw);

    requestAnimationFrame(() => {
      computeLayouts();
      renderInspector();
      draw();
    });
  </script>
</body>
</html>
"""


def render_html(graph_data: dict, mode: str = "standalone", title: str = "Citation Lineage Map") -> str:
    compact_nodes = []
    for n in graph_data.get("nodes", []):
        compact_nodes.append(
            {
                "canonical_id": n.get("canonical_id"),
                "role": n.get("role", "semantic_sibling"),
                "title": n.get("title"),
                "authors": (n.get("authors") or [])[:8],
                "year": n.get("year"),
                "venue": n.get("venue"),
                "is_published_venue": bool(n.get("is_published_venue")),
                "doi": n.get("doi"),
                "arxiv_id": n.get("arxiv_id"),
                "citation_count": n.get("citation_count", 0),
                "influential_citation_count": n.get("influential_citation_count", 0),
                "seed_overlap": n.get("seed_overlap", 0),
                "is_retracted": bool(n.get("is_retracted")),
                "tldr": n.get("tldr"),
                "abstract": (n.get("abstract") or "")[:450] if not n.get("tldr") else None,
                "url": n.get("url"),
            }
        )

    payload = {
        "seeds": [{"canonical_id": s.get("canonical_id")} for s in graph_data.get("seeds", [])],
        "nodes": compact_nodes,
        "edges": graph_data.get("edges", []),
    }

    if mode == "inline":
        body_class = "bg-transparent text-[var(--foreground)] antialiased p-0 m-0"
        wrapper_class = "py-1.5 space-y-2"
        grid_class = "grid-cols-1 md:grid-cols-3"
        canvas_height = "345"
    else:
        body_class = "bg-[var(--background)] text-[var(--foreground)] antialiased p-4 m-0"
        wrapper_class = "max-w-7xl mx-auto space-y-3"
        grid_class = "grid-cols-1 lg:grid-cols-3"
        canvas_height = "560"

    # Replace CANVAS_HEIGHT on canvas vs inspector cleanly: canvas gets col-span-2!
    html = (
        HTML_TEMPLATE.replace("__TITLE__", title)
        .replace("__BODY_CLASS__", body_class)
        .replace("__WRAPPER_CLASS__", wrapper_class)
        .replace("__GRID_CLASS__", grid_class)
        .replace("__CANVAS_HEIGHT__", canvas_height)
        .replace("__TOTAL_NODES__", str(len(compact_nodes)))
        .replace("__GRAPH_JSON__", json.dumps(payload, ensure_ascii=False))
    )
    # Give canvas 2/3 width on multi-column layout
    html = html.replace(
        'class="relative rounded border border-[var(--card-border)] bg-[var(--card)] overflow-hidden"',
        'class="relative md:col-span-2 lg:col-span-2 rounded border border-[var(--card-border)] bg-[var(--card)] overflow-hidden"',
    )
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Render interactive citation map HTML from lineage JSON.")
    parser.add_argument("graph_json", help="Input JSON generated by scholarly_graph.py lineage")
    parser.add_argument("--output", "-o", required=True, help="Output HTML file path")
    parser.add_argument(
        "--mode",
        choices=["standalone", "inline"],
        default="standalone",
        help="standalone (560px side-pane explorer) or inline (<=395px total height for <agent-embed>)",
    )
    parser.add_argument("--title", default="Citation Lineage & Discovery Map", help="Document title")
    args = parser.parse_args()

    data = json.loads(Path(args.graph_json).expanduser().read_text(encoding="utf-8"))
    html = render_html(data, mode=args.mode, title=args.title)
    out = Path(args.output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Rendered {args.mode} interactive citation map ({len(data.get('nodes', []))} nodes) -> {out}")


if __name__ == "__main__":
    main()
