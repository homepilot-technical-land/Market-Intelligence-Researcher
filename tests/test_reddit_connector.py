"""Unit tests for the RedditConnector."""

from src.connectors.reddit_connector import RedditConnector

def test_reddit_connector_extract_post_id():
    url1 = "https://www.reddit.com/r/irishpersonalfinance/comments/1xwxv80/a_13_year_savings_journey_road_to_100000_and/"
    assert RedditConnector.extract_post_id(url1) == "1xwxv80"

    url2 = "https://reddit.com/comments/abc1234/"
    assert RedditConnector.extract_post_id(url2) == "abc1234"

    raw_id = "xyz987"
    assert RedditConnector.extract_post_id(raw_id) == "xyz987"

def test_reddit_connector_unconfigured_status():
    connector = RedditConnector(client_id="", client_secret="")
    assert connector.is_configured() is False

    res = connector.fetch_thread("https://reddit.com/r/ireland/comments/1xwxv80/test/")
    assert res["success"] is False
    assert res["status"] == "credentials_required"
    assert res["post_id"] == "1xwxv80"
