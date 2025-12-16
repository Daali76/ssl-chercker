# Shodan Integration - Quick Start

## 1. Get Your API Key

```bash
# Visit https://www.shodan.io and sign up
# Get your API key from Account Settings
```

## 2. Add to Environment

```bash
# Add to .env file
echo "SHODAN_API_KEY=your_key_here" >> .env

# Or export directly
export SHODAN_API_KEY=your_key_here
```

## 3. Access Shodan Features

### Option A: Direct Search URL (No API Key Needed)
```bash
# Get Shodan search link for any domain
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/shodan/search-url/1
```

**Response:**
```json
{
  "domain": "zarinpal.com",
  "search_url": "https://www.shodan.io/search?query=zarinpal.com"
}
```

Click the search_url to view Shodan results!

### Option B: API Data (Requires API Key)
```bash
# Get detailed Shodan data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/1/shodan
```

## 4. View in Dashboard

After adding the API key, you'll see:
- Shodan results for each domain
- Number of exposed services
- IP addresses and ports
- Organization and ISP info
- Last scan timestamp

## 5. Refresh All Data

```bash
# Admin only - refresh all domains
curl -X POST \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/domains/shodan/refresh-all
```

## Common Queries

### Search for all services on a domain
```
https://www.shodan.io/search?query=example.com
```

### Search for specific port
```
https://www.shodan.io/search?query=example.com:443
```

### Search for IP with organization
```
https://www.shodan.io/search?query=org:"Example Corp"
```

## API Limits

- **Free**: 1 query/month
- **Educational**: 10 queries/month  
- **Professional**: Unlimited

💡 The app caches results for 24 hours to stay within limits!

## Next Steps

- Read [SHODAN_INTEGRATION.md](./SHODAN_INTEGRATION.md) for detailed documentation
- Set up notifications for new exposed services
- Monitor Shodan data trends over time
