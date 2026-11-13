import pytest
from src.normalisation.normaliser import DocumentNormaliser

def test_html_cleaning_and_boilerplate_stripping():
    html_raw = """
    <!DOCTYPE html>
    <html>
    <head><title>Buying a Home in Navan - HomePilot</title></head>
    <body>
        <nav><a href="/home">Home</a><a href="/login">Login</a></nav>
        <header>Header logo and navigation</header>
        <main>
            <h1>Navan Housing Developments</h1>
            <p>Glenveagh has commenced 350 new starter homes in Navan, Co. Meath.</p>
            <p>Eligible buyers can apply for the First Home Scheme and Help to Buy.</p>
        </main>
        <footer>
            <p>Cookie settings and privacy policy. All rights reserved 2026.</p>
        </footer>
    </body>
    </html>
    """
    title, markdown = DocumentNormaliser.clean_html(html_raw)
    assert title == "Buying a Home in Navan - HomePilot"
    assert "Navan Housing Developments" in markdown
    assert "Glenveagh has commenced 350 new starter homes" in markdown
    assert "Cookie settings" not in markdown
    assert "Header logo" not in markdown

def test_canonical_hash_consistency():
    content = "# Title\nConsistent content line."
    hash1 = DocumentNormaliser.compute_hash(content)
    hash2 = DocumentNormaliser.compute_hash(content)
    assert hash1 == hash2
    assert len(hash1) == 64
