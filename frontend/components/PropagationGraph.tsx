'use client';
import { useEffect, useRef, useState, useCallback } from 'react';
import type { CredibilityScorecard } from '@/lib/types';
import { buildGraphFromScorecard, type GraphNodeData } from '@/lib/credible_sources';

interface Props {
  sc: CredibilityScorecard;
}

// ─────────────────────────────────────────────────────────────────────────────
// Node info panel (replaces tooltip — shown on click, pinned to side)
// ─────────────────────────────────────────────────────────────────────────────
interface InfoPanel {
  node: GraphNodeData;
}

// ─────────────────────────────────────────────────────────────────────────────
// Custom canvas painter — stable, readable at all zoom levels
// ─────────────────────────────────────────────────────────────────────────────
function paintNode(
  node: GraphNodeData,
  ctx: CanvasRenderingContext2D,
  globalScale: number,
  selectedId: number | null,
) {
  if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;

  const isSelected = node.id === selectedId;
  const baseR      = node.isSource ? 10 : 6;
  const r          = baseR / Math.sqrt(Math.max(globalScale, 0.4));
  const fontSize   = Math.max(9, (node.isSource ? 13 : 10) / globalScale);

  // Outer glow for source OR selected node
  if (node.isSource || isSelected) {
    const glowR = r * (isSelected ? 3.5 : 3);
    const g = ctx.createRadialGradient(node.x!, node.y!, 0, node.x!, node.y!, glowR);
    g.addColorStop(0, node.color + (isSelected ? '70' : '50'));
    g.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(node.x!, node.y!, glowR, 0, 2 * Math.PI);
    ctx.fillStyle = g;
    ctx.fill();
  }

  // Main circle
  ctx.beginPath();
  ctx.arc(node.x!, node.y!, r, 0, 2 * Math.PI);
  ctx.fillStyle = node.color;
  ctx.fill();

  // Ring
  ctx.strokeStyle = isSelected ? '#ffffff' : (node.isSource ? '#ffffff' : node.color + 'bb');
  ctx.lineWidth   = (isSelected ? 2.5 : node.isSource ? 2 : 1) / globalScale;
  ctx.stroke();

  // Label — only when zoomed in enough
  if (globalScale > 0.5) {
    const rawLabel = node.label;
    const label    = rawLabel.length > 24 ? rawLabel.slice(0, 22) + '…' : rawLabel;
    ctx.font        = `${node.isSource || isSelected ? '700' : '400'} ${fontSize}px Inter,system-ui,sans-serif`;
    ctx.fillStyle   = '#ffffff';
    ctx.textAlign   = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(label, node.x!, node.y! + r + 2 / globalScale);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────
export default function PropagationGraph({ sc }: Props) {
  const containerRef   = useRef<HTMLDivElement>(null);
  const fgRef          = useRef<any>(null);
  const [ForceGraph, setForceGraph] = useState<any>(null);
  const [width, setWidth]           = useState(0);
  const [infoPanel, setInfoPanel]   = useState<InfoPanel | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Build graph data once per scorecard
  const graphData = buildGraphFromScorecard(sc);

  const credibleCount    = graphData.nodes.filter(n => !n.isSource && n.color === '#22c55e').length;
  const nonCredibleCount = graphData.nodes.filter(n => !n.isSource && n.color === '#ef4444').length;

  // ── Load library (browser-only) ────────────────────────────────────────────
  useEffect(() => {
    import('react-force-graph-2d').then(mod => setForceGraph(() => mod.default));
  }, []);

  // ── Measure container width responsively ──────────────────────────────────
  useEffect(() => {
    const measure = () => {
      if (containerRef.current) setWidth(containerRef.current.offsetWidth);
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  // ── Zoom-to-fit once simulation settles ───────────────────────────────────
  useEffect(() => {
    const t = setTimeout(() => fgRef.current?.zoomToFit(600, 40), 800);
    return () => clearTimeout(t);
  }, [ForceGraph, graphData]);

  // ── Node click: show pinned info panel ────────────────────────────────────
  const handleNodeClick = useCallback((node: GraphNodeData) => {
    if (selectedId === node.id) {
      // toggle off
      setSelectedId(null);
      setInfoPanel(null);
    } else {
      setSelectedId(node.id);
      setInfoPanel({ node });
      // gentle center (no aggressive zoom)
      fgRef.current?.centerAt(node.x, node.y, 500);
    }
  }, [selectedId]);

  const closePanel = useCallback(() => {
    setSelectedId(null);
    setInfoPanel(null);
  }, []);

  // ── Escape key closes panel ────────────────────────────────────────────────
  useEffect(() => {
    const fn = (e: KeyboardEvent) => { if (e.key === 'Escape') closePanel(); };
    window.addEventListener('keydown', fn);
    return () => window.removeEventListener('keydown', fn);
  }, [closePanel]);

  const HEIGHT = 400;

  return (
    <div style={{ marginTop: '24px' }}>
      {/* Section header */}
      <p style={{
        fontSize: '11px', fontWeight: 600, color: '#A1A1AA',
        textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px',
      }}>
        Source Verification Network
      </p>

      {/* Graph panel */}
      <div
        ref={containerRef}
        style={{
          position: 'relative',
          width: '100%',
          height: `${HEIGHT}px`,
          borderRadius: '12px',
          overflow: 'hidden',
          background: '#0d0f18',
          border: '1px solid rgba(255,255,255,0.09)',
        }}
      >
        {/* ── Legend ──────────────────────────────────────────────────────── */}
        <div style={{
          position: 'absolute', top: '10px', left: '12px', zIndex: 10,
          display: 'flex', gap: '12px', alignItems: 'center',
          background: 'rgba(0,0,0,0.60)', backdropFilter: 'blur(8px)',
          borderRadius: '8px', padding: '5px 11px',
          border: '1px solid rgba(255,255,255,0.07)',
        }}>
          <span style={{ fontSize: '9px', fontWeight: 700, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Sources</span>
          <LegendDot color="#22c55e" label={`${credibleCount} credible`} />
          <LegendDot color="#ef4444" label={`${nonCredibleCount} unverified`} />
        </div>

        {/* ── Controls hint ───────────────────────────────────────────────── */}
        <div style={{
          position: 'absolute', bottom: '10px', right: '12px', zIndex: 10,
          fontSize: '10px', color: 'rgba(255,255,255,0.25)',
          background: 'rgba(0,0,0,0.45)', padding: '3px 8px', borderRadius: '5px',
        }}>
          Drag · Scroll to zoom · Click node for details
        </div>

        {/* ── Background-click reset button ───────────────────────────────── */}
        {infoPanel && (
          <button
            onClick={closePanel}
            style={{
              position: 'absolute', top: '10px', right: '12px', zIndex: 15,
              background: 'rgba(0,0,0,0.60)', border: '1px solid rgba(255,255,255,0.12)',
              color: 'rgba(255,255,255,0.7)', borderRadius: '6px',
              padding: '4px 10px', fontSize: '11px', cursor: 'pointer',
              backdropFilter: 'blur(6px)',
            }}
          >
            ✕ Close
          </button>
        )}

        {/* ── Pinned info panel (shown on node click) ─────────────────────── */}
        {infoPanel && (
          <div style={{
            position: 'absolute', bottom: '36px', left: '12px', zIndex: 20,
            background: 'rgba(10,12,22,0.97)',
            border: `1px solid ${infoPanel.node.color}44`,
            borderRadius: '10px',
            padding: '14px 16px',
            boxShadow: `0 8px 32px rgba(0,0,0,0.7), 0 0 0 1px ${infoPanel.node.color}22`,
            width: '240px',
            backdropFilter: 'blur(12px)',
          }}>
            {/* Node type badge */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '5px',
              marginBottom: '8px',
              padding: '2px 8px', borderRadius: '20px',
              background: infoPanel.node.color + '22',
              border: `1px solid ${infoPanel.node.color}44`,
            }}>
              <div style={{
                width: '6px', height: '6px', borderRadius: '50%',
                background: infoPanel.node.color,
                boxShadow: `0 0 6px ${infoPanel.node.color}`,
              }} />
              <span style={{ fontSize: '9px', fontWeight: 700, color: infoPanel.node.color, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                {infoPanel.node.isSource ? 'Article Source' : infoPanel.node.color === '#22c55e' ? 'Credible Source' : 'Unverified Source'}
              </span>
            </div>

            {/* Domain name */}
            <p style={{ fontSize: '13px', fontWeight: 700, color: '#ffffff', marginBottom: '4px', wordBreak: 'break-all' }}>
              {infoPanel.node.label}
            </p>

            {/* Category label */}
            <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', marginBottom: '10px' }}>
              {infoPanel.node.credLabel}
            </p>

            {/* Score row */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '8px 10px', borderRadius: '7px',
              background: 'rgba(255,255,255,0.05)',
              marginBottom: '10px',
            }}>
              <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.45)' }}>Registry Score</span>
              <span style={{
                marginLeft: 'auto', fontSize: '14px', fontWeight: 700,
                color: infoPanel.node.credScore !== null ? infoPanel.node.color : '#71717A',
              }}>
                {infoPanel.node.credScore !== null ? `${infoPanel.node.credScore}/100` : 'Not listed'}
              </span>
            </div>

            {/* Clickable link */}
            <a
              href={`https://${infoPanel.node.label}`}
              target="_blank"
              rel="noreferrer noopener"
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                fontSize: '11px', color: '#60A5FA',
                textDecoration: 'none',
                padding: '6px 10px', borderRadius: '6px',
                background: 'rgba(96,165,250,0.10)',
                border: '1px solid rgba(96,165,250,0.20)',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(96,165,250,0.18)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'rgba(96,165,250,0.10)')}
            >
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              Visit {infoPanel.node.label}
            </a>

            {infoPanel.node.isSource && sc.url && (
              <a
                href={sc.url}
                target="_blank"
                rel="noreferrer noopener"
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  fontSize: '11px', color: '#A78BFA',
                  textDecoration: 'none',
                  padding: '6px 10px', borderRadius: '6px',
                  background: 'rgba(167,139,250,0.10)',
                  border: '1px solid rgba(167,139,250,0.20)',
                  marginTop: '6px',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(167,139,250,0.18)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(167,139,250,0.10)')}
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                Open analyzed article ↗
              </a>
            )}
          </div>
        )}

        {/* ── Loading state ────────────────────────────────────────────────── */}
        {!ForceGraph && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'rgba(255,255,255,0.3)', fontSize: '13px', gap: '8px',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" style={{ animation: 'spin 1s linear infinite' }}>
              <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
            Loading graph…
          </div>
        )}

        {/* ── Force graph ──────────────────────────────────────────────────── */}
        {ForceGraph && width > 0 && (
          <ForceGraph
            ref={fgRef}
            width={width}
            height={HEIGHT}
            graphData={graphData}
            backgroundColor="#0d0f18"

            // ── Node painting ─────────────────────────────────────────────
            nodeCanvasObject={(node: GraphNodeData, ctx: CanvasRenderingContext2D, scale: number) =>
              paintNode(node, ctx, scale, selectedId)
            }
            nodeCanvasObjectMode={() => 'replace'}

            // Larger hit-zone so clicks register easily
            nodePointerAreaPaint={(node: GraphNodeData, color: string, ctx: CanvasRenderingContext2D, scale: number) => {
              if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
              const r = (node.isSource ? 18 : 13) / Math.sqrt(Math.max(scale, 0.4));
              ctx.beginPath();
              ctx.arc(node.x!, node.y!, r, 0, 2 * Math.PI);
              ctx.fillStyle = color;
              ctx.fill();
            }}

            // ── Links ─────────────────────────────────────────────────────
            linkColor={(l: any) => l.color}
            linkWidth={0.8}
            linkDirectionalArrowLength={3}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowColor={(l: any) => 'rgba(200,200,200,0.35)'}

            // ── Interaction ───────────────────────────────────────────────
            onNodeClick={(node: GraphNodeData) => handleNodeClick(node)}
            onBackgroundClick={() => {
              closePanel();
              fgRef.current?.zoomToFit(600, 40);
            }}

            // ── Simulation physics — calmer, less jittery ─────────────────
            cooldownTicks={150}
            cooldownTime={3000}
            d3AlphaDecay={0.025}
            d3VelocityDecay={0.4}
            onEngineStop={() => fgRef.current?.zoomToFit(600, 40)}

            // ── Min/max zoom ──────────────────────────────────────────────
            minZoom={0.3}
            maxZoom={6}
          />
        )}
      </div>

      {/* Caption */}
      <p style={{ fontSize: '11px', color: '#A1A1AA', marginTop: '8px', lineHeight: 1.5 }}>
        Center node = article source. <span style={{ color: '#22c55e' }}>Green</span> = credible (registry score ≥ 70). <span style={{ color: '#ef4444' }}>Red</span> = unverified or below threshold.
        Click any node to see details and open its link.
      </p>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
      <div style={{
        width: '7px', height: '7px', borderRadius: '50%', background: color, flexShrink: 0,
        boxShadow: `0 0 5px ${color}88`,
      }} />
      <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.5)', whiteSpace: 'nowrap' }}>{label}</span>
    </div>
  );
}
