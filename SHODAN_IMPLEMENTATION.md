# Shodan Integration - Implementation Summary

## Overview
Complete Shodan intelligence integration has been added to the SSL Checker application. This allows monitoring and gathering security intelligence for all monitored domains through the Shodan search engine.

## Files Added

### 1. **`app/services/shodan_service.py`** (NEW)
Core service for Shodan integration with:
- `get_shodan_search_url()` - Generate Shodan search URLs
- `fetch_shodan_api_data()` - Fetch data from Shodan API
- `fetch_shodan_data_batch()` - Batch fetch for multiple domains
- `parse_shodan_results()` - Format and parse API responses

### 2. **`SHODAN_INTEGRATION.md`** (NEW)
Complete documentation including:
- Feature overview
- Setup instructions
- API endpoint documentation
- Usage examples
- Error handling
- Security considerations
- Troubleshooting guide

### 3. **`SHODAN_QUICKSTART.md`** (NEW)
Quick start guide for getting up and running in minutes

### 4. **`static/shodan_panel.html`** (NEW)
Dashboard UI component for displaying Shodan data:
- Modal popup for Shodan results
- Device listing
- Service information display
- Responsive styling

## Files Modified

### 1. **`app/models/all_models.py`**
Added to `Domain` model:
```python
shodan_data = Column(JSON, nullable=True)           # Cache Shodan data
shodan_last_checked = Column(DateTime, nullable=True)  # Last update time
```

Added to `AppSettings` model:
```python
shodan_api_key = Column(String, nullable=True)  # Shodan API key storage
```

### 2. **`app/routers/domains.py`**
Added new endpoints:
- `GET /api/domains/{did}/shodan` - Get Shodan data for a domain
- `GET /api/domains/shodan/search-url/{did}` - Get Shodan search URL
- `POST /api/domains/shodan/refresh-all` - Refresh all domains' Shodan data

### 3. **`app/core/config.py`**
Added configuration:
```python
self.shodan_api_key = os.environ.get("SHODAN_API_KEY", "")
```

### 4. **`app/schemas/schemas.py`**
Added to `SettingsUpdate` schema:
```python
shodan_api_key: Optional[str] = None
```

### 5. **`requirements.txt`**
Added dependency:
```
shodan>=1.28.0
```

## Key Features

### 1. **Search URL Generation** (No API Key Required)
- Direct links to Shodan search pages for each domain
- Format: `https://www.shodan.io/search?query={domain}`
- Example: `https://www.shodan.io/search?query=zarinpal.com`

### 2. **API Data Fetching** (Requires API Key)
- Detailed device and service information
- IP addresses, ports, hostnames
- Organization and ISP details
- Operating system information

### 3. **Smart Caching**
- 24-hour cache to minimize API calls
- Automatic cache invalidation after 24 hours
- Manual refresh capability

### 4. **Batch Operations**
- Refresh data for all domains at once
- Admin-only endpoint with error reporting

## API Endpoints

```
GET    /api/domains/{did}/shodan
       Fetch Shodan data for a domain (with caching)

GET    /api/domains/shodan/search-url/{did}
       Get Shodan search URL (no API key required)

POST   /api/domains/shodan/refresh-all
       Refresh Shodan data for all domains (admin only)
```

## Database Schema Changes

### Domain Table
```sql
ALTER TABLE domains ADD COLUMN shodan_data JSON;
ALTER TABLE domains ADD COLUMN shodan_last_checked TIMESTAMP;
```

### AppSettings Table
```sql
ALTER TABLE settings ADD COLUMN shodan_api_key VARCHAR;
```

## Configuration

### Environment Variables
```env
SHODAN_API_KEY=your_api_key_here
```

### Dashboard Settings
Users can add their API key via Settings → API Keys interface

## Usage Example

```bash
# Get Shodan search URL (no auth needed)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/domains/1/shodan/search-url

# Get detailed Shodan data
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/domains/1/shodan

# Refresh all Shodan data (admin)
curl -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/domains/shodan/refresh-all
```

## Response Format

### Success Response
```json
{
  "domain": "example.com",
  "data": {
    "status": "success",
    "total_results": 5,
    "results_found": 5,
    "devices": [
      {
        "ip": "192.0.2.1",
        "port": 443,
        "hostnames": ["example.com"],
        "org": "Example Corp",
        "isp": "Example ISP",
        "os": "Linux"
      }
    ]
  },
  "cached": false,
  "last_checked": "2025-12-15T10:30:00"
}
```

## Security Considerations

1. **API Key Storage**: Stored in database or environment variables only
2. **Access Control**: Regular users can view, only admins can refresh all
3. **HTTPS Required**: Always use HTTPS in production
4. **Rate Limiting**: Built-in caching respects Shodan API limits
5. **No Key Exposure**: API keys never exposed in responses

## Rate Limits

- **Free Plan**: 1 query/month
- **Educational**: 10 queries/month
- **Professional**: Unlimited

The 24-hour caching strategy helps stay within limits.

## Integration Steps for Existing Installation

1. **Install new package**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add environment variable**:
   ```bash
   export SHODAN_API_KEY=your_key
   ```

3. **No database migration needed** - columns created automatically on first use

4. **Add UI buttons** - Include the `shodan_panel.html` in your dashboard template

## Testing

```bash
# Test API availability (no key required)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/domains/1/shodan/search-url

# Test with API key (requires SHODAN_API_KEY set)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/domains/1/shodan
```

## Future Enhancements

1. **Vulnerability Detection** - Alert on CVEs found via Shodan
2. **Historical Tracking** - Store trends over time
3. **Port Monitoring** - Alert on new open ports
4. **GeoIP Mapping** - Visualize device locations
5. **Advanced Filtering** - Filter by port, protocol, services
6. **Automated Alerts** - Notify on security changes

## Troubleshooting

### No Shodan Data Showing
1. Check if API key is configured
2. Verify API key is valid
3. Check network connectivity to api.shodan.io

### Getting Timeout Errors
1. Check internet connection
2. Verify Shodan API status
3. Increase timeout settings if needed

### Rate Limit Exceeded
1. Upgrade Shodan plan
2. Rely on 24-hour cache between requests
3. Schedule bulk refreshes during off-hours

## Support

For more information:
- [Shodan Documentation](https://www.shodan.io/api_docs)
- [Shodan Query Help](https://www.shodan.io/search/filters)
- [SHODAN_INTEGRATION.md](./SHODAN_INTEGRATION.md)
- [SHODAN_QUICKSTART.md](./SHODAN_QUICKSTART.md)
