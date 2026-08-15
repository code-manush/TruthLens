from src.schemas.article_schema import (
    ArticleInput, ExtractedArticle, TitleAnalysis, ContentAnalysis,
    AdAnalysis, PublisherAnalysis, Claim, AnalysisResult, CredibilityReport,
    EmotionAnalysis, AuthenticityAnalysis
)

def test_extracted_article_schema():
    article = ExtractedArticle(title="Test", text="Body text here.", authors=["Jane Doe"])
    assert article.title == "Test"
    assert article.uses_https is False

def test_title_analysis_schema():
    ta = TitleAnalysis(clickbait_score=0.8, emoji_count=2, emotional_word_count=3,
                       emotional_words_found=["shocking", "danger"], clickbait_reasons=["Caps"])
    assert ta.clickbait_score == 0.8
    assert ta.emoji_count == 2

def test_content_analysis_schema():
    ca = ContentAnalysis(bias_score=0.4, misleading_info_score=0.2, emotional_body_score=0.3)
    assert ca.bias_score == 0.4

def test_ad_analysis_schema():
    ad = AdAnalysis(num_ads=5, ad_ratio=0.15, ad_types_found=["banner"], ad_topic_relevance=0.3,
                    claims_in_ads=True, ad_claim_examples=["100% guaranteed"], ad_penalty_score=0.3)
    assert ad.claims_in_ads is True

def test_publisher_analysis_schema():
    pub = PublisherAnalysis(domain="reuters.com", uses_https=True,
                            extension_trust_score=0.9, outbound_link_quality=0.8,
                            known_unreliable=False, publisher_credibility_score=0.95)
    assert pub.publisher_credibility_score == 0.95

def test_article_input_publisher():
    ai = ArticleInput(raw_text="Some text", publisher="BBC News")
    assert ai.publisher == "BBC News"
