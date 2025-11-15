# CyberGuard API Integration Guide

## Overview

CyberGuard έχει ενσωματώσει μια **REST API** που επιτρέπει:
- Ανάλυση emails μέσω HTTP requests
- Αποθήκευση και ανάκτηση ιστορικού
- Λήψη στατιστικών και απειλών
- Σύνδεση με εξωτερικές εφαρμογές

## Architecture

```
┌─────────────────────────────────────┐
│   Desktop GUI Application            │
│   (CyberGuard_Desktop_API.py)        │
│                                      │
│   - Tkinter Interface                │
│   - Real-time Analysis               │
│   - Local copy/paste support         │
└──────────────┬──────────────────────┘
               │ HTTP Requests
               │ (REST API)
               ▼
┌─────────────────────────────────────┐
│   Flask API Server                   │
│   (CyberGuard_API.py)                │
│   Running on: http://localhost:5000  │
│                                      │
│   - /api/v1/analyze (POST)           │
│   - /api/v1/history (GET)            │
│   - /api/v1/threats (GET)            │
│   - /api/v1/statistics (GET)         │
│   - /api/v1/health (GET)             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   JSON Database                      │
│   (cyberguard_api_db.json)           │
│                                      │
│   - Analysis History                 │
│   - Threat Records                   │
└─────────────────────────────────────┘
```

## Installation & Setup

### 1. Install Dependencies

```powershell
pip install flask flask-cors scikit-learn numpy requests
```

### 2. Start API Server

```powershell
python C:\Users\User\Desktop\CyberGuard_API.py
```

Output:
```
════════════════════════════════════════════════════════
CyberGuard API Server v1.0
════════════════════════════════════════════════════════
Starting server on http://localhost:5000
API documentation: http://localhost:5000/api/v1/info
════════════════════════════════════════════════════════
```

### 3. Run Desktop Application

```powershell
python C:\Users\User\Desktop\CyberGuard_Desktop_API.py
```

The application will automatically detect and connect to the API.

### 4. (Optional) Test API with Client Script

```powershell
python C:\Users\User\Desktop\CyberGuard_API_Client.py
```

## API Endpoints

### 1. Health Check
```
GET /api/v1/health

Response:
{
  "status": "healthy",
  "api_version": "1.0",
  "service": "CyberGuard API",
  "timestamp": "2025-11-15T10:30:45.123456"
}
```

### 2. Analyze Email
```
POST /api/v1/analyze

Request:
{
  "email_text": "Email content here...",
  "subject": "Email Subject"
}

Response:
{
  "risk_level": "DANGEROUS",
  "risk_score": 0.75,
  "keyword_score": 0.80,
  "pattern_score": 0.70,
  "ml_score": 0.75,
  "keywords_found": ["verify", "urgent", "account"],
  "patterns_found": {
    "urls": ["http://suspicious.com"],
    "emails": ["noreply@fake.com"],
    "ips": ["192.168.1.1"],
    "suspicious_phrases": 2
  },
  "analysis_id": "analysis_20251115_103045_123456",
  "subject": "Email Subject",
  "email_length": 250,
  "timestamp": "2025-11-15T10:30:45.123456"
}
```

### 3. Get Analysis History
```
GET /api/v1/history?limit=50&risk_level=DANGEROUS

Query Parameters:
- limit: Number of records (default: 50)
- risk_level: Filter by SAFE|SUSPICIOUS|DANGEROUS (optional)

Response:
{
  "total_count": 150,
  "filtered_count": 25,
  "analyses": [
    {
      "risk_level": "DANGEROUS",
      "risk_score": 0.75,
      "subject": "URGENT: Update Your Password",
      "timestamp": "2025-11-15T10:30:45.123456",
      ...
    }
  ]
}
```

### 4. Get Threats
```
GET /api/v1/threats?limit=20

Response:
{
  "total_threats": 45,
  "critical_threats": 12,
  "threats": [
    {
      "threat_id": "analysis_20251115_103045_123456",
      "subject": "URGENT: Update Your Password",
      "risk_level": "DANGEROUS",
      "risk_score": 0.75,
      "timestamp": "2025-11-15T10:30:45.123456",
      "keywords": ["verify", "urgent", "account"]
    }
  ]
}
```

### 5. Get Statistics
```
GET /api/v1/statistics

Response:
{
  "total_analyses": 150,
  "safe_count": 50,
  "suspicious_count": 75,
  "dangerous_count": 25,
  "safe_percentage": 33.33,
  "suspicious_percentage": 50.0,
  "dangerous_percentage": 16.67,
  "average_risk_score": 0.45
}
```

### 6. Get API Info
```
GET /api/v1/info

Response:
{
  "api_version": "1.0",
  "service": "CyberGuard API",
  "description": "REST API for phishing email detection",
  "endpoints": {
    "health": {...},
    "analyze": {...},
    "history": {...},
    ...
  }
}
```

### 7. Clear Database
```
POST /api/v1/clear

Response:
{
  "status": "success",
  "message": "Database cleared"
}
```

