# Shodan Integration - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Integration](#integration)
5. [Testing](#testing)
6. [Dashboard Integration](#dashboard-integration)
7. [Common Tasks](#common-tasks)

## Prerequisites

- Python 3.8+
- FastAPI application running
- PostgreSQL or compatible database
- Internet connection (for Shodan API)

## Installation

### Step 1: Install Dependencies

```bash
# Update your Python environment
pip install -r requirements.txt

# This will install the new Shodan package
pip install shodan>=1.28.0
```

### Step 2: Update Environment File

Add to your `.env` file:

```env
# Shodan Configuration
SHODAN_API_KEY=your_shodan_api_key_here

# Optional: Proxy configuration (if needed)
# PROXY_URL=http://proxy-server:8080
```

### Step 3: Get Your API Key

1. Visit [https://www.shodan.io](https://www.shodan.io)
2. Sign up for a free or premium account
3. Navigate to Account → API Key
4. Copy your API key
5. Add it to your `.env` file

## Configuration

### Via Environment Variables

```bash
export SHODAN_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"
```

### Via Dashboard Settings

1. Log in to your SSL Checker dashboard as admin
2. Go to Settings → API Keys
3. Paste your Shodan API key
4. Click Save

### Verify Configuration

```bash
# Test if the environment variable is loaded
python -c "import os; print('SHODAN_API_KEY:', os.getenv('SHODAN_API_KEY'))"
```

## Integration

### Database Schema Updates

The following columns are automatically added to existing tables:

**domains table:**
```sql
ALTER TABLE domains ADD COLUMN shodan_data JSON DEFAULT NULL;
ALTER TABLE domains ADD COLUMN shodan_last_checked TIMESTAMP DEFAULT NULL;
```

**settings table:**
```sql
ALTER TABLE settings ADD COLUMN shodan_api_key VARCHAR(255) DEFAULT NULL;
```

These will be created automatically when the models are initialized.

### API Integration

All new endpoints are automatically registered with the FastAPI application:

```python
# In app/routers/domains.py - Already added
@router.get("/{did}/shodan")
@router.get("/shodan/search-url/{did}")
@router.post("/shodan/refresh-all")
```

## Testing

### Test 1: Check if Service Loads

```bash
python -c "from app.services.shodan_service import ShodanService; print('✓ Shodan service loaded')"
```

### Test 2: Generate Search URL

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/1/shodan/search-url
```

**Expected Response:**
```json
{
  "domain": "example.com",
  "search_url": "https://www.shodan.io/search?query=example.com",
  "redirect_url": "https://www.shodan.io/search?query=example.com"
}
```

### Test 3: Fetch Shodan Data

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/domains/1/shodan
```

**Expected Response:**
```json
{
  "domain": "example.com",
  "data": {
    "status": "success",
    "total_results": 5,
    "results_found": 5,
    "devices": [...]
  },
  "cached": false,
  "last_checked": "2025-12-15T10:30:00"
}
```

### Test 4: Refresh All (Admin)

```bash
curl -X POST \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/domains/shodan/refresh-all
```

## Dashboard Integration

### Add Shodan Button to Domain List

In your `dashboard.html`, add to the domain list table:

```html
<button 
  class="btn btn-sm btn-info"
  onclick="viewShodanData(${domain.id}, '${domain.url}')"
  title="View Shodan Intelligence">
  <i class="fas fa-search"></i> Shodan
</button>
```

### Include the Shodan Panel Component

Add to your HTML template:

```html
<!-- Include Shodan Modal -->
<script src="/static/shodan_panel.html"></script>

<!-- Or copy the styles and scripts directly -->
```

### Add Admin Settings Form

In your settings page, add:

```html
<div class="form-group">
  <label for="shodan_api_key">Shodan API Key</label>
  <input 
    type="password" 
    class="form-control" 
    id="shodan_api_key"
    placeholder="Enter your Shodan API key">
  <small class="form-text text-muted">
    Get your key from <a href="https://www.shodan.io/account/api" target="_blank">shodan.io/account/api</a>
  </small>
</div>

<script>
// Save Shodan API key
document.getElementById('save-settings-btn').addEventListener('click', async () => {
  const apiKey = document.getElementById('shodan_api_key').value;
  
  const response = await fetch('/api/settings', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ shodan_api_key: apiKey })
  });
  
  if (response.ok) {
    showAlert('Shodan API key saved!', 'success');
  }
});
</script>
```

## Common Tasks

### Task 1: Fetch Shodan Data for a Single Domain

```python
import asyncio
from app.services.shodan_service import ShodanService

async def check_domain():
    service = ShodanService(api_key="your_api_key")
    data = await service.fetch_shodan_api_data("example.com")
    parsed = ShodanService.parse_shodan_results(data)
    print(parsed)

asyncio.run(check_domain())
```

### Task 2: Generate Bulk Report

```bash
#!/bin/bash

# Get list of all domains
DOMAINS=$(curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/domains | jq -r '.[].id')

# Fetch Shodan data for each
for DOMAIN_ID in $DOMAINS; do
  echo "Domain ID: $DOMAIN_ID"
  curl -H "Authorization: Bearer TOKEN" \
    http://localhost:8000/api/domains/$DOMAIN_ID/shodan/search-url
done
```

### Task 3: Monitor for Changes

```python
import time
import requests

def monitor_domains(token, interval=3600):
    """Monitor domains every hour for Shodan data changes"""
    
    while True:
        # Get all domains
        domains = requests.get(
            "http://localhost:8000/api/domains",
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        # Refresh Shodan data
        result = requests.post(
            "http://localhost:8000/api/domains/shodan/refresh-all",
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        print(f"Updated: {result['updated']}, Failed: {result['failed']}")
        
        # Wait for next interval
        time.sleep(interval)

# Run with: monitor_domains(token="your_token")
```

### Task 4: Export Shodan Report

```python
import json
import requests

def export_shodan_report(token, output_file="shodan_report.json"):
    """Export all Shodan data to JSON"""
    
    domains = requests.get(
        "http://localhost:8000/api/domains",
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    report = {}
    
    for domain in domains:
        data = requests.get(
            f"http://localhost:8000/api/domains/{domain['id']}/shodan",
            headers={"Authorization": f"Bearer {token}"}
        ).json()
        
        report[domain['url']] = data
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {output_file}")

# Run with: export_shodan_report(token="your_token")
```

## Troubleshooting

### Issue: "Module 'shodan' not found"

**Solution:** Install the package
```bash
pip install shodan>=1.28.0
```

### Issue: "Shodan API key not configured"

**Solution:** Set environment variable
```bash
export SHODAN_API_KEY=your_key
```

### Issue: "API request timeout"

**Solution:** Check network connectivity
```bash
ping api.shodan.io
```

### Issue: "Invalid Shodan API key"

**Solution:** Verify key at https://www.shodan.io/account/api

### Issue: "Rate limit exceeded"

**Solution:** Upgrade Shodan plan or wait for reset

## Next Steps

1. Review [SHODAN_INTEGRATION.md](./SHODAN_INTEGRATION.md) for detailed API documentation
2. Read [SHODAN_QUICKSTART.md](./SHODAN_QUICKSTART.md) for quick reference
3. Check [examples/shodan_example.py](./examples/shodan_example.py) for code samples
4. Set up monitoring and alerting for changes

## Support Resources

- **Shodan API Documentation**: https://www.shodan.io/api_docs
- **Shodan Query Help**: https://www.shodan.io/search/filters
- **Shodan Forum**: https://forums.shodan.io
- **Email Support**: support@shodan.io

## Security Reminders

✅ **DO:**
- Store API keys in environment variables
- Use HTTPS in production
- Limit API key permissions if possible
- Monitor API usage

❌ **DON'T:**
- Commit API keys to version control
- Share API keys in messages/emails
- Use in client-side code
- Log API keys to files

## Additional Notes

- **Cache Duration**: 24 hours (configurable in shodan_service.py)
- **API Rate Limits**: Check your Shodan plan for limits
- **Async Operations**: All API calls are async-safe
- **Database**: No separate migrations needed, columns created automatically

For more information, visit: https://www.shodan.io
