"""
Shodan Integration Service.

Provides functionality to fetch and manage Shodan intelligence data for domains.
"""
import logging
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

SHODAN_API_BASE_URL = "https://api.shodan.io"


class ShodanService:
    """Service to interact with Shodan API and web search."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Shodan service with API key."""
        self.api_key = api_key or settings.shodan_api_key
        self.base_url = SHODAN_API_BASE_URL

    def get_shodan_search_url(self, domain: str) -> str:
        """
        Generate Shodan search URL for a domain.
        
        Args:
            domain: Domain name to search
            
        Returns:
            URL to Shodan search results page
        """
        # Clean domain name
        domain_clean = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        return f"https://www.shodan.io/search?query={domain_clean}"

    async def fetch_shodan_api_data(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Fetch domain data from Shodan API.
        
        Args:
            domain: Domain name to search
            
        Returns:
            Dictionary with Shodan data or None if API key not configured
        """
        if not self.api_key:
            logger.warning("Shodan API key not configured")
            return None

        domain_clean = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

        try:
            async with aiohttp.ClientSession() as session:
                # Shodan API endpoint for domain info
                url = f"{self.base_url}/shodan/host/search"
                params = {
                    "query": domain_clean,
                    "key": self.api_key
                }

                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "total_results": data.get("total", 0),
                            "matches": data.get("matches", []),
                            "fetched_at": datetime.utcnow().isoformat(),
                            "search_url": self.get_shodan_search_url(domain)
                        }
                    elif response.status == 401:
                        logger.error("Shodan API: Invalid API key")
                        return {
                            "success": False,
                            "error": "Invalid Shodan API key",
                            "search_url": self.get_shodan_search_url(domain)
                        }
                    else:
                        logger.error(f"Shodan API error: {response.status}")
                        return {
                            "success": False,
                            "error": f"Shodan API returned status {response.status}",
                            "search_url": self.get_shodan_search_url(domain)
                        }

        except asyncio.TimeoutError:
            logger.warning(f"Shodan API timeout for domain: {domain_clean}")
            return {
                "success": False,
                "error": "API request timeout",
                "search_url": self.get_shodan_search_url(domain)
            }
        except Exception as e:
            logger.error(f"Error fetching Shodan data for {domain_clean}: {e}")
            return {
                "success": False,
                "error": str(e),
                "search_url": self.get_shodan_search_url(domain)
            }

    async def fetch_shodan_data_batch(self, domains: list) -> Dict[str, Dict[str, Any]]:
        """
        Fetch Shodan data for multiple domains.
        
        Args:
            domains: List of domain names
            
        Returns:
            Dictionary mapping domain to its Shodan data
        """
        results = {}
        for domain in domains:
            data = await self.fetch_shodan_api_data(domain)
            results[domain] = data
        return results

    @staticmethod
    def parse_shodan_results(data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse and format Shodan API results.
        
        Args:
            data: Raw Shodan API response
            
        Returns:
            Formatted Shodan data summary
        """
        if not data:
            return {
                "status": "unavailable",
                "message": "No data available"
            }

        if not data.get("success"):
            return {
                "status": "error",
                "error": data.get("error", "Unknown error"),
                "search_url": data.get("search_url", "")
            }

        matches = data.get("matches", [])
        summary = {
            "status": "success",
            "total_results": data.get("total_results", 0),
            "results_found": len(matches),
            "fetched_at": data.get("fetched_at"),
            "search_url": data.get("search_url", ""),
            "devices": []
        }

        # Extract key information from matches
        for match in matches[:10]:  # Limit to 10 results
            device_info = {
                "ip": match.get("ip_str"),
                "port": match.get("port"),
                "hostnames": match.get("hostnames", []),
                "org": match.get("org", "N/A"),
                "isp": match.get("isp", "N/A"),
                "os": match.get("os", "N/A"),
                "last_update": match.get("timestamp", "N/A"),
                "services": match.get("ssl", {}) if match.get("ssl") else None
            }
            summary["devices"].append(device_info)

        return summary


import asyncio
