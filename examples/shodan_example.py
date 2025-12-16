#!/usr/bin/env python3
"""
Shodan Integration Example Script
Demonstrates how to use the Shodan integration in the SSL Checker
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

class ShodanClientExample:
    """Example client for Shodan integration"""
    
    def __init__(self, api_url: str = "http://localhost:8000", token: str = None):
        """Initialize the client"""
        self.api_url = api_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json"
        }
    
    def get_shodan_search_url(self, domain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Shodan search URL for a domain (no API key required).
        
        Args:
            domain_id: Domain ID in the system
            
        Returns:
            Dictionary with search URL or None if error
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/domains/shodan/search-url/{domain_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def get_shodan_data(self, domain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed Shodan data for a domain (requires API key).
        
        Args:
            domain_id: Domain ID in the system
            
        Returns:
            Dictionary with Shodan data or None if error
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/domains/{domain_id}/shodan",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def refresh_all_shodan_data(self) -> Optional[Dict[str, Any]]:
        """
        Refresh Shodan data for all domains (admin only).
        
        Returns:
            Dictionary with refresh results or None if error
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/domains/shodan/refresh-all",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Exception: {e}")
            return None
    
    def print_shodan_data(self, data: Dict[str, Any]):
        """Pretty print Shodan data"""
        print("\n" + "="*70)
        print(f"Domain: {data['domain']}")
        print(f"Last Checked: {data['last_checked']}")
        print(f"Cached: {data['cached']}")
        print("-"*70)
        
        shodan = data['data']
        
        if shodan.get('status') == 'error':
            print(f"Error: {shodan.get('error')}")
            print(f"View at: {shodan.get('search_url')}")
            return
        
        print(f"Status: {shodan.get('status')}")
        print(f"Total Results: {shodan.get('total_results')}")
        print(f"Devices Found: {shodan.get('results_found')}")
        print("-"*70)
        
        devices = shodan.get('devices', [])
        if devices:
            print("\nDevices:")
            for i, device in enumerate(devices, 1):
                print(f"\n  Device {i}:")
                print(f"    IP: {device.get('ip')}")
                print(f"    Port: {device.get('port')}")
                print(f"    Organization: {device.get('org', 'N/A')}")
                print(f"    ISP: {device.get('isp', 'N/A')}")
                print(f"    OS: {device.get('os', 'N/A')}")
                if device.get('hostnames'):
                    print(f"    Hostnames: {', '.join(device['hostnames'])}")
        
        print(f"\nView full results: {shodan.get('search_url')}")
        print("="*70)


def example_1_get_search_url(client: ShodanClientExample, domain_id: int = 1):
    """Example 1: Get Shodan search URL"""
    print("\n### Example 1: Get Shodan Search URL ###")
    print(f"Fetching search URL for domain {domain_id}...")
    
    result = client.get_shodan_search_url(domain_id)
    if result:
        print(f"Domain: {result['domain']}")
        print(f"Search URL: {result['search_url']}")
        print(f"Open in browser: {result['redirect_url']}")


def example_2_get_detailed_data(client: ShodanClientExample, domain_id: int = 1):
    """Example 2: Get detailed Shodan data"""
    print("\n### Example 2: Get Detailed Shodan Data ###")
    print(f"Fetching Shodan data for domain {domain_id}...")
    
    result = client.get_shodan_data(domain_id)
    if result:
        client.print_shodan_data(result)


def example_3_refresh_all(client: ShodanClientExample):
    """Example 3: Refresh all Shodan data (admin only)"""
    print("\n### Example 3: Refresh All Shodan Data ###")
    print("Refreshing Shodan data for all domains (requires admin token)...")
    
    result = client.refresh_all_shodan_data()
    if result:
        print(f"Total domains: {result['total']}")
        print(f"Updated: {result['updated']}")
        print(f"Failed: {result['failed']}")
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error['domain']}: {error['error']}")


def example_4_analyze_devices(client: ShodanClientExample, domain_id: int = 1):
    """Example 4: Analyze device information"""
    print("\n### Example 4: Analyze Device Information ###")
    
    result = client.get_shodan_data(domain_id)
    if not result:
        return
    
    shodan = result['data']
    devices = shodan.get('devices', [])
    
    print(f"\nTotal devices exposed: {len(devices)}")
    
    # Analyze by port
    ports = {}
    for device in devices:
        port = device.get('port')
        ports[port] = ports.get(port, 0) + 1
    
    print(f"\nPorts distribution:")
    for port, count in sorted(ports.items()):
        print(f"  Port {port}: {count} device(s)")
    
    # Analyze by organization
    orgs = {}
    for device in devices:
        org = device.get('org', 'Unknown')
        orgs[org] = orgs.get(org, 0) + 1
    
    print(f"\nOrganizations:")
    for org, count in sorted(orgs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {org}: {count} device(s)")


if __name__ == "__main__":
    # Configuration
    API_URL = "http://localhost:8000"
    # Replace with your actual token
    TOKEN = "your_token_here"
    DOMAIN_ID = 1
    
    print("Shodan Integration Example Script")
    print("="*70)
    
    # Create client
    client = ShodanClientExample(api_url=API_URL, token=TOKEN)
    
    # Run examples
    try:
        # Example 1: Get search URL (no API key needed)
        example_1_get_search_url(client, DOMAIN_ID)
        
        # Example 2: Get detailed data (requires API key)
        example_2_get_detailed_data(client, DOMAIN_ID)
        
        # Example 4: Analyze devices
        example_4_analyze_devices(client, DOMAIN_ID)
        
        # Example 3: Refresh all (uncomment if you have admin privileges)
        # example_3_refresh_all(client)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
