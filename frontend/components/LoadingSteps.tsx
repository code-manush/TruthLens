'use client';

const STEPS = [
  { n: '01', label: 'Extracting content',       sub: 'Fetching and parsing article HTML via Trafilatura...' },
  { n: '02', label: 'AI context analysis',       sub: 'qwen3:8b is extracting facts, claims and tone...' },
  { n: '03', label: 'Live web corroboration',    sub: 'Tavily is searching 50+ trusted news sources...' },
  { n: '04', label: 'Generating scorecard',      sub: 'Computing weighted credibility dimensions...' },
];

export default function LoadingSteps({ step }: { step: number }) {
  return (
    <div className="w-full max-w-xs mx-auto select-none">
      <div className="space-y-5">
        {STEPS.map((s, i) => {
          const idx    = i + 1;
          const done   = step > idx;
          const active = step === idx;
          return (
            <div key={idx} className="flex items-start gap-4">
              {/* indicator */}
              <div className="relative flex-shrink-0 w-6 h-6 mt-0.5 flex items-center justify-center">
                {done ? (
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <circle cx="10" cy="10" r="10" fill="#166534" fillOpacity="0.12"/>
                    <path d="M6 10l3 3 5-5" stroke="#166534" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : active ? (
                  <span className="flex h-2 w-2">
                    <span className="pulse-dot inline-flex rounded-full h-2 w-2 bg-[#1B3A6B]" />
                  </span>
                ) : (
                  <span className="inline-block w-2 h-2 rounded-full bg-[#D4D0C8]" />
                )}
              </div>

              <div>
                <p className={`text-sm font-medium transition-colors duration-300 ${
                  done   ? 'text-[#166534]' :
                  active ? 'text-[#18181B]' :
                           'text-[#A1A1AA]'
                }`}>{s.label}</p>
                {active && (
                  <p className="text-xs text-[#71717A] mt-0.5 leading-relaxed">{s.sub}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Subtle progress bar */}
      <div className="mt-8 h-px w-full bg-[#E8E5DE] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#1B3A6B] rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${(step / 4) * 100}%` }}
        />
      </div>
      <p className="text-xs text-[#A1A1AA] text-right mt-1.5">{step} of 4</p>
    </div>
  );
}
