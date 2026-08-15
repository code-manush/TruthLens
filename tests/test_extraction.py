import pytest
from src.schemas.article_schema import ArticleInput
from src.extraction.article_extractor import ArticleExtractor
from src.extraction.metadata_extractor import MetadataExtractor

def test_extract_from_raw_text():
    extractor = ArticleExtractor()
    input_data = ArticleInput(
        raw_text="Breaking News: Breakthrough in AI Research\nScientists have made a major discovery in artificial intelligence safety.",
        title="Breaking News: Breakthrough in AI Research"
    )
    article = extractor.extract(input_data)
    assert article.title == "Breaking News: Breakthrough in AI Research"
    assert "Scientists have made a major discovery" in article.text
    assert article.domain == "raw_input"

def test_extract_invalid_input():
    extractor = ArticleExtractor()
    input_data = ArticleInput()
    with pytest.raises(ValueError):
        extractor.extract(input_data)

def test_metadata_ad_density():
    meta_extractor = MetadataExtractor()
    html_sample = """
    <html>
        <body>
            <div class="ad-banner">Ad 1</div>
            <div id="sponsor-link">Ad 2</div>
            <iframe src="ad.html"></iframe>
            <p>This is standard news content with some detailed context and facts.</p>
        </body>
    </html>
    """
    metrics = meta_extractor.analyze_ad_density(html_sample, text_length=500)
    assert metrics["num_ads_estimated"] >= 3
    assert metrics["ad_ratio"] > 0.0
