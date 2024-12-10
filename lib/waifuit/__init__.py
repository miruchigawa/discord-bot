import aiohttp
from typing import Optional, Dict, Any
from urllib.parse import urlencode

class WaifuIt:
    """Async client for the waifu.it API
    
    This client provides methods to interact with waifu.it API endpoints.
    All endpoints follow the format: https://waifu.it/api/v{version}/{endpoint}
    
    Args:
        token (str, optional): API authentication token
        version (int, optional): API version number (default: 4)
    """
    
    def __init__(self, token: Optional[str] = None, version: int = 4):
        self.base_url = f"https://waifu.it/api/v{version}"
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make API request to any endpoint
        
        Args:
            endpoint (str): API endpoint path
            params (Dict[str, str], optional): Query parameters
            
        Returns:
            Dict[str, Any]: API response
        """
        await self._ensure_session()
        url = f"{self.base_url}/{endpoint}"
        if params:
            url = f"{url}?{urlencode(params)}"
            
        async with self.session.get(url, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()
