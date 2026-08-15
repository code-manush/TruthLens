document.addEventListener('DOMContentLoaded', () => {
  const btnAnalyze = document.getElementById('analyze-btn');
  const btnRetry = document.getElementById('retry-btn');
  
  const stateIdle = document.getElementById('idle-state');
  const stateLoading = document.getElementById('loading-state');
  const stateError = document.getElementById('error-state');
  const stateResult = document.getElementById('result-state');
  const errorMsg = document.getElementById('error-msg');

  function showState(stateElement) {
    [stateIdle, stateLoading, stateError, stateResult].forEach(el => el.classList.add('hidden'));
    stateElement.classList.remove('hidden');
  }

  function scoreColor(s) {
    if (s >= 70) return '#166534';
    if (s >= 45) return '#92400E';
    return '#991B1B';
  }

  function verdictStyle(v) {
    if (v === 'REAL')        return { pill: '#166534', bg: '#F0FDF4', border: '#BBF7D0' };
    if (v === 'LIKELY REAL') return { pill: '#92400E', bg: '#FFFBEB', border: '#FDE68A' };
    if (v === 'LIKELY FAKE') return { pill: '#9A3412', bg: '#FFF7ED', border: '#FDBA74' };
    return                          { pill: '#991B1B', bg: '#FEF2F2', border: '#FECACA' };
  }

  function renderResult(data) {
    const vStyle = verdictStyle(data.verdict);
    const sColor = scoreColor(data.overall_score);

    let html = `
      <div class="score-hero">
        <div class="score-num" style="color: ${sColor}">${Math.round(data.overall_score)}</div>
        <div class="score-divider"></div>
        <div>
          <span class="verdict-pill" style="color: ${vStyle.pill}; background: ${vStyle.bg}; border: 1px solid ${vStyle.border}">
            ${data.verdict}
          </span>
          <p class="verdict-sum">${data.verdict_summary}</p>
        </div>
      </div>
    `;

    if (data.red_flags && data.red_flags.length > 0) {
      html += `
        <div class="section-title" style="color: #991B1B">Red Flags</div>
        <div class="flags">
          <ul>
            ${data.red_flags.slice(0, 3).map(f => `<li><span>—</span> ${f}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    if (data.relevant_facts && data.relevant_facts.length > 0) {
      html += `
        <div class="section-title">Verified Facts</div>
        <div class="facts">
          <ul>
            ${data.relevant_facts.slice(0, 3).map((f, i) => `<li><span class="bullet">${i+1}.</span> ${f}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    stateResult.innerHTML = html;
    showState(stateResult);
  }

  async function analyzeCurrentTab() {
    showState(stateLoading);
    
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.url) {
        throw new Error("Could not get the current page URL.");
      }

      // Send to local TruthLens server
      const res = await fetch('http://localhost:3000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: tab.url })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `Server returned ${res.status}`);
      }

      const data = await res.json();
      renderResult(data);

    } catch (err) {
      errorMsg.textContent = err.message || "Failed to connect to local server.";
      showState(stateError);
    }
  }

  btnAnalyze.addEventListener('click', analyzeCurrentTab);
  btnRetry.addEventListener('click', () => showState(stateIdle));
});
