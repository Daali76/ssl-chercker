# Shodan Integration Guide

## Overview

The Shodan integration allows you to gather intelligence about your monitored domains by leveraging the Shodan search engine database. This gives you visibility into what services and vulnerabilities are exposed on your domains.

## Features

1. **Shodan Search URLs** - Direct links to Shodan search results for each domain (no API key required)
2. **Shodan API Data** - Detailed device and service information (requires API key)
3. **Automatic Caching** - Data is cached for 24 hours to minimize API calls
4. **Batch Refresh** - Refresh Shodan data for all domains at once

## Setup

### 1. Get a Shodan API Key

1. Visit [https://www.shodan.io/](https://www.shodan.io/)
2. Sign up for a free or premium account
3. Go to Account Settings → API key
4. Copy your API key

### 2. Configure the API Key

Add your Shodan API key to your `.env` file:

```env
SHODAN_API_KEY=your_api_key_here
```

Or set it as an environment variable:

```bash
export SHODAN_API_KEY=your_api_key_here
```

### 3. Update Settings in Dashboard

Navigate to Settings → API Keys and add your Shodan API key through the web interface.

## API Endpoints

### 1. Get Shodan Search URL
Get the Shodan search page URL for a domain (no API key required).

**Endpoint:** `GET /api/domains/shodan/search-url/{domain_id}`

**Response:**
```json
{
  "domain": "example.com",
  "search_url": "https://www.shodan.io/search?query=example.com",
  "redirect_url": "https://www.shodan.io/search?query=example.com"
}
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/shodan/search-url/1
```

### 2. Get Shodan API Data
Fetch detailed Shodan intelligence for a domain. Returns cached data if available (< 24 hours old).

**Endpoint:** `GET /api/domains/{domain_id}/shodan`

**Response:**
```json
{
  "domain": "example.com",
  "data": {
    "status": "success",
    "total_results": 5,
    "results_found": 5,
    "fetched_at": "2025-12-15T10:30:00",
    "search_url": "https://www.shodan.io/search?query=example.com",
    "devices": [
      {
        "ip": "192.0.2.1",
        "port": 443,
        "hostnames": ["example.com", "www.example.com"],
        "org": "Example Corporation",
        "isp": "Example ISP",
        "os": "Linux",
        "last_update": "2025-12-15T08:00:00Z",
        "services": null
      }
    ]
  },
  "cached": false,
  "last_checked": "2025-12-15T10:30:00",
  "search_url": "https://www.shodan.io/search?query=example.com"
}
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/1/shodan
```

### 3. Refresh All Shodan Data
Refresh Shodan data for all domains (admin only).

**Endpoint:** `POST /api/domains/shodan/refresh-all`

**Response:**
```json
{
  "total": 10,
  "updated": 10,
  "failed": 0,
  "errors": []
}
```

**Usage:**
```bash
curl -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/domains/shodan/refresh-all
```

## Data Structure

### Domain Model Updates

The Domain model now includes:

```python
class Domain(Base):
    # ... existing fields ...
    shodan_data = Column(JSON, nullable=True)  # Cached Shodan data
    shodan_last_checked = Column(DateTime, nullable=True)  # Last update timestamp
```

### Shodan Response Data

**Success Response:**
```json
{
  "status": "success",
  "total_results": <number>,
  "results_found": <number>,
  "fetched_at": <ISO timestamp>,
  "search_url": <string>,
  "devices": [
    {
      "ip": <string>,
      "port": <number>,
      "hostnames": [<string>, ...],
      "org": <string>,
      "isp": <string>,
      "os": <string>,
      "last_update": <string>,
      "services": <object or null>
    }
  ]
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": <error message>,
  "search_url": <string>
}
```

## Usage Examples

### Example 1: Get Shodan Data via Python

```python
import requests

# Set your token
headers = {"Authorization": "Bearer your_token"}

# Get Shodan data for domain ID 1
response = requests.get(
    "http://localhost:8000/api/domains/1/shodan",
    headers=headers
)

data = response.json()
print(f"Domain: {data['domain']}")
print(f"Total results: {data['data']['total_results']}")

for device in data['data']['devices']:
    print(f"  - IP: {device['ip']}, Port: {device['port']}")
```

### Example 2: Get Search URL via JavaScript

```javascript
async function getShodanSearchUrl(domainId) {
  const token = localStorage.getItem('token');
  
  const response = await fetch(
    `/api/domains/shodan/search-url/${domainId}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  
  const data = await response.json();
  window.open(data.search_url, '_blank');
}
```

### Example 3: Refresh All Data via cURL

```bash
# Refresh all Shodan data (admin only)
curl -X POST \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/domains/shodan/refresh-all
```

## Caching Strategy

- **Cache Duration**: 24 hours
- **Cache Location**: Database (shodan_data column)
- **Last Updated**: Tracked in shodan_last_checked column
- **Cache Invalidation**: Manual via refresh endpoint or automatic after 24 hours

## Rate Limiting

Shodan API has the following rate limits:

- **Free Plan**: 1 query/month
- **Educational**: 10 queries/month
- **Professional**: Unlimited

The implementation caches results to minimize API calls.

## Error Handling

### API Key Not Configured
```json
{
  "status": "unavailable",
  "message": "No data available"
}
```

### Invalid API Key
```json
{
  "status": "error",
  "error": "Invalid Shodan API key",
  "search_url": "https://www.shodan.io/search?query=example.com"
}
```

### API Timeout
```json
{
  "status": "error",
  "error": "API request timeout",
  "search_url": "https://www.shodan.io/search?query=example.com"
}
```

## Database Migration

If you're upgrading an existing installation, run the migration to add Shodan columns:

```bash
# The migration will automatically create:
# - shodan_data (JSON column)
# - shodan_last_checked (DateTime column)
```

## Security Considerations

1. **API Key Protection**: Store your API key in environment variables, never in code
2. **Rate Limiting**: Monitor your Shodan API usage to avoid hitting rate limits
3. **Access Control**: Only admin users can refresh all data; regular users can view results
4. **HTTPS Only**: Always use HTTPS in production to protect API keys in transit

## Troubleshooting

### Issue: "Shodan API key not configured"

**Solution**: Set the `SHODAN_API_KEY` environment variable or add it through the Settings UI.

### Issue: Getting timeout errors

**Solution**: Check your network connectivity to api.shodan.io. The API may also be experiencing high load.

### Issue: Invalid API key error

**Solution**: Verify your API key is correct by testing it on shodan.io directly.

### Issue: Rate limit exceeded

**Solution**: Upgrade your Shodan plan or wait for the rate limit reset period.

## API Response Examples

### Real Domain Example

**Request:**
```bash
GET /api/domains/1/shodan
```

**Response:**
```json
{
  "domain": "zarinpal.com",
  "data": {
    "status": "success",
    "total_results": 12,
    "results_found": 12,
    "fetched_at": "2025-12-15T14:22:31.456789",
    "search_url": "https://www.shodan.io/search?query=zarinpal.com",
    "devices": [
      {
        "ip": "185.139.116.130",
        "port": 443,
        "hostnames": ["zarinpal.com", "www.zarinpal.com"],
        "org": "Arvancloud",
        "isp": "Arvancloud Ltd",
        "os": "Linux",
        "last_update": "2025-12-15T10:00:00Z",
        "services": {
          "cipher": {
            "bits": 256,
            "name": "ECDHE-RSA-AES256-GCM-SHA384"
          },
          "versions": ["TLSv1.2", "TLSv1.3"]
        }
      }
    ]
  },
  "cached": false,
  "last_checked": "2025-12-15T14:22:31.456789",
  "search_url": "https://www.shodan.io/search?query=zarinpal.com"
}
```

## Future Enhancements

Potential improvements for the Shodan integration:

1. **Vulnerability Detection** - Highlight known vulnerabilities found in Shodan data
2. **Alerts** - Notify admins when new exposed services are detected
3. **Historical Tracking** - Store historical Shodan data for trend analysis
4. **Port Monitoring** - Alert on unexpected new ports opening
5. **SSL/TLS Analysis** - Integrate with Shodan's SSL data
6. **GeoIP Mapping** - Display device locations on a map
