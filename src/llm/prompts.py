"""
Human-written prompts for Ollama (qwen3:8b).
Each prompt has a strict JSON output format so the pipeline can parse it reliably.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT 1: Context-first article analysis
# Used by: OllamaExtractor.analyze_article()
#
# The LLM must:
#   1. First identify the core context of the article (what is it ACTUALLY about)
#   2. Extract ALL verifiable facts from the text
#   3. Sort those facts: relevant (match the context) vs irrelevant (don't match)
#   4. Extract claims, search queries, language signals
# ─────────────────────────────────────────────────────────────────────────────

ARTICLE_ANALYSIS_PROMPT = """You are a senior investigative journalist and fact-checker with 20 years of experience. You will analyse a news article in a structured, step-by-step way.

ARTICLE TITLE: {title}

ARTICLE TEXT:
{text}

---

STEP 1 — UNDERSTAND THE CONTEXT FIRST.
Read the entire article. Before doing anything else, identify what this article is fundamentally about in 1-2 sentences. This is the "core context" and it will guide everything else.

STEP 2 — EXTRACT ALL FACTS, THEN FILTER THEM.
Extract every verifiable, specific factual statement in the article. Then go through each fact and ask: "Is this fact directly related to the core context from Step 1?"
  - If YES → it is a RELEVANT FACT.
  - If NO  → it is an IRRELEVANT FACT (padding, off-topic trivia, or unrelated filler).

STEP 3 — COMPLETE THE FULL ANALYSIS.

Now output your complete analysis in this exact JSON format:

{{
  "article_context": "string — 1-2 sentences describing what this article is FUNDAMENTALLY about",

  "relevant_facts": [
    // 3-8 specific, verifiable facts that are DIRECTLY related to the article's core context.
    // Example for a moon article: "NASA's Apollo 17 was the last crewed lunar mission in December 1972"
    // These are the facts Tavily will search to verify.
  ],

  "irrelevant_facts": [
    // Any facts or statements in the article that are NOT related to the core context.
    // Example: if a moon article mentions "The Eiffel Tower is 330 metres tall", that is irrelevant.
    // If there are none, use an empty list [].
    // NOTE: Irrelevant facts in an article are a RED FLAG for low-quality or padded content.
  ],

  "main_claims": [
    // 2-5 major assertions or conclusions the article makes — things it wants you to believe.
    // These may be opinions or verifiable statements.
  ],

  "search_queries": [
    // Exactly 5 focused search queries to fact-check this article using a news search engine.
    // Make them specific and directly related to the article's context and relevant facts.
    // Bad: "moon facts"
    // Good: "why did NASA stop Apollo moon missions after 1972"
  ],

  "emotional_phrases": [
    // Copy exact phrases from the article that use emotional, alarming, or charged language.
    // Leave empty [] if the article is neutral and professional.
  ],

  "clickbait_elements": [
    // List specific clickbait techniques found:
    // - Curiosity gaps: "What happened next will shock you"
    // - Exaggeration: "The BIGGEST scandal in history"
    // - Excessive punctuation, ALL CAPS misuse, vague promises
    // Leave empty [] if none are present.
  ],

  "bias_indicators": [
    // Language revealing one-sided, partisan, or propagandistic framing.
    // Leave empty [] if the article appears balanced.
  ],

  "misleading_patterns": [
    // Patterns suggesting misinformation or manipulation:
    // "Doctors don't want you to know...", "Secret remedy", "100% proven", "Government hiding..."
    // Leave empty [] if none are present.
  ],

  "has_named_sources": true,     // Does the article cite real named people or institutions?
  "has_statistics": true,         // Does the article include specific numbers or statistics?
  "has_expert_quotes": false,     // Does the article include direct quotes from named experts?
  "content_tone": "neutral",      // One of: neutral / positive / fear / anger / sensational / promotional
  "language_quality": "normal"    // One of: professional / normal / poor
}}

CRITICAL RULES:
- Output ONLY the JSON. No text before or after it.
- Do NOT make up facts. Only use what is in the article text.
- The irrelevant_facts list is very important — do not skip it.
- All strings must use double quotes.
- true/false must be lowercase JSON booleans.
- If a list has nothing to report, use an empty list [].
"""


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT 2: Credibility reasoning given corroboration results
# Used by: OllamaExtractor.reason_about_credibility()
# ─────────────────────────────────────────────────────────────────────────────

CREDIBILITY_REASONING_PROMPT = """You are a senior fact-checker at a major news organisation. You have searched the internet for articles about the same topic and found the results below.

ORIGINAL ARTICLE:
Title: {title}
Domain: {domain}
Core Context: {article_context}

RELEVANT FACTS FROM THE ARTICLE:
{claims}

WEB SEARCH RESULTS (real articles found online via Tavily):
{search_results}

---

Based on the evidence above, answer the following in JSON:

{{
  "corroboration_assessment": "string — 1-2 sentences: do trusted outlets cover this same story? Are the facts corroborated?",
  "red_flags": [
    // Most concerning problems found. For example:
    // "No major news outlet has covered this story"
    // "The article makes extreme claims with no named sources"
    // "Irrelevant filler facts detected, suggesting padded/low-quality content"
    // Leave empty [] if the article seems credible.
  ],
  "positive_signals": [
    // Positive credibility signals. For example:
    // "Reuters and BBC both independently covered this story"
    // "Multiple government sources are cited"
    // Leave empty [] if no positive signals found.
  ],
  "overall_reasoning": "string — 2-3 sentences explaining why this article is or is not credible"
}}

RULES:
- Output ONLY the JSON.
- Base your answer ONLY on the information provided above.
- Be direct and specific. Reference actual domains from the search results if possible.
"""
