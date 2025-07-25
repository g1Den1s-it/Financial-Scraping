import pytest
import httpx
import asyncio
import datetime
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock
from src.scrap.financial_parser import FinancialParser
from src.scrap.schemas import PostSchema



SINGLE_ARTICLE_HTML = """
<html>
    <body>
        <h1 class="o-topper__headline">Test Article Title</h1>
        <a data-trackable="author">Author One</a>
        <a data-trackable="author">Author Two</a>
        <article id="article-body"><p>Test content</p></article>
        <time class="article-info__timestamp o3-editorial-typography-byline-timestamp o-date" datetime="2025-07-20T12:00:00"></time>
    </body>
</html>
"""

ARTICLE_LIST_HTML = """
<html>
    <body>
        <li class="o-teaser-collection__item o-grid-row">
            <a data-trackable="heading-link" href="/content/123"></a>
            <time class="o3-type-label o-date" datetime="2025-07-20T12:00:00"></time>
        </li>
        <li class="o-teaser-collection__item o-grid-row">
            <a data-trackable="heading-link" href="/content/456"></a>
            <time class="o3-type-label o-date" datetime="2025-06-20T12:00:00"></time>
        </li>
        <div class="stream__pagination">
            <a data-trackable="next-page" href="/world?page=2"></a>
        </div>
    </body>
</html>
"""


@pytest.mark.asyncio
async def test_financial_parser_init():

    parser = FinancialParser()
    assert parser.base_url == "https://www.ft.com"
    assert parser.start_page == "/world"
    assert isinstance(parser.headers, dict)
    assert parser.post_list_link == []
    assert parser.article_data == []



@pytest.mark.asyncio
async def test_parsing_single_data_paywall(mocker):
    parser = FinancialParser()
    paywall_html = '<html><body><a id="charge-button">Subscribe</a></body></html>'
    mock_response = MagicMock()
    mock_response.text = paywall_html
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    result = await parser._FinancialParser__parsing_single_data(mock_client, "/content/123")
    assert result is None


@pytest.mark.asyncio
async def test_parsing_single_data_timeout(mocker):
    parser = FinancialParser()
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Timeout")
    result = await parser._FinancialParser__parsing_single_data(mock_client, "/content/123")
    assert result is None


