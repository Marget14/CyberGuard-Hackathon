# CyberGuard v2.1 - Email Phishing Detection System
## REST API & Desktop Application

[Ελληνικά στο κάτω μέρος]

---

## 📋 Overview

**CyberGuard** is a comprehensive phishing email detection system with:
- ✅ **REST API Backend** for programmatic access
- ✅ **Modern Desktop GUI** with real-time analysis  
- ✅ **Machine Learning** phishing detection
- ✅ **Analysis History & Statistics**
- ✅ **Greek Language Support** (Δήμος Αθηναίων)
- ✅ **No Cloud Dependencies** - Local processing only

Perfect for **City Challenge Apps4Athens Hackathon 2.0** - Athens Municipality

---

## 🚀 Quick Start

### Option 1: Automatic Launcher (Recommended)

**Windows - Batch File:**
```batch
C:\Users\User\Desktop\START_MUNICIPAL.bat
```

**Windows - PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\START_MUNICIPAL.ps1"
```

This will automatically:
1. Start the API server on port 5000
2. Launch the desktop application
3. Test the connection
4. Manage both processes

### Option 2: Manual Start

**Terminal 1 - Start API Server:**
```powershell
python C:\Users\User\Desktop\CyberGuard_API.py
```

Output:
```
============================================================
CyberGuard API Server v1.0
============================================================
Starting server on http://localhost:5000
API documentation: http://localhost:5000/api/v1/info
============================================================
 * Running on http://127.0.0.1:5000
```

**Terminal 2 - Start Desktop Application:**
```powershell
python C:\Users\User\Desktop\CyberGuard_Desktop_API.py
```

### Option 3: Test API Only

```powershell
python C:\Users\User\Desktop\CyberGuard_API_Client.py
```

---

## 📦 Installation

### Prerequisites
- Python 3.13+
- Windows 7/10/11 (or Linux/macOS with minor modifications)

### Step 1: Install Dependencies
```powershell
pip install flask flask-cors scikit-learn numpy requests
```

### Step 2: Verify Files
All files should be in `C:\Users\User\Desktop\`:
- ✅ `CyberGuard_API.py` - Flask REST API server
- ✅ `CyberGuard_Desktop_API.py` - Tkinter desktop GUI
- ✅ `CyberGuard_API_Client.py` - API test client
- ✅ `START_MUNICIPAL.ps1` - PowerShell launcher
- ✅ `START_MUNICIPAL.bat` - Batch launcher
- ✅ `API_GUIDE.md` - Detailed API documentation
- ✅ `README.md` - This file

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│         WEB CLIENTS / EXTERNAL APPLICATIONS              │
│              (JavaScript, cURL, Postman)                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
                     │ (Port 5000)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FLASK API SERVER                            │
│         (CyberGuard_API.py)                              │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  DETECTION ENGINE                               │  │
│  │  • Keyword Detection (60+ keywords)              │  │
│  │  • Pattern Detection (URLs, IPs, emails)         │  │
│  │  • Machine Learning (Logistic Regression)        │  │
│  │  • Combined Risk Scoring                         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ENDPOINTS                                       │  │
│  │  POST   /api/v1/analyze                         │  │
│  │  GET    /api/v1/history                         │  │
│  │  GET    /api/v1/threats                         │  │
│  │  GET    /api/v1/statistics                      │  │
│  │  GET    /api/v1/health                          │  │
│  │  GET    /api/v1/info                            │  │
│  │  POST   /api/v1/clear                           │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ local calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│              DESKTOP GUI APPLICATION                    │
│         (CyberGuard_Desktop_API.py - Tkinter)           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  TABS                                            │  │
│  │  • Analyzer - Real-time email analysis           │  │
│  │  • History - Analysis history with filters       │  │
│  │  • Statistics - Trend analysis & metrics         │  │
│  │  • About - Application information               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  FEATURES                                        │  │
│  │  • Copy/Paste from external apps                │  │
│  │  • Load PDF/DOCX/TXT files                      │  │
│  │  • Real-time analysis as you type               │  │
│  │  • Dark/Light theme toggle                      │  │
│  │  • Greek language support                       │  │
│  │  • Keyboard shortcuts (Ctrl+O, Ctrl+V, etc)     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              JSON DATABASE                              │
│     (cyberguard_api_db.json)                            │
│                                                          │
│  • Analysis History (all emails analyzed)              │
│  • Threat Records (dangerous emails)                   │
│  • Statistics (aggregated metrics)                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Features

### Detection Methods

#### 1. **Keyword Detection** (30% weight)
- 60+ suspicious keywords in English & Greek
- Categories: Verification, Payment, Urgent, Brands
- Case-insensitive matching
- Examples: "verify", "urgent", "click here", "account suspended"

#### 2. **Pattern Detection** (35% weight)
- **URLs**: Detects HTTP/HTTPS links
- **IP Addresses**: Flags direct IP access (+0.35 score)
- **Email Addresses**: Identifies suspicious senders
- **Suspicious Phrases**: Multi-word patterns
- Bonus scoring for multiple patterns

#### 3. **Machine Learning** (35% weight)
- **Algorithm**: Logistic Regression
- **Features**: Keyword count, URL count, email count, urgency score, IP count
- **Training Data**: 8 labeled phishing/legitimate emails
- **Real-time Scoring**: 0.0-1.0 probability

### Risk Classification
- **🟢 SAFE**: Score < 0.25
- **🟡 SUSPICIOUS**: Score 0.25-0.55
- **🔴 DANGEROUS**: Score > 0.55

### User Interface
- **Real-time Analysis**: Analyzes as you type
- **Copy/Paste**: Ctrl+V from Gmail, Outlook, etc.
- **File Loading**: PDF, DOCX, TXT, HTML, EML support
- **History Tracking**: All analyses stored
- **Statistics Dashboard**: Risk distribution, trends
- **Dark/Light Themes**: Eye-friendly interface
- **Keyboard Shortcuts**:
  - `Ctrl+O` - Open file
  - `Ctrl+V` - Paste from clipboard
  - `Ctrl+A` - Select all
  - `Ctrl+C` - Copy
  - `Ctrl+Return` - Analyze

### API Integration
- **7 RESTful Endpoints**
- **JSON Database**: Auto-saves all analyses
- **CORS Support**: Cross-origin requests allowed
- **Error Handling**: Comprehensive error messages
- **Extensible Design**: Easy to add new endpoints

---

## 🔌 API Usage

### Health Check
```bash
GET http://localhost:5000/api/v1/health

