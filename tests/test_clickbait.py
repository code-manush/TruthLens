from src.schemas.article_schema import ExtractedArticle, ArticleInput
from src.analysis.clickbait_detector import ClickbaitDetector
from src.analysis.emotion_detector import EmotionDetector
from src.analysis.content_analyzer import ContentAnalyzer
from src.analysis.publisher_analyzer import PublisherAnalyzer
from src.analysis.ad_analyzer import AdAnalyzer

def test_clickbait_title_analysis():
    detector = ClickbaitDetector()
    result = detector.analyze_title("SHOCKING SECRET: Top 10 Reasons You Won't Believe!!!")
    assert result.clickbait_score > 0.5
    assert result.emotional_word_count >= 1
    assert len(result.clickbait_reasons) >= 2

def test_emoji_detection():
    detector = ClickbaitDetector()
    result = detector.analyze_title("Breaking 🔥🔥 You MUST See This!")
    assert result.emoji_count >= 2

def test_emotion_breakdown():
    detector = EmotionDetector()
    article = ExtractedArticle(
        title="Catastrophic disaster",
        text="This is a horrifying disaster causing panic and alarm across the nation. Furious citizens outraged."
    )
    result = detector.analyze(article)
    assert "fear" in result.emotion_breakdown
    assert "anger" in result.emotion_breakdown
    assert result.sensationalism_score > 0.0

def test_content_bias_detection():
    analyzer = ContentAnalyzer()
    article = ExtractedArticle(
        title="Test",
        text="Everyone knows the liberal media is always lying. The deep state is clearly corrupt and nobody believes them."
    )
    result = analyzer.analyze(article)
    assert result.bias_score > 0.0
    assert len(result.bias_indicators) >= 1

def test_content_misleading_detection():
    analyzer = ContentAnalyzer()
    article = ExtractedArticle(
        title="Test",
        text="Doctors hate this secret miracle cure! 100% proven with no side effects. Government hiding the truth."
    )
    result = analyzer.analyze(article)
    assert result.misleading_info_score > 0.0

def test_publisher_high_credibility():
    analyzer = PublisherAnalyzer()
    result = analyzer.analyze(domain="www.reuters.com", uses_https=True, outbound_links=[])
    assert result.publisher_credibility_score >= 0.8
    assert result.known_unreliable is False

def test_publisher_low_credibility():
    analyzer = PublisherAnalyzer()
    result = analyzer.analyze(domain="infowars.com", uses_https=False, outbound_links=[])
    assert result.known_unreliable is True
    assert result.publisher_credibility_score < 0.3

def test_publisher_gov_extension():
    analyzer = PublisherAnalyzer()
    result = analyzer.analyze(domain="cdc.gov", uses_https=True)
    assert result.extension_trust_score >= 0.9