## Usage Examples

### Using Python Requests Library

```python
import requests

# Analyze email
response = requests.post(
    'http://localhost:5000/api/v1/analyze',
    json={
        'email_text': 'Click here to verify your account!',
        'subject': 'Verify Your Account'
    }
)

print(response.json())

# Get statistics
response = requests.get('http://localhost:5000/api/v1/statistics')
stats = response.json()
print(f"Total: {stats['total_analyses']}")
print(f"Dangerous: {stats['dangerous_count']}")
```

### Using cURL

```bash
# Analyze email
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "Click here to verify your account!",
    "subject": "Verify Account"
  }'

# Get statistics
curl http://localhost:5000/api/v1/statistics

# Get history
curl "http://localhost:5000/api/v1/history?limit=10&risk_level=DANGEROUS"
```

### Using JavaScript/Fetch

```javascript
// Analyze email
const response = await fetch('http://localhost:5000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email_text: 'Click here to verify your account!',
    subject: 'Verify Account'
  })
});

const result = await response.json();
console.log(result);

// Get statistics
const statsResponse = await fetch('http://localhost:5000/api/v1/statistics');
const stats = await statsResponse.json();
console.log(stats);
```

## Database Structure

### cyberguard_api_db.json

```json
{
  "analyses": [
    {
      "risk_level": "DANGEROUS",
      "risk_score": 0.75,
      "keyword_score": 0.80,
      "pattern_score": 0.70,
      "ml_score": 0.75,
      "keywords_found": ["verify", "urgent"],
      "patterns_found": {...},
      "analysis_id": "analysis_20251115_103045_123456",
      "subject": "Subject",
      "email_length": 250,
      "timestamp": "2025-11-15T10:30:45.123456"
    }
  ],
  "threats": [
    {
      "threat_id": "analysis_20251115_103045_123456",
      "subject": "Subject",
      "risk_level": "DANGEROUS",
      "risk_score": 0.75,
      "timestamp": "2025-11-15T10:30:45.123456",
      "keywords": ["verify", "urgent"]
    }
  ]
}
```

## Files Overview

### 1. CyberGuard_API.py (Flask Server)
- Main API server
- Detection algorithms
- ML model training
- Database management
- 600+ lines

### 2. CyberGuard_Desktop_API.py (GUI Client)
- Tkinter desktop application
- API integration
- Real-time analysis
- History and statistics tabs
- 700+ lines

### 3. CyberGuard_API_Client.py (Test Client)
- API testing utility
- Example usage
- Comprehensive test suite
- 300+ lines

### 4. cyberguard_api_db.json (Database)
- JSON database
- Analysis history
- Threat records
- Auto-created on first analysis

## Features

### ✅ Implemented
- [x] REST API with 7 endpoints
- [x] Real-time email analysis
- [x] Analysis history storage
- [x] Threat detection and tracking
- [x] Statistics and metrics
- [x] Multi-detection methods
- [x] Greek language support
- [x] JSON database
- [x] CORS support
- [x] Error handling

### 🔄 Future Enhancements
- [ ] Authentication (API key/token)
- [ ] Rate limiting
- [ ] Database migration to SQLite/PostgreSQL
- [ ] Webhook notifications
- [ ] Scheduled scanning
- [ ] Email server integration (IMAP/SMTP)
- [ ] Web dashboard
- [ ] Docker containerization
- [ ] API versioning (v2, v3)

## Troubleshooting

### API Server Won't Start
```powershell
# Check if port 5000 is in use
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

# Kill process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

### Desktop App Can't Connect to API
1. Ensure API server is running
2. Check http://localhost:5000/api/v1/health
3. Verify firewall settings
4. Check console for error messages

### Database File Not Found
- Database is auto-created on first analysis
- Location: `C:\Users\User\Desktop\cyberguard_api_db.json`
- Manually create if needed

### Import Errors
```powershell
pip install flask flask-cors scikit-learn numpy requests
```

## Performance Metrics

### Analysis Speed
- API: ~50-100ms per email
- Desktop GUI: ~200-300ms (includes UI updates)
- ML Model: ~10-20ms

### Database Size
- Per analysis: ~2KB average
- 1000 analyses: ~2MB
- JSON format keeps it human-readable

### Memory Usage
- API server: ~100-150MB
- ML model: ~50MB
- Database in memory: Loaded on demand

## Security Notes

⚠️ **For Production Deployment:**
1. Add authentication (JWT, API keys)
2. Implement rate limiting
3. Use HTTPS/TLS
4. Run behind reverse proxy (nginx)
5. Implement API versioning
6. Add comprehensive logging
7. Use environment variables for secrets
8. Consider database encryption

## Contact & Support

For issues or suggestions about the API integration:
- Check the logs: API console output
- Test endpoints manually: Use cURL or Postman
- Review database: cyberguard_api_db.json
- Enable debug mode: Set `debug=True` in Flask app

---

**Version:** 2.1 (API Integrated)  
**Last Updated:** November 15, 2025  
**License:** MIT Open Source