Response:
{
  "status": "healthy",
  "api_version": "1.0",
  "service": "CyberGuard API",
  "timestamp": "2025-11-15T10:30:45"
}
```

### Analyze Email
```bash
POST http://localhost:5000/api/v1/analyze

Body:
{
  "email_text": "Click here to verify your account!",
  "subject": "Verify Account"
}

Response:
{
  "risk_level": "DANGEROUS",
  "risk_score": 0.75,
  "keyword_score": 0.80,
  "pattern_score": 0.70,
  "ml_score": 0.75,
  "keywords_found": ["verify", "click here"],
  "patterns_found": {
    "urls": ["http://fake-bank.com"],
    "emails": ["noreply@phishing.com"],
    "ips": [],
    "suspicious_phrases": 2
  },
  "analysis_id": "analysis_20251115_103045_123456",
  "timestamp": "2025-11-15T10:30:45"
}
```

### Get History
```bash
GET http://localhost:5000/api/v1/history?limit=50&risk_level=DANGEROUS

Response:
{
  "total_count": 150,
  "filtered_count": 25,
  "analyses": [...]
}
```

### Get Statistics
```bash
GET http://localhost:5000/api/v1/statistics

Response:
{
  "total_analyses": 150,
  "safe_count": 50,
  "suspicious_count": 75,
  "dangerous_count": 25,
  "safe_percentage": 33.33,
  "dangerous_percentage": 16.67,
  "average_risk_score": 0.45
}
```

### Get Threats
```bash
GET http://localhost:5000/api/v1/threats?limit=20

