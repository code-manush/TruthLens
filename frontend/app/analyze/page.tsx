'use client';
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import type { CredibilityScorecard, AnalysisMode } from '@/lib/types';

const LoadingSteps   = dynamic(() => import('@/components/LoadingSteps'),   { ssr: false });
const ScorecardModal = dynamic(() => import('@/components/ScorecardModal'), { ssr: false });

export default function AnalyzePage() {
  const [mode, setMode]     = useState<AnalysisMode>('url');
  const [url, setUrl]       = useState('');
  const [text, setText]     = useState('');
  const [stage, setStage]   = useState<'idle' | 'loading' | 'done' | 'error'>('idle');
  const [step, setStep]     = useState(1);
  const [sc, setSc]         = useState<CredibilityScorecard | null>(null);
  const [error, setError]   = useState('');
  const [show, setShow]     = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const canSubmit = mode === 'url' ? url.trim() !== '' : mode === 'text' ? text.trim().length > 50 : true;

  const submit = async () => {
    setError(''); setStage('loading'); setStep(1);
    const tmr = setInterval(() => setStep((s) => Math.min(s + 1, 3)), 80000);

    try {
      const body: Record<string, string> = {};
      if (mode === 'url')  body.url = url;
      if (mode === 'text') body.text = text;

      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      clearInterval(tmr);

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Unknown server error.' }));
        throw new Error(err.error || `Error ${res.status}`);
      }

      setSc(await res.json());
      setStep(4);
      setStage('done');
      setShow(true);
    } catch (e: any) {
      clearInterval(tmr);
      setStage('error');
      setError(e.message || 'Something went wrong.');
    }
  };

  const reset = () => { setStage('idle'); setStep(1); setSc(null); setShow(false); setError(''); };

  // SVG Icons
  const IconUrl = <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>;
  const IconTxt = <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>;
  const IconImg = <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#F8F7F4', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* ── Navbar ───────────────────────────────────────────────── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(248,247,244,0.85)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid #E8E5DE', padding: '0 32px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '60px',
      }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{ width: '30px', height: '30px', borderRadius: '8px', background: '#1B3A6B', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          </div>
          <span style={{ fontFamily: 'Playfair Display, serif', fontWeight: 700, fontSize: '18px', color: '#18181B', letterSpacing: '-0.02em' }}>
            TruthLens
          </span>
        </Link>
        <span style={{ fontSize: '13px', color: '#71717A', display: 'none' }} className="md:block">Multi-Modal Disinformation Detector</span>
        
        {sc && (
          <button onClick={() => setShow(true)} style={{
            fontSize: '12px', fontWeight: 500, color: '#1B3A6B', background: '#EEF2FA',
            padding: '6px 14px', borderRadius: '6px', border: '1px solid rgba(27,58,107,0.1)', cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: '6px',
          }}>
            View Report <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
        )}
      </nav>

      {/* ── Content ──────────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '64px 24px' }}>
        <div style={{ width: '100%', maxWidth: '580px' }}>

          {stage === 'idle' && (
            <div className="fade-up">
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <h1 className="serif" style={{ fontSize: '32px', fontWeight: 700, color: '#18181B', marginBottom: '8px', letterSpacing: '-0.02em' }}>Verify Content</h1>
                <p style={{ fontSize: '14px', color: '#71717A' }}>Paste a URL, raw text, or upload an image to analyze.</p>
              </div>

              {/* Box */}
              <div style={{ background: '#FFFFFF', border: '1px solid #E8E5DE', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 24px rgba(0,0,0,0.02)' }}>
                {/* Tabs */}
                <div style={{ display: 'flex', borderBottom: '1px solid #E8E5DE' }}>
                  {[
                    { id: 'url', l: 'URL', i: IconUrl },
                    { id: 'text', l: 'Text', i: IconTxt },
                    { id: 'image', l: 'Image', i: IconImg },
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setMode(t.id as AnalysisMode)}
                      style={{
                        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                        padding: '16px', fontSize: '13px', fontWeight: 500, cursor: 'pointer',
                        border: 'none', background: mode === t.id ? '#FAFAFA' : '#FFFFFF',
                        borderBottom: mode === t.id ? '2px solid #1B3A6B' : '2px solid transparent',
                        color: mode === t.id ? '#1B3A6B' : '#71717A', transition: 'all 0.2s',
                      }}
                    >
                      {t.i} {t.l}
                    </button>
                  ))}
                </div>

                {/* Input area */}
                <div style={{ padding: '24px' }}>
                  {mode === 'url' && (
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#18181B', marginBottom: '10px' }}>Article URL</label>
                      <input
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && canSubmit && submit()}
                        placeholder="https://example.com/article..."
                        style={{
                          width: '100%', padding: '14px 16px', fontSize: '14px', color: '#18181B',
                          background: '#F8F7F4', border: '1px solid #E8E5DE', borderRadius: '8px',
                          outline: 'none', transition: 'border-color 0.2s',
                        }}
                      />
                      <p style={{ fontSize: '12px', color: '#A1A1AA', marginTop: '10px' }}>Supports news articles, blog posts, and editorial pages. MSN/Yahoo/Google News redirects may fail.</p>
                    </div>
                  )}

                  {mode === 'text' && (
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#18181B', marginBottom: '10px' }}>Raw Article Text</label>
                      <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows={7}
                        placeholder="Paste the full article text here (minimum 50 characters)..."
                        style={{
                          width: '100%', padding: '14px 16px', fontSize: '14px', color: '#18181B',
                          background: '#F8F7F4', border: '1px solid #E8E5DE', borderRadius: '8px',
                          outline: 'none', resize: 'none',
                        }}
                      />
                      <p style={{ fontSize: '12px', color: '#A1A1AA', marginTop: '6px' }}>{text.length} characters</p>
                    </div>
                  )}

                  {mode === 'image' && (
                    <div
                      onClick={() => fileRef.current?.click()}
                      style={{
                        border: '2px dashed #E8E5DE', borderRadius: '8px', padding: '40px 20px',
                        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px',
                        cursor: 'pointer', background: '#FAFAFA',
                      }}
                    >
                      <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: '#EEF2FA', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1B3A6B' }}>
                        {IconImg}
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <p style={{ fontSize: '14px', fontWeight: 500, color: '#18181B' }}>Drop image or click to upload</p>
                        <p style={{ fontSize: '12px', color: '#A1A1AA', marginTop: '4px' }}>PNG, JPG, WEBP — Screenshots, infographics</p>
                      </div>
                      <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} />
                      <div style={{ fontSize: '11px', color: '#92400E', background: '#FFFBEB', padding: '4px 10px', borderRadius: '4px', border: '1px solid #FDE68A', marginTop: '4px' }}>
                        ⚠ Deepfake detection module — coming soon
                      </div>
                    </div>
                  )}
                </div>

                {/* Submit */}
                <div style={{ padding: '0 24px 24px' }}>
                  <button
                    onClick={submit}
                    disabled={!canSubmit || mode === 'image'}
                    style={{
                      width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                      padding: '14px', fontSize: '14px', fontWeight: 600, color: '#FFFFFF',
                      background: '#1B3A6B', border: 'none', borderRadius: '8px', cursor: (!canSubmit || mode === 'image') ? 'not-allowed' : 'pointer',
                      opacity: (!canSubmit || mode === 'image') ? 0.4 : 1, transition: 'all 0.2s',
                    }}
                  >
                    Analyze Content
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                  </button>
                  <p style={{ textAlign: 'center', fontSize: '11px', color: '#A1A1AA', marginTop: '12px' }}>
                    Analysis takes 2–10 minutes due to local AI processing.<br/>Please keep the tab open.
                  </p>
                </div>
              </div>
            </div>
          )}

          {stage === 'loading' && (
            <div className="fade-up" style={{ background: '#FFFFFF', border: '1px solid #E8E5DE', borderRadius: '12px', padding: '40px', boxShadow: '0 4px 24px rgba(0,0,0,0.02)' }}>
              <p style={{ fontSize: '11px', fontWeight: 600, color: '#A1A1AA', textTransform: 'uppercase', letterSpacing: '0.12em', textAlign: 'center', marginBottom: '32px' }}>
                Analyzing Data
              </p>
              <LoadingSteps step={step} />
            </div>
          )}

          {stage === 'error' && (
            <div className="fade-up" style={{ background: '#FFFFFF', border: '1px solid #E8E5DE', borderRadius: '12px', padding: '40px', textAlign: 'center', boxShadow: '0 4px 24px rgba(0,0,0,0.02)' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '24px', background: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: '#991B1B' }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              </div>
              <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#18181B', marginBottom: '8px' }}>Analysis Failed</h3>
              <p style={{ fontSize: '13px', color: '#71717A', marginBottom: '24px' }}>{error}</p>
              <button onClick={reset} style={{ padding: '10px 24px', fontSize: '13px', fontWeight: 500, color: '#FFFFFF', background: '#1B3A6B', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                Try Again
              </button>
            </div>
          )}

          {stage === 'done' && !show && sc && (
            <div className="fade-up" style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: '#71717A', marginBottom: '20px' }}>
                Analysis complete for <strong style={{ color: '#18181B' }}>{sc.domain || 'your content'}</strong>
              </p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button onClick={() => setShow(true)} style={{ padding: '10px 24px', fontSize: '13px', fontWeight: 500, color: '#FFFFFF', background: '#1B3A6B', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>
                  View Scorecard
                </button>
                <button onClick={reset} style={{ padding: '10px 24px', fontSize: '13px', fontWeight: 500, color: '#52525B', background: 'transparent', border: '1px solid #D4D0C8', borderRadius: '8px', cursor: 'pointer' }}>
                  Analyze Another
                </button>
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Scorecard modal */}
      {show && sc && <ScorecardModal sc={sc} onClose={() => setShow(false)} />}
    </div>
  );
}
