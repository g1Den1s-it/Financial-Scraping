import httpx
import asyncio
import logging

from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from src.scrap.schemas import PostSchema

logger = logging.getLogger(__name__)


class FinancialParser:
    """A class for asynchronously scraping articles from the Financial Times website.

    This class handles the collection of article links from the '/world' section,
    filters them by a specified time period, and extracts detailed information
    (e.g., title, author, content) for each article. It uses asynchronous HTTP
    requests for efficiency and handles paywalled content and errors gracefully.

    Attributes:
        headers (dict): HTTP headers to mimic a browser request.
        base_url (str): Base URL of the Financial Times website.
        start_page (str): Starting page for scraping (e.g., '/world').
        post_list_link (list): List of article URLs collected during scraping.
        article_data (list): List of parsed article data as PostSchema objects.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,uk;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Referer': 'https://www.google.com/',
        }
        self.base_url = "https://www.ft.com"
        self.start_page = "/world"
        self.post_list_link = []
        self.article_data = []
    
    async def __parsing_single_data(self, client, article_link) -> list[dict[str, str]]:
        """Parse a single article page to extract its details.

        Args:
            client (httpx.AsyncClient): The HTTP client for making requests.
            article_link (str): The relative URL of the article (e.g., '/content/123').

        Returns:
            PostSchema | None: A PostSchema object containing article details, or None if
                the article is paywalled or an error occurs.

        Raises:
            httpx.TimeoutException: If the request times out.
            httpx.HTTPStatusError: If an HTTP error occurs (e.g., 404, 403).
            httpx.RequestError: If a network error occurs.
            Exception: For unexpected errors during parsing.
        """
        try:
            req = await client.get(f"{self.base_url}{article_link}", headers=self.headers)

            soup = BeautifulSoup(req.text, 'lxml')

            subscribe_el = soup.find("a", id="charge-button")

            if subscribe_el:
                return None

            header_el = soup.find('h1', class_='o-topper__headline')
            subtitle_el = soup.find('div', class_='topper__standfirst')

            authors_els = soup.find_all('a', attrs={"data-trackable": "author"})

            article_el = soup.find('article', id="article-body")

            article_time_el = soup.find('time', class_="article-info__timestamp o3-editorial-typography-byline-timestamp o-date")

            date_val = article_time_el.get("datetime")

            if '.' in date_val:
                date_val = date_val.split('.')[0]
            
            post = PostSchema(
                url=f"{self.base_url}{article_link}",
                author="".join([author.text for author in authors_els]),
                title=header_el.text,
                content=str(article_el),
                published_at=datetime.strptime(date_val, '%Y-%m-%dT%H:%M:%S'),
                scraped_at=datetime.utcnow()
            )

        
            return post
        except httpx.TimeoutException:
            logger.error(f"Timeout occurred while fetching {article_link}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {article_link}: {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {article_link}: {e}")
            return None
        except Exception as e:
            logger.exception(f"__parsing_single_data - Unexpected error for {article_link}: {e}")
            return None


    async def pars_post_data(self):
        """Parse all collected article links and extract their details.

        This method processes the URLs in `self.post_list_link` concurrently,
        storing valid results in `self.article_data`.

        Returns:
            list[PostSchema]: A list of PostSchema objects containing article details.

        Raises:
            httpx.TimeoutException: If a request times out.
            httpx.HTTPStatusError: If an HTTP error occurs.
            httpx.RequestError: If a network error occurs.
        """
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=5.0)) as client:
            logger.info(f"Fetched: {len(self.post_list_link)} posts link")
            tasks = []

            for article_link in self.post_list_link:
                tasks.append(self.__parsing_single_data(client, article_link))

            
            res = await asyncio.gather(*tasks)

            self.article_data = [data for data in res if data is not None]

            return self.article_data


    async def parsing(self, period: timedelta):
        """Scrape article links from the '/world' section within a specified time period.

        This method paginates through the website, collecting article URLs that meet
        the time period criteria, and stores them in `self.post_list_link`.

        Args:
            period (timedelta): The time period for filtering recent articles (e.g., 30 days).

        Raises:
            httpx.RequestError: If a network error occurs during pagination.
            Exception: For unexpected errors during parsing or pagination.
        """
        is_parsing = True
        next_page = ""
        async with httpx.AsyncClient() as client:
            while is_parsing:
                if next_page:
                    req = await client.get(f"{self.base_url}{self.start_page}{next_page}", headers=self.headers)
                else:
                    req = await client.get(f"{self.base_url}{self.start_page}", headers=self.headers)

                soup = BeautifulSoup(req.text, "lxml")
            
                posts = soup.find_all('li', class_="o-teaser-collection__item o-grid-row")

                for post in posts:
                    if not post:
                        continue

                    try:
                        if not self.__is_recent_article(post, period):
                            is_parsing = False
                            break
                    except Exception as e:
                        continue

                    a = post.find('a', attrs={"data-trackable":"heading-link"})

                    self.post_list_link.append(a.get("href"))

                try:
                    pagination = soup.find("div", class_="stream__pagination")

                    pag_a = pagination.find('a', attrs={'data-trackable': 'next-page'})

                    if not pag_a:
                        is_parsing = False
                        break
                    
                    next_page = pag_a.get("href")
                except Exception as e:
                    logger.error(f"parsing - Error: {e}")
                    break


        
    def __is_recent_article(self, post, period):
        """Check if an article's publication date is within the specified time period.

        Args:
            post (BeautifulSoup): The BeautifulSoup element representing an article teaser.
            period (timedelta): The time period to check against (e.g., 30 days).

        Returns:
            bool: True if the article is within the time period, False otherwise.

        Raises:
            ValueError: If the publication date cannot be parsed.
        """
        time = post.find('time', class_='o3-type-label o-date')

        date_val = time.get("datetime")

        try:
            if '.' in date_val:
                date_val = date_val.split('.')[0]
            
            publish_date = datetime.strptime(date_val, '%Y-%m-%dT%H:%M:%S')

            current_date = datetime.utcnow()

            thirty_days_ago = current_date - period
            
            

            if publish_date > thirty_days_ago:
                return True
            else:
                return False

        except ValueError:
            return False
    