Response:
{
  "total_threats": 45,
  "critical_threats": 12,
  "threats": [...]
}
```

**See [API_GUIDE.md](API_GUIDE.md) for complete documentation!**

---

## 💻 Code Files

### 1. `CyberGuard_API.py` (600 lines)
Flask REST API server with:
- Email analysis engine
- Pattern & keyword detection
- ML model training and prediction
- JSON database management
- 7 API endpoints
- CORS support

### 2. `CyberGuard_Desktop_API.py` (700 lines)
Tkinter desktop GUI with:
- Multi-tab interface (Analyzer, History, Stats, About)
- Real-time email analysis
- API integration
- Copy/paste functionality
- File loading support
- Theme toggle & language support

### 3. `CyberGuard_API_Client.py` (300 lines)
API test client with:
- 9 comprehensive tests
- Example usage patterns
- Error handling
- Pretty JSON output

### 4. Launcher Scripts
- `START_MUNICIPAL.ps1` - PowerShell launcher
- `START_MUNICIPAL.bat` - Batch file launcher

---

## 🗄️ Database

### File Location
```
C:\Users\User\Desktop\cyberguard_api_db.json
```

### Structure
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
      "patterns_found": { ... },
      "analysis_id": "analysis_20251115_103045_123456",
      "subject": "Subject",
      "email_length": 250,
      "timestamp": "2025-11-15T10:30:45"
    }
  ],
  "threats": [
    {
      "threat_id": "analysis_20251115_103045_123456",
      "subject": "Subject",
      "risk_level": "DANGEROUS",
      "risk_score": 0.75,
      "timestamp": "2025-11-15T10:30:45",
      "keywords": ["verify", "urgent"]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### API Server Won't Start
```powershell
# Check if port 5000 is in use
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

# Kill process on port 5000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force

# Try a different port - edit CyberGuard_API.py line: API_PORT = 5001
```

### Desktop App Can't Connect
1. Ensure API server is running
2. Check `http://localhost:5000/api/v1/health`
3. Verify Windows Firewall isn't blocking port 5000
4. Check console for error messages

### Import Errors
```powershell
pip install --upgrade flask flask-cors scikit-learn numpy requests
```

### Permission Denied
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Unicode Errors (Greek Characters)
Add to PowerShell:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| API Response Time | 50-100ms |
| Desktop GUI Response | 200-300ms |
| ML Model Inference | 10-20ms |
| Database Size (1000 analyses) | ~2MB |
| Memory Usage (API) | 100-150MB |
| Memory Usage (ML Model) | 50MB |

---

## 🔒 Security Notes

⚠️ **For Production Deployment:**

1. **Authentication**
   - Add API key/token validation
   - Implement JWT tokens
   - Use OAuth2 for user accounts

2. **HTTPS/TLS**
   - Use SSL certificates
   - Run behind nginx/Apache proxy
   - Implement certificate pinning

3. **Rate Limiting**
   - Prevent API abuse
   - Implement request throttling
   - Track usage per client

4. **Database Security**
   - Encrypt sensitive data
   - Use SQLite/PostgreSQL instead of JSON
   - Implement access controls
   - Regular backups

5. **Logging & Monitoring**
   - Comprehensive audit logs
   - Performance monitoring
   - Alert on suspicious patterns
   - Regular security audits

---

## 🚀 Future Enhancements

- [ ] IMAP/SMTP email server integration
- [ ] SQLite/PostgreSQL database migration
- [ ] Web dashboard (Flask templates)
- [ ] User authentication & role-based access
- [ ] Webhook notifications
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Machine learning model updates via API
- [ ] Advanced statistics & reporting
- [ ] Email attachment scanning

---

## 🏛️ About

**CyberGuard v2.1 - API Integrated Edition**
- **Purpose**: Phishing email detection for Athens Municipality
- **Hackathon**: City Challenge Crowdhackathon 2025
- **Organization**: Δήμος Αθηναίων (Athens Municipality)
- **License**: MIT Open Source
- **Technology Stack**: 
  - Python 3.13
  - Tkinter (GUI)
  - Flask (REST API)
  - scikit-learn (ML)
  - NumPy (Numeric)
  - Requests (HTTP)

