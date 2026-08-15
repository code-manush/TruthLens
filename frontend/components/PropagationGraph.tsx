'use client';
import { useEffect, useRef, useState } from 'react';
import type { CredibilityScorecard } from '@/lib/types';
import { buildGraphFromScorecard, type GraphNodeData } from '@/lib/credible_sources';

interface Props {
  sc: CredibilityScorecard;
}

// ─────────────────────────────────────────────────────────────────────────────
// Tooltip state
// ─────────────────────────────────────────────────────────────────────────────

interface TooltipState {
  x: number;
  y: number;
  node: GraphNodeData;
} 

// ─────────────────────────────────────────────────────────────────────────────
// Custom canvas node painter
// ─────────────────────────────────────────────────────────────────────────────

function paintNode(
  node: GraphNodeData,
  ctx: CanvasRenderingContext2D,
  globalScale: number,
) {
  // Guard: skip rendering until the force simulation assigns finite positions
  if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;

  const r        = (node.isSource ? 9 : node.credScore && node.credScore >= 70 ? 5 : 4) / Math.sqrt(Math.max(globalScale, 0.3));
  const fontSize = Math.max(8, (node.isSource ? 12 : 9) / globalScale);

  // Glow / halo for the source node
  if (node.isSource) {
    const g = ctx.createRadialGradient(node.x!, node.y!, 0, node.x!, node.y!, r * 3);
    g.addColorStop(0, node.color + '55');
    g.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(node.x!, node.y!, r * 3, 0, 2 * Math.PI);
    ctx.fillStyle = g;
    ctx.fill();
  }

  // Main dot
  ctx.beginPath();
  ctx.arc(node.x!, node.y!, r, 0, 2 * Math.PI);
  ctx.fillStyle = node.color;
  ctx.fill();

  // Ring
  ctx.strokeStyle = node.isSource ? '#ffffff' : node.color + 'cc';
  ctx.lineWidth   = (node.isSource ? 1.8 : 1) / globalScale;
  ctx.stroke();

  // Label — only draw when zoomed in enough to be readable
  if (globalScale > 0.45) {
    const label  = node.label.length > 22 ? node.label.slice(0, 20) + '…' : node.label;
    ctx.font     = `${node.isSource ? 'bold ' : ''}${fontSize}px Inter, system-ui, sans-serif`;
    ctx.fillStyle = node.isSource ? '#ffffff' : 'rgba(240,240,240,0.85)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(label, node.x!, node.y! + r + 2 / globalScale);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export default function PropagationGraph({ sc }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef        = useRef<any>(null);
  const [ForceGraph, setForceGraph] = useState<any>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 380 });
  const [tooltip, setTooltip]       = useState<TooltipState | null>(null);
  const graphData = buildGraphFromScorecard(sc);

  // ── Lazy-load the browser-only library ────────────────────────────────────
  useEffect(() => {
    import('react-force-graph-2d').then(mod => {
      setForceGraph(() => mod.default);
    });
  }, []);

  // ── Measure container ──────────────────────────────────────────────────────
  useEffect(() => {
    const measure = () => {
      if (containerRef.current) {
        setDimensions({
          width:  containerRef.current.offsetWidth,
          height: 380,
        });
      }
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  // ── Zoom-to-fit after simulation settles ──────────────────────────────────
  useEffect(() => {
    const t = setTimeout(() => {
      fgRef.current?.zoomToFit(500, 32);
    }, 700);
    return () => clearTimeout(t);
  }, [graphData, ForceGraph]);

  // ── Counts for header ─────────────────────────────────────────────────────
  const credibleCount    = graphData.nodes.filter(n => !n.isSource && n.color === '#22c55e').length;
  const nonCredibleCount = graphData.nodes.filter(n => !n.isSource && n.color === '#ef4444').length;

  return (
    <div style={{ marginTop: '20px' }}>
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
          borderRadius: '12px',
          overflow: 'hidden',
          background: '#0d0f18',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.04)',
        }}
      >
        {/* Legend */}
        <div style={{
          position: 'absolute', top: '10px', left: '12px', zIndex: 10,
          display: 'flex', gap: '14px', alignItems: 'center',
          background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(6px)',
          borderRadius: '8px', padding: '6px 12px',
          border: '1px solid rgba(255,255,255,0.07)',
        }}>
          <span style={{ fontSize: '10px', fontWeight: 600, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Sources
          </span>
          <LegendDot color="#22c55e" label={`${credibleCount} credible`} />
          <LegendDot color="#ef4444" label={`${nonCredibleCount} unverified`} />
        </div>

        {/* Controls hint */}
        <div style={{
          position: 'absolute', bottom: '10px', right: '12px', zIndex: 10,
          fontSize: '10px', color: 'rgba(255,255,255,0.28)', letterSpacing: '0.03em',
          background: 'rgba(0,0,0,0.4)', padding: '4px 8px', borderRadius: '6px',
        }}>
          Drag · Scroll to zoom · Hover for info
        </div>

        {/* Tooltip */}
        {tooltip && (
          <div style={{
            position: 'absolute',
            left: tooltip.x + 14,
            top:  tooltip.y - 10,
            zIndex: 20,
            pointerEvents: 'none',
            background: 'rgba(10,12,22,0.95)',
            border: `1px solid ${tooltip.node.color}55`,
            borderRadius: '8px',
            padding: '8px 12px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
            minWidth: '180px',
          }}>
            <p style={{ fontSize: '12px', fontWeight: 600, color: tooltip.node.isSource ? '#ffffff' : tooltip.node.color, marginBottom: '3px' }}>
              {tooltip.node.isSource ? '◉ ' : '● '}{tooltip.node.label}
            </p>
            <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.55)', marginBottom: '4px' }}>
              {tooltip.node.credLabel}
            </p>
            {tooltip.node.credScore !== null ? (
              <p style={{ fontSize: '11px', color: tooltip.node.color, fontWeight: 600 }}>
                Registry score: {tooltip.node.credScore}/100
              </p>
            ) : (
              <p style={{ fontSize: '11px', color: '#ef4444' }}>
                Not in credibility registry
              </p>
            )}
            {tooltip.node.isSource && (
              <p style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', marginTop: '3px', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '4px' }}>
                Article source
              </p>
            )}
          </div>
        )}

        {/* Force graph */}
        {!ForceGraph ? (
          <div style={{
            height: 380, display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'rgba(255,255,255,0.3)', fontSize: '13px', gap: '8px',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" style={{ animation: 'spin 1s linear infinite' }}>
              <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
            Loading graph…
          </div>
        ) : dimensions.width > 0 ? (
          <ForceGraph
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            backgroundColor="#0d0f18"
            nodeCanvasObject={(node: GraphNodeData, ctx: CanvasRenderingContext2D, scale: number) =>
              paintNode(node, ctx, scale)
            }
            nodeCanvasObjectMode={() => 'replace'}
            linkColor={(l: any) => l.color}
            linkWidth={1}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkDirectionalArrowColor={(l: any) => l.color.replace('0.25', '0.5').replace('0.15', '0.35').replace('0.10', '0.25')}
            onNodeHover={(node: GraphNodeData | null, _: any, event: MouseEvent) => {
              if (!node) { setTooltip(null); return; }
              const rect = containerRef.current?.getBoundingClientRect();
              if (!rect) return;
              setTooltip({
                x: (event?.clientX ?? 0) - rect.left,
                y: (event?.clientY ?? 0) - rect.top,
                node,
              });
            }}
            onNodeClick={(node: GraphNodeData) => {
              // Zoom into clicked node
              fgRef.current?.centerAt(node.x, node.y, 600);
              fgRef.current?.zoom(4, 600);
            }}
            onBackgroundClick={() => {
              setTooltip(null);
              fgRef.current?.zoomToFit(500, 32);
            }}
            cooldownTicks={120}
            onEngineStop={() => fgRef.current?.zoomToFit(500, 32)}
            nodePointerAreaPaint={(node: GraphNodeData, color: string, ctx: CanvasRenderingContext2D) => {
              const r = (node.isSource ? 14 : 9);
              ctx.beginPath();
              ctx.arc(node.x!, node.y!, r, 0, 2 * Math.PI);
              ctx.fillStyle = color;
              ctx.fill();
            }}
          />
        ) : null}
      </div>

      {/* Caption */}
      <p style={{ fontSize: '11px', color: '#A1A1AA', marginTop: '8px', lineHeight: 1.5 }}>
        Center node = article source. Green = credible (registry score ≥ 70). Red = unverified or below threshold.
        Click a node to focus; scroll to zoom; drag to explore.
      </p>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
      <div style={{
        width: '8px', height: '8px', borderRadius: '50%',
        background: color, flexShrink: 0,
        boxShadow: `0 0 6px ${color}88`,
      }} />
      <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.55)', whiteSpace: 'nowrap' }}>
        {label}
      </span>
    </div>
  );
}
