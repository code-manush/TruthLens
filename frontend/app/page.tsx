'use client';
import Link from 'next/link';
import dynamic from 'next/dynamic';

const NetworkCanvas = dynamic(() => import('@/components/NetworkCanvas'), { ssr: false });

export default function LandingPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Navbar ───────────────────────────────────────────────── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(248,247,244,0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid #E8E5DE',
        padding: '0 32px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: '60px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '30px', height: '30px', borderRadius: '8px',
            background: '#1B3A6B', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
          </div>
          <span style={{ fontFamily: 'Playfair Display, serif', fontWeight: 700, fontSize: '18px', color: '#18181B', letterSpacing: '-0.02em' }}>
            TruthLens
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
          <a href="#how" style={{ fontSize: '13px', color: '#71717A', textDecoration: 'none' }}>How it works</a>
          <a href="#features" style={{ fontSize: '13px', color: '#71717A', textDecoration: 'none' }}>Features</a>
          <a href="https://github.com/TruthLens" target="_blank" rel="noreferrer" style={{ fontSize: '13px', color: '#71717A', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Extension
          </a>
          <Link href="/analyze" style={{
            fontSize: '13px', fontWeight: 500, color: '#FFFFFF',
            background: '#1B3A6B', padding: '7px 18px', borderRadius: '8px',
            textDecoration: 'none', letterSpacing: '-0.01em',
          }}>
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section style={{ position: 'relative', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '96px 24px 80px', background: '#F8F7F4', overflow: 'hidden', minHeight: '560px' }}>
        <NetworkCanvas />
        <div style={{ position: 'relative', zIndex: 2, maxWidth: '600px', textAlign: 'center' }}>
          <p className="fade-up" style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#1B3A6B', marginBottom: '20px' }}>
            Multi-Modal Disinformation Detection
          </p>
          <h1 className="fade-up-d1 serif" style={{ fontSize: 'clamp(52px,8vw,80px)', fontWeight: 700, color: '#18181B', lineHeight: 1.05, letterSpacing: '-0.03em', marginBottom: '20px' }}>
            TruthLens
          </h1>
          <p className="fade-up-d2" style={{ fontSize: '16px', color: '#52525B', lineHeight: 1.7, marginBottom: '36px', maxWidth: '460px', margin: '0 auto 36px' }}>
            Paste any article link or text. Our AI verifies claims against 50+ live sources and returns a detailed, explainable credibility scorecard.
          </p>
          <div className="fade-up-d3" style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/analyze" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              padding: '12px 28px', background: '#1B3A6B', color: '#FFFFFF',
              borderRadius: '10px', fontSize: '14px', fontWeight: 500,
              textDecoration: 'none', letterSpacing: '-0.01em',
            }}>
              Analyze an article
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
              </svg>
            </Link>
            <a href="https://github.com/TruthLens" target="_blank" rel="noreferrer" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              padding: '12px 24px', border: '1px solid #D4D0C8', color: '#52525B',
              borderRadius: '10px', fontSize: '14px', fontWeight: 500,
              textDecoration: 'none', background: '#FFFFFF',
            }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Download Extension
            </a>
          </div>
        </div>
      </section>

      {/* ── Divider ──────────────────────────────────────────────── */}
      <div style={{ background: '#F2F0EC', borderTop: '1px solid #E8E5DE', borderBottom: '1px solid #E8E5DE', padding: '16px 40px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '32px', flexWrap: 'wrap' }}>
        {[['NLP Classification', 'Fact & claim extraction'], ['Deepfake Detection', 'Visual media analysis'], ['Live Verification', 'Tavily web search'], ['PDF Scorecard', 'Downloadable report']].map(([t, s]) => (
          <div key={t} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '13px', fontWeight: 500, color: '#18181B' }}>{t}</div>
            <div style={{ fontSize: '11px', color: '#A1A1AA', marginTop: '1px' }}>{s}</div>
          </div>
        ))}
      </div>

      {/* ── How It Works ─────────────────────────────────────────── */}
      <section id="how" style={{ background: '#FFFFFF', padding: '80px 24px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '56px' }}>
            <h2 className="serif" style={{ fontSize: '36px', fontWeight: 700, color: '#18181B', marginBottom: '12px', letterSpacing: '-0.02em' }}>
              How it works
            </h2>
            <p style={{ fontSize: '15px', color: '#71717A', maxWidth: '400px', margin: '0 auto' }}>
              A four-stage AI pipeline that goes from raw URL to verified credibility score.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '2px' }}>
            {[
              { n: '01', t: 'Paste URL or Text',   d: 'Drop in any article link, or paste the full article text directly.' },
              { n: '02', t: 'AI Extraction',         d: 'Ollama qwen3:8b identifies the context, separates relevant from irrelevant facts, and detects bias.' },
              { n: '03', t: 'Web Verification',      d: 'Tavily searches 50+ live news sources and scores corroboration from Tier-1 outlets.' },
              { n: '04', t: 'Credibility Scorecard', d: 'A weighted five-dimension score with red flags, positive signals, and PDF download.' },
            ].map(({ n, t, d }) => (
              <div key={n} style={{ padding: '28px 24px', background: '#F8F7F4', borderRadius: '2px' }}>
                <div style={{ fontFamily: 'Playfair Display, serif', fontSize: '28px', fontWeight: 700, color: '#E8E5DE', marginBottom: '10px', lineHeight: 1 }}>{n}</div>
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#18181B', marginBottom: '8px' }}>{t}</h3>
                <p style={{ fontSize: '13px', color: '#71717A', lineHeight: 1.6 }}>{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────── */}
      <section id="features" style={{ background: '#F8F7F4', padding: '80px 24px', borderTop: '1px solid #E8E5DE' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '56px' }}>
            <h2 className="serif" style={{ fontSize: '36px', fontWeight: 700, color: '#18181B', marginBottom: '12px', letterSpacing: '-0.02em' }}>
              What we detect
            </h2>
            <p style={{ fontSize: '15px', color: '#71717A', maxWidth: '400px', margin: '0 auto' }}>
              Built for journalists, researchers, and anyone who wants to verify what they read online.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '16px' }}>
            {[
              {
                title: 'NLP Credibility Scoring',
                desc: 'AI context-awareness separates relevant facts from off-context filler. Detects emotional language, bias, and clickbait patterns.',
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1B3A6B" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
                  </svg>
                ),
              },
              {
                title: 'Live Source Corroboration',
                desc: 'Cross-references 50+ live web sources in real-time. Tier-1 outlets (Reuters/BBC) carry higher weight in the credibility score.',
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1B3A6B" strokeWidth="1.8" strokeLinecap="round">
                    <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                  </svg>
                ),
              },
              {
                title: 'Ad & Clickbait Analysis',
                desc: 'Detects low-quality ad networks (Taboola, Outbrain) and excessive ad density — key signals of clickbait or monetization-driven content.',
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1B3A6B" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                ),
              },
            ].map(({ title, desc, icon }) => (
              <div key={title} style={{
                background: '#FFFFFF', border: '1px solid #E8E5DE',
                borderRadius: '12px', padding: '24px',
              }}>
                <div style={{
                  width: '38px', height: '38px', background: '#EEF2FA', borderRadius: '10px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px',
                }}>
                  {icon}
                </div>
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#18181B', marginBottom: '8px' }}>{title}</h3>
                <p style={{ fontSize: '13px', color: '#71717A', lineHeight: 1.65 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────── */}
      <section style={{ background: '#1B3A6B', padding: '72px 24px', textAlign: 'center' }}>
        <h2 className="serif" style={{ fontSize: '38px', fontWeight: 700, color: '#FFFFFF', marginBottom: '14px', letterSpacing: '-0.02em' }}>
          Don&apos;t trust — verify.
        </h2>
        <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.65)', marginBottom: '32px', maxWidth: '380px', margin: '0 auto 32px' }}>
          Paste any article and get a credibility scorecard in minutes.
        </p>
        <Link href="/analyze" style={{
          display: 'inline-flex', alignItems: 'center', gap: '8px',
          padding: '13px 30px', background: '#FFFFFF', color: '#1B3A6B',
          borderRadius: '10px', fontSize: '14px', fontWeight: 600,
          textDecoration: 'none',
        }}>
          Start analyzing
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
          </svg>
        </Link>
      </section>

      {/* ── Footer ───────────────────────────────────────────────── */}
      <footer style={{ background: '#FFFFFF', borderTop: '1px solid #E8E5DE', padding: '28px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '24px', height: '24px', borderRadius: '6px', background: '#1B3A6B', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          </div>
          <span style={{ fontFamily: 'Playfair Display, serif', fontSize: '15px', fontWeight: 700, color: '#18181B' }}>TruthLens</span>
        </div>
        <p style={{ fontSize: '12px', color: '#A1A1AA' }}>
          Multi-Modal Disinformation Detection · Powered by Ollama + Tavily
        </p>
      </footer>
    </div>
  );
}
