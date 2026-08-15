from src.schemas.article_schema import ArticleInput
from src.claims.claim_extractor import ClaimExtractor
from src.pipeline.article_pipeline import ArticlePipeline

def test_claim_extractor():
    extractor = ClaimExtractor()
    text = "A recent study found that 85% of respondents prefer renewable energy. Researchers announced the findings today."
    claims = extractor.extract_claims(text)
    assert len(claims) >= 1

def test_pipeline_real_article():
    """A balanced news-style article from a reputable domain should score reasonably well."""
    pipeline = ArticlePipeline()
    input_data = ArticleInput(
        title="NASA Scientists Confirm Water Ice Found on Moon's South Pole",
        raw_text=(
            "NASA researchers today confirmed the discovery of water ice deposits near the Moon's "
            "south pole, according to a study published in Nature. The findings could enable future "
            "lunar missions to use local water resources. Scientists analyzed data collected by the "
            "Lunar Reconnaissance Orbiter. The research was conducted over three years with 85% confidence."
        ),
        publisher="reuters.com"
    )
    report = pipeline.run(input_data)
    assert report.overall_credibility_score > 40.0
    assert report.real_or_fake_verdict in ["REAL", "LIKELY REAL", "LIKELY FAKE", "FAKE"]
    assert report.credibility_rating in ["HIGH", "MODERATE", "LOW", "UNRELIABLE"]
    assert len(report.dimension_scores) == 6

def test_pipeline_fake_article():
    """A heavily clickbait/misleading article should score lower."""
    pipeline = ArticlePipeline()
    input_data = ArticleInput(
        title="SHOCKING SECRET MIRACLE CURE Doctors DON'T Want You To Know!!!",
        raw_text=(
            "The deep state is hiding a miracle cure! 100% proven with no side effects. "
            "Government concealing the truth. Everyone knows the liberal media always lies. "
            "Click here to see what happened next. Secret remedy will change your life!"
        )
    )
    report = pipeline.run(input_data)
    assert report.overall_credibility_score < 70.0
    assert report.real_or_fake_verdict in ["LIKELY FAKE", "FAKE", "LIKELY REAL"]

def test_pipeline_dimension_scores():
    """Dimension scores dict should always contain all 6 keys."""
    pipeline = ArticlePipeline()
    report = pipeline.run(ArticleInput(
        title="Breaking news today",
        raw_text="Some article content here about current events."
    ))
    expected_keys = {"title", "content", "emotion", "claims", "ads", "publisher"}
    assert set(report.dimension_scores.keys()) == expected_keys
