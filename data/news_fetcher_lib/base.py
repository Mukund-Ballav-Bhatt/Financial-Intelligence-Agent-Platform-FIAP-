import logging
import requests
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


class BaseNewsFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.session = requests.Session()
        logger.info("BaseNewsFetcher initialized")

    def _make_request(self, url, params=None, retries=3):
        if params is None:
            params = {}
        if self.api_key:
            params['apiKey'] = self.api_key

        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retries}): {url}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    logger.error(f"Request failed after {retries} attempts: {url}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None

        return None

    def _delay(self, seconds=1):
        time.sleep(seconds)

    def test_connection(self):
        return self.api_key is not None