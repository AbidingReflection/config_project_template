import aiohttp
import asyncio
import pandas as pd
from typing import List, Dict, Any, Callable

class HttpRequestProcessor:
    def __init__(self, config, request_bundle: List[str], request_header: Dict[str, str], data_processor: Callable[[Any], List[Dict]], method: str = 'GET', payload: Dict[str, Any] = None):
        """Initialize the request processor with config, requests, headers, and method."""
        self.config = config
        self.request_bundle = request_bundle
        self.request_header = request_header
        self.data_processor = data_processor
        self.method = method.upper()  # Ensure method is uppercase (GET, POST, etc.)
        self.payload = payload 

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Any:
        """Make an async request to the given URL using the specified HTTP method."""
        self.config["logger"].info(f"Making '{self.method}' request to '{url}'")
        try:
            if self.method == 'GET':
                async with session.get(url, headers=self.request_header) as response:
                    return await self._handle_response(response, url)
            elif self.method == 'POST':
                async with session.post(url, headers=self.request_header, json=self.payload) as response:
                    return await self._handle_response(response, url)
            # elif self.method == 'PUT':
            #     async with session.put(url, headers=self.request_header, json=self.payload) as response:
            #         return await self._handle_response(response, url)
            # elif self.method == 'DELETE':
            #     async with session.delete(url, headers=self.request_header) as response:
            #         return await self._handle_response(response, url)
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")
        except Exception as e:
            self.config["logger"].error(f"Error making '{self.method}' request to '{url}': {e}")
            raise

    async def _handle_response(self, response, url: str) -> Any:
        """Handle the HTTP response and return JSON data if successful."""
        if response.status == 200:
            self.config["logger"].info(f"Request to '{url}' succeeded with status '{response.status}'")
            return await response.json()
        else:
            self.config["logger"].error(f"Request to '{url}' failed with status '{response.status}'")
            response.raise_for_status()

    async def make_requests(self, config) -> pd.DataFrame:
        """Perform asynchronous requests with limited concurrency and process the responses."""

        # Use the value from config["max_concurrent_requests"], or default to 1 if not provided
        max_concurrent_requests = config.get("max_concurrent_requests", 1)
        semaphore = asyncio.Semaphore(max_concurrent_requests)

        async with aiohttp.ClientSession() as session:
            async def limited_fetch(url):
                async with semaphore:  # Limit the number of concurrent requests
                    return await self.fetch(session, url)
            
            # Create the tasks for fetching with concurrency control
            tasks = [limited_fetch(url) for url in self.request_bundle]
            self.config["logger"].info(f"AsyncRequestProcessor: Making '{len(tasks)}' requests with a max concurrency of '{max_concurrent_requests}'")
            
            # Execute the tasks concurrently but with the concurrency limit
            response_bundle = await asyncio.gather(*tasks)

        # Process the response data
        processed_data = [self.data_processor(config, response) for response in response_bundle]
        flattened_data = [item for sublist in processed_data for item in sublist]
        
        return pd.DataFrame(flattened_data)