**Features:**
- ✅ Multi-level detection (Keyword + Pattern + ML)
- ✅ REST API backend
- ✅ Modern desktop GUI
- ✅ Real-time analysis
- ✅ Greek language support
- ✅ No cloud dependencies
- ✅ Local data storage
- ✅ Extensible architecture

---

## 📞 Support

For issues or questions:
1. Check the console output
2. Review [API_GUIDE.md](API_GUIDE.md) for detailed API documentation
3. Test manually with `http://localhost:5000/api/v1/health`
4. Check database file: `cyberguard_api_db.json`
5. Enable debug logging in Flask (`debug=True` in app.run)

---

## 📄 License

MIT License - Open Source
Feel free to modify and distribute!

---

---

# CyberGuard v2.1 - Σύστημα Ανίχνευσης Phishing Emails

## 🇬🇷 Ελληνική Έκδοση

### Γρήγορη Έναρξη

**Εκκίνηση Αυτόματη (Προτείνεται):**
```batch
C:\Users\User\Desktop\START_MUNICIPAL.bat
```

**Ή με PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\START_MUNICIPAL.ps1"
```

### Απαιτήσεις

- Python 3.13+
- Windows 7/10/11

### Εγκατάσταση

```powershell
pip install flask flask-cors scikit-learn numpy requests
```

### Δομή Εφαρμογής

**Αρχικοί Σερβερ:**
1. **API Server** (CyberGuard_API.py) - Port 5000
2. **Desktop GUI** (CyberGuard_Desktop_API.py) - Tkinter

**Βάση Δεδομένων:**
- JSON αρχείο: `cyberguard_api_db.json`
- Αποθήκευση ιστορικού αναλύσεων
- Ηλεκτρονικές απειλές

### Μέθοδοι Ανίχνευσης

1. **Ανίχνευση Λέξεων Κλειδιών** (30%)
   - 60+ ύποπτες λέξεις
   - Αγγλικά & Ελληνικά
   - Παραδείγματα: "επιβεβαίωση", "επείγουσα", "κλικ εδώ"

2. **Ανίχνευση Μοτίβων** (35%)
   - URLs, IP addresses, emails
   - Ύποπτες φράσεις
   - Bonus για πολλά μοτίβα

3. **Μηχανική Μάθηση** (35%)
   - Logistic Regression classifier
   - 8 δεδομένα εκπαίδευσης
   - Real-time βαθμολόγηση

### Κατηγοριοποίηση Κινδύνου

- **🟢 ΑΣΦΑΛΗΣ**: Σκορ < 0.25
- **🟡 ΎΠΟΠΤΗ**: Σκορ 0.25-0.55
- **🔴 ΕΠΙΚΙΝΔΥΝΗ**: Σκορ > 0.55

### Χαρακτηριστικά

- ✅ Ανάλυση σε πραγματικό χρόνο
- ✅ Αντιγραφή/Επικόλληση από εξωτερικές εφαρμογές
- ✅ Φόρτωση αρχείων (PDF, DOCX, TXT, HTML)
- ✅ Ιστορικό αναλύσεων
- ✅ Στατιστικά & μετρικές
- ✅ Υποστήριξη Ελληνικών
- ✅ Σκούρο/Ανοιχτό θέμα
- ✅ Χωρίς cloud ή διαδίκτυο

### API Endpoints

| Μέθοδος | Endpoint | Περιγραφή |
|---------|----------|-----------|
| GET | `/api/v1/health` | Έλεγχος υγείας API |
| POST | `/api/v1/analyze` | Ανάλυση email |
| GET | `/api/v1/history` | Ιστορικό αναλύσεων |
| GET | `/api/v1/threats` | Ανιχνευμένες απειλές |
| GET | `/api/v1/statistics` | Στατιστικά |
| GET | `/api/v1/info` | Πληροφορίες API |
| POST | `/api/v1/clear` | Καθαρισμός DB |

### Πληροφορίες

- **Σκοπός**: Ανίχνευση phishing emails για Δήμο Αθηναίων
- **Hackathon**: City Challenge Crowdhackathon 2025
- **Άδεια**: MIT Open Source

**Για περισσότερες λεπτομέρειες, δείτε [API_GUIDE.md](API_GUIDE.md)**

---

**Version 2.1** | November 2025
