"""
Odysseus API Client
Communicates with API server inside Odysseus container
"""

import aiohttp
import logging
from config import API_URL, API_TIMEOUT

logger = logging.getLogger(__name__)


class OdysseusAPIClient:
    """Async HTTP client for Odysseus API"""
    
    def __init__(self, base_url=API_URL, timeout=API_TIMEOUT):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def _request(self, method: str, endpoint: str, **kwargs):
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(method, url, **kwargs) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        raise Exception(f"API error {resp.status}: {error_text}")
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise
    
    async def get_status(self) -> dict:
        """Get system status"""
        return await self._request("POST", "/api/status")
    
    async def send_message(self, text: str) -> dict:
        """Send message to Odysseus for processing"""
        return await self._request(
            "POST",
            "/api/message",
            json={"text": text}
        )
    
    async def get_logs(self, lines: int = 50) -> dict:
        """Get recent container logs"""
        return await self._request(
            "POST",
            "/api/logs",
            json={"lines": lines}
        )
    
    async def start_odysseus(self) -> dict:
        """Start Odysseus (orchestrate.sh odysseus)"""
        return await self._request(
            "POST",
            "/api/start",
        )
    
    async def stop_odysseus(self) -> dict:
        """Stop Odysseus (orchestrate.sh openclaw)"""
        return await self._request(
            "POST",
            "/api/stop",
        )
    
    async def execute_command(self, command: str, timeout: int = 30) -> dict:
        """Execute shell command in container (optional, controlled)"""
        return await self._request(
            "POST",
            "/api/execute",
            json={"command": command, "timeout": timeout}
        )


# Test the client
if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = OdysseusAPIClient()
        try:
            status = await client.get_status()
            print(f"✓ Status: {status}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    asyncio.run(test())
