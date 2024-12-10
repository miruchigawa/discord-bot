"""
Stable Diffusion API Client

This module provides an async client for interacting with Stable Diffusion web UI API.
It supports text-to-image generation and model/sampler management.

Example:
    ```python
    async def generate_image():
        client = StableDiffusion("http://localhost:7860")
        
        config = SDConfig(
            prompt="a cute cat, high quality, detailed",
            negative_prompt="low quality, blurry"
        )
        
        try:
            images = await client.text2img(config)
            with open("generated.png", "wb") as f:
                f.write(images[0])
        finally:
            await client.close()
    ```
"""

import aiohttp
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import base64
from contextlib import asynccontextmanager

@dataclass
class SDConfig:
    """Configuration parameters for Stable Diffusion image generation.
    
    Attributes:
        prompt (str): The main prompt describing desired image
        negative_prompt (str, optional): Things to avoid in generation
        steps (int, optional): Number of denoising steps (default: 24)
        cfg_scale (float, optional): Classifier free guidance scale (default: 4.5)
        width (int, optional): Image width in pixels (default: 1024)
        height (int, optional): Image height in pixels (default: 1024)
        seed (int, optional): Random seed (-1 for random) (default: -1)
        batch_size (int, optional): Number of images per batch (default: 1)
        n_iter (int, optional): Number of batches to generate (default: 1)
        sampler_name (str, optional): Name of sampler to use (default: "Euler a")
    """
    
    prompt: str
    negative_prompt: str = ""
    steps: int = 24
    cfg_scale: float = 4.5
    width: int = 1024
    height: int = 1024
    seed: int = -1
    batch_size: int = 1
    n_iter: int = 1
    sampler_name: str = "Euler a"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for API payload."""
        return asdict(self)

class StableDiffusion:
    """Async client for Stable Diffusion API.
    
    This client provides methods to interact with a Stable Diffusion web UI API endpoint
    for text-to-image generation and model management.
    
    Attributes:
        base_url (str): Base URL of the Stable Diffusion API
        timeout (aiohttp.ClientTimeout): Request timeout configuration
        session (Optional[aiohttp.ClientSession]): Async HTTP session
        
    Args:
        base_url (str): Base URL of the Stable Diffusion API
        timeout (int, optional): Request timeout in seconds (default: 300)
    """
    
    def __init__(self, base_url: str, timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    @asynccontextmanager
    async def _session(self):
        """Context manager for handling the aiohttp session.
        
        Yields:
            aiohttp.ClientSession: The active session
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        try:
            yield self.session
        finally:
            if self.session and self.session.closed:
                self.session = None

    async def _api_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        **kwargs
    ) -> Dict[str, Any]:
        """Make an API request to the Stable Diffusion server.
        
        Args:
            endpoint (str): API endpoint path
            method (str, optional): HTTP method (default: "GET")
            **kwargs: Additional arguments passed to request
            
        Returns:
            Dict[str, Any]: JSON response from API
            
        Raises:
            aiohttp.ClientError: If the API request fails
        """
        async with self._session() as session:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    async def text2img(self, config: Union[SDConfig, Dict[str, Any]]) -> List[bytes]:
        """Generate images from text prompt using Stable Diffusion.
        
        Args:
            config (Union[SDConfig, Dict[str, Any]]): Generation parameters
            
        Returns:
            List[bytes]: List of generated images as bytes
            
        Raises:
            aiohttp.ClientError: If API request fails
            ValueError: If config is invalid
        """
        if isinstance(config, dict):
            payload = config
        elif isinstance(config, SDConfig):
            payload = config.to_dict()
        else:
            raise ValueError("Config must be SDConfig or dict")

        result = await self._api_request(
            "sdapi/v1/txt2img",
            method="POST",
            json=payload
        )
        
        return [base64.b64decode(img) for img in result["images"]]

    async def get_samplers(self) -> List[Dict[str, str]]:
        """Get list of available samplers.
        
        Returns:
            List[Dict[str, str]]: List of sampler info with name and aliases
            
        Raises:
            aiohttp.ClientError: If API request fails
        """
        return await self._api_request("sdapi/v1/samplers")

    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models.
        
        Returns:
            List[Dict[str, Any]]: List of model info
            
        Raises:
            aiohttp.ClientError: If API request fails
        """
        return await self._api_request("sdapi/v1/sd-models")

    async def close(self) -> None:
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def __del__(self):
        """Ensure session is cleaned up on deletion."""
        if self.session and not self.session.closed:
            if self.session._loop.is_running():
                self.session._loop.create_task(self.session.close())
            else:
                self.session._loop.run_until_complete(self.session.close())
