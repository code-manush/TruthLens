export interface DimensionScore {
  name: string;
  score: number;
  weight: number;
  contribution: number;
  summary: string;
}

/** A web source checked during fact-verification (matches backend CorroboratingSource) */
export interface CorroboratingSource {
  url: string;
  title: string;
  domain: string;
  snippet?: string;
  trusted: boolean;
  tier: number;
  search_query?: string;
  relevance_score?: number;
}

export interface CorroborationResult {
  total_sources_found: number;
  trusted_sources_count: number;
  tier1_count: number;
  tier2_count: number;
  corroboration_score: number;
  verdict_label: string;
  top_sources: CorroboratingSource[];
  search_queries_used: string[];
}

export interface AdProfile {
  total_ad_slots: number;
  has_clickbait_ads: boolean;
  clickbait_networks_found: string[];
  ad_density: number;
}

export interface CredibilityScorecard {
  url: string | null;
  title: string;
  domain: string | null;
  publisher: string | null;
  authors: string[];
  publish_date: string | null;
  overall_score: number;
  credibility_rating: string;
  verdict: string;
  verdict_summary: string;
  dimensions: DimensionScore[];
  ad_profile: AdProfile;
  article_context: string;
  relevant_facts: string[];
  irrelevant_facts: string[];
  main_claims: string[];
  emotional_phrases: string[];
  clickbait_elements: string[];
  bias_indicators: string[];
  misleading_patterns: string[];
  content_tone: string;
  red_flags: string[];
  positive_signals: string[];
  /** Corroboration from Tavily */
  corroboration?: CorroborationResult;
}

export type AnalysisMode = 'url' | 'text' | 'image';
