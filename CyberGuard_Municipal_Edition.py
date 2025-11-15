"""
CyberGuard - Municipal Edition για Δήμο Αθηναίων
Απλοποιημένη έκδοση με ενοποίηση της δημοτικής βάσης δεδομένων
Phishing email detection για δημόσια διοίκηση
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
from tkinter import font as tkFont
import json
import os
import re
from datetime import datetime
import requests
from threading import Thread
import time
import unicodedata

# Import municipal database module
try:
    from municipal_database import MunicipalDatabase, municipal_based_detection
    MUNICIPAL_DB_AVAILABLE = True
except ImportError:
    MUNICIPAL_DB_AVAILABLE = False
    print("⚠️  Municipal database module not found")

# Only using local municipal database
ATHENS_DIGITAL_LAB_AVAILABLE = False

# API Configuration
API_BASE_URL = "http://localhost:5000"
API_TIMEOUT = 5
API_RETRIES = 3
API_RETRY_DELAY = 1

def api_request_with_retry(method, endpoint, **kwargs):
    """Make API request with retry logic"""
    url = f"{API_BASE_URL}{endpoint}"
    kwargs.pop('timeout', None)
    
    for attempt in range(API_RETRIES):
        try:
            if method == 'GET':
                response = requests.get(url, timeout=API_TIMEOUT, **kwargs)
            elif method == 'POST':
                response = requests.post(url, timeout=API_TIMEOUT, **kwargs)
            else:
                return None, f"Invalid HTTP method: {method}"
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"API Error {response.status_code}"
        
        except requests.exceptions.Timeout:
            if attempt < API_RETRIES - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return None, "Timeout"
        
        except requests.exceptions.ConnectionError:
            if attempt < API_RETRIES - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return None, "Connection Error"
        
        except Exception as e:
            return None, str(e)
    
    return None, "Max retries exceeded"

class CyberGuardMunicipal(tk.Tk):
    def __init__(self, root=None):
        super().__init__(root)
        
        self.title("🛡️ CyberGuard - Δήμος Αθηναίων")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # App state
        self.language = "el"  # Ελληνικά από default
        self.api_connected = False
        self.current_analysis = None
        
        # Municipal database
        self.db = None
        if MUNICIPAL_DB_AVAILABLE:
            try:
                self.db = MunicipalDatabase()
                print(f"✅ Municipal database loaded: {len(self.db.employees)} employees")
            except Exception as e:
                print(f"⚠️  Could not load municipal database: {e}")
        
        # Using local municipal database only
        
        # Demo emails
        self.demo_emails = {
            'safe': {
                'subject': 'Ανανέωση Άδειας Κατοικίας - Δήμος Αθηναίων',
                'body': """Αγαπητέ πολίτη,

Σας ενημερώνουμε ότι η άδειά σας κατοικίας έχει ανανεωθεί.
Αριθμός Αίτησης: DAA-2025-001234

Για περισσότερες πληροφορίες επισκεφθείτε το δημοτικό κατάστημα ή
επικοινωνήστε με το 210-1234567

Φιλικά,
Δήμος Αθηναίων
Τμήμα Διοικητικών Υπηρεσιών"""
            },
            'suspicious': {
                'subject': 'ΣΗΜΑΝΤΙΚΟ: Ενημέρωση Δημοτικής Χρέωσης',
                'body': """Κύριε/κυρία,

ΕΚΤΑΚΤΟ! Η δημοτική σας χρέωση έχει ανέβει κατακόρυφα!
Πρέπει να ανανεώσετε τα στοιχεία σας ΑΜΕΣΩΣ

Κάντε κλικ εδώ: http://192.168.1.1/dimos-update/

Ή καλέστε τώρα: 0800-111-1111 (χρέωση αναμετάδοσης)

Δεν πρέπει να χάσετε χρόνο!
Administrator
"""
            },
            'dangerous': {
                'subject': 'ΚΡΙΣΙΜΗ ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Ο λογαριασμός σας έχει αναστείλει!',
                'body': """ΠΡΟΣΟΧΗ!!!

Το λογαριασμό δημοτικών υπηρεσιών σας έχει αναστείλει λόγω ύποπτης δραστηριότητας!

Επιβεβαιώστε τα στοιχεία σας ΤΩΡΑ:
http://10.0.0.1/verify-account/login.php

Εισάγετε:
- ΑΦΜ
- Κωδικό πρόσβασης
- Στοιχεία κάρτας

Αν δεν ενεργήσετε σε 24 ώρες, το λογαριασμό σας θα διαγραφεί!

Δήμος Αθηναίων - Security Team
noreply@dimos-athens-security.local
"""
            }
        }
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        self.check_api_connection()
    
    def setup_styles(self):
        """Setup colors and fonts"""
        self.bg_color = '#1a1a2e'
        self.fg_color = '#e0e0e0'
        self.accent_blue = '#0066cc'
        self.accent_green = '#00cc00'
        self.accent_red = '#ff3333'
        self.accent_yellow = '#ffaa00'
        
        self.configure(bg=self.bg_color)
        
        # Large fonts for accessibility
        self.font_title = ('Arial', 18, 'bold')
        self.font_large_button = ('Arial', 14, 'bold')
        self.font_normal = ('Arial', 11)
        self.font_small = ('Arial', 10)
    
    def setup_ui(self):
        """Setup simplified user interface"""
        # Header with logo
        header = tk.Frame(self, bg='#004499', height=80)
        header.pack(fill=tk.X)
        
        logo_frame = tk.Frame(header, bg='#004499')
        logo_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        title = tk.Label(
            logo_frame,
            text="🛡️ CyberGuard",
            font=('Arial', 24, 'bold'),
            bg='#004499',
            fg='white'
        )
        title.pack()
        
        subtitle = tk.Label(
            logo_frame,
            text="Προστασία από Απατηλά Emails - Δήμος Αθηναίων",
            font=('Arial', 12),
            bg='#004499',
            fg='#ccddff'
        )
        subtitle.pack()
        
        # API Status
        self.api_status = tk.Label(
            header,
            text="🔴 Σύνδεση...",
            font=('Arial', 11, 'bold'),
            bg='#004499',
            fg='#ffcccc'
        )
        self.api_status.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Database Status
        db_status_text = "✅ ΒΔ Δήμου" if self.db else "⚠️  ΒΔ Offline"
        db_color = '#ccffcc' if self.db else '#ffcccc'
        self.db_status = tk.Label(
            header,
            text=db_status_text,
            font=('Arial', 11, 'bold'),
            bg='#004499',
            fg=db_color
        )
        self.db_status.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Main content area
        content = tk.Frame(self, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Top panel: Quick demo buttons
        demo_frame = tk.LabelFrame(
            content,
            text="📧 ΔΟΚΙΜΑΣΤΙΚΑ EMAILS (Κάντε κλικ για παράδειγμα)",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.accent_blue,
            padx=10,
            pady=10
        )
        demo_frame.pack(fill=tk.X, pady=10)
        
        # Demo buttons
        self.btn_safe = tk.Button(
            demo_frame,
            text="✅ ΑΣΦΑΛΗΣ EMAIL\n(Νόμιμο)",
            command=lambda: self.load_demo('safe'),
            font=self.font_large_button,
            bg='#00aa00',
            fg='white',
            height=3,
            width=20,
            relief=tk.RAISED,
            bd=3
        )
        self.btn_safe.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_suspicious = tk.Button(
            demo_frame,
            text="⚠️  ΎΠΟΠΤΟ EMAIL\n(Προσοχή)",
            command=lambda: self.load_demo('suspicious'),
            font=self.font_large_button,
            bg=self.accent_yellow,
            fg='black',
            height=3,
            width=20,
            relief=tk.RAISED,
            bd=3
        )
        self.btn_suspicious.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_dangerous = tk.Button(
            demo_frame,
            text="🚨 ΕΠΙΚΙΝΔΥΝΟ EMAIL\n(Απάτη)",
            command=lambda: self.load_demo('dangerous'),
            font=self.font_large_button,
            bg='#ff3333',
            fg='white',
            height=3,
            width=20,
            relief=tk.RAISED,
            bd=3
        )
        self.btn_dangerous.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Main work area
        work_frame = tk.Frame(content, bg=self.bg_color)
        work_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left panel: Email input
        left_panel = tk.LabelFrame(
            work_frame,
            text="📝 ΕΙΣΑΓΩΓΗ EMAIL",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.accent_blue,
            padx=10,
            pady=10
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.email_input = scrolledtext.ScrolledText(
            left_panel,
            height=20,
            wrap=tk.WORD,
            bg='#2d2d2d',
            fg=self.fg_color,
            font=('Courier', 11),
            insertbackground='#00ff00'
        )
        self.email_input.pack(fill=tk.BOTH, expand=True)
        # Keyboard bindings
        self.email_input.bind('<Control-c>', self.on_copy_email)
        self.email_input.bind('<Control-v>', self.on_paste_email)
        self.email_input.bind('<Control-x>', self.on_cut_email)
        self.email_input.bind('<Control-a>', self.on_select_all_email)
        # Right-click menu
        self.email_input.bind('<Button-3>', self.show_context_menu_email)
        
        # Instructions
        instr = tk.Label(
            left_panel,
            text="💡 Επικολλήστε ή γράψτε email | Ctrl+V για επικόλληση",
            font=self.font_small,
            bg=self.bg_color,
            fg='#aaaaaa'
        )
        instr.pack(fill=tk.X, pady=(5, 0))
        
        # Right panel: Results
        right_panel = tk.LabelFrame(
            work_frame,
            text="📊 ΑΠΟΤΕΛΕΣΜΑΤΑ ΑΝΑΛΥΣΗΣ",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.accent_blue,
            padx=10,
            pady=10
        )
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Large risk display
        self.risk_label = tk.Label(
            right_panel,
            text="—",
            font=('Arial', 32, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.risk_label.pack(pady=10)
        
        self.risk_text = tk.Label(
            right_panel,
            text="Αναμονή...",
            font=('Arial', 14),
            bg=self.bg_color,
            fg='#ffaa00'
        )
        self.risk_text.pack(pady=5)
        
        # Details
        self.details_text = scrolledtext.ScrolledText(
            right_panel,
            height=16,
            wrap=tk.WORD,
            bg='#2d2d2d',
            fg=self.fg_color,
            font=('Courier', 10),
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.details_text.bind('<Control-c>', self.on_copy_results)
        self.details_text.bind('<Control-v>', self.on_paste_results)
        self.details_text.bind('<Control-x>', self.on_cut_results)
        self.details_text.bind('<Control-a>', self.on_select_all_results)
        self.details_text.bind('<Button-3>', self.show_context_menu_results)
        
        # Bottom action buttons
        button_frame = tk.Frame(content, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        btn_analyze = tk.Button(
            button_frame,
            text="🔍 ΑΝΑΛΥΣΗ ΤΩΡΑ",
            command=self.on_analyze,
            font=self.font_large_button,
            bg=self.accent_blue,
            fg='white',
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        btn_analyze.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(
            button_frame,
            text="🗑️ ΚΑΘΑΡΙΣΜΟΣ",
            command=self.on_clear,
            font=self.font_large_button,
            bg='#666666',
            fg='white',
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_load = tk.Button(
            button_frame,
            text="📂 ΦΟΡΤΩΣΗ ΑΡΧΕΙΟΥ",
            command=self.load_file,
            font=self.font_large_button,
            bg=self.accent_blue,
            fg='white',
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        btn_load.pack(side=tk.LEFT, padx=5)
        
        btn_history = tk.Button(
            button_frame,
            text="📋 ΙΣΤΟΡΙΚΟ",
            command=self.show_history,
            font=self.font_large_button,
            bg='#0088cc',
            fg='white',
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        btn_history.pack(side=tk.LEFT, padx=5)
        
        btn_info = tk.Button(
            button_frame,
            text="ℹ️  ΠΛΗΡΟΦΟΡΙΕΣ",
            command=self.show_info,
            font=self.font_large_button,
            bg='#666666',
            fg='white',
            padx=30,
            pady=15,
            relief=tk.RAISED,
            bd=3
        )
        btn_info.pack(side=tk.LEFT, padx=5)
    
    def check_api_connection(self):
        """Check API in background"""
        def check():
            for attempt in range(3):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
                    if response.status_code == 200:
                        self.api_connected = True
                        self.api_status.config(text="🟢 Σύστημα Έτοιμο", fg='#00ff00')
                        return
                except:
                    if attempt < 2:
                        time.sleep(1)
            
            self.api_connected = False
            self.api_status.config(text="🔴 Σύνδεση Απαιτείται", fg='#ff6666')
        
        Thread(target=check, daemon=True).start()

    def normalize_email_text(self, text: str) -> str:
        """Normalize email text for consistent analysis while preserving capitalization.

        - Unicode normalization (NFKC)
        - Remove zero-width / BOM characters
        - Collapse multiple spaces/tabs to single space
        - Normalize line endings and remove excessive blank lines
        """
        if not text:
            return ''
        txt = unicodedata.normalize('NFKC', text)
        # Remove zero-width and BOM
        txt = txt.replace('\u200b', '').replace('\u200c', '').replace('\ufeff', '')
        # Normalize CRLF to LF
        txt = re.sub(r'\r\n?', '\n', txt)
        # Collapse repeated whitespace but keep newlines
        txt = re.sub(r'[ \t]+', ' ', txt)
        # Collapse multiple blank lines
        txt = re.sub(r'\n\s*\n+', '\n\n', txt)
        return txt.strip()
    

    
    def load_demo(self, demo_type):
        """Load demo email"""
        email = self.demo_emails[demo_type]
        self.email_input.delete("1.0", tk.END)
        self.email_input.insert(tk.END, f"Subject: {email['subject']}\n\n{email['body']}")
        self.on_analyze()
    
    def on_analyze(self):
        """Analyze email"""
        raw_text = self.email_input.get("1.0", tk.END)
        email_text = self.normalize_email_text(raw_text)
        
        if not email_text or len(email_text) < 10:
            self.show_result("—", "Παρακαλώ εισάγετε email", '#ffaa00')
            return
        
        self.risk_text.config(text="⏳ Ανάλυση σε εξέλιξη...")
        self.update_idletasks()
        
        if not self.api_connected:
            self.show_result("⚠️", "Σύστημα offline", '#ff8800')
            return
        
        def analyze():
            try:
                data, error = api_request_with_retry(
                    'POST',
                    '/api/v1/analyze',
                    json={'email_text': email_text, 'subject': 'Analysis'},
                    timeout=API_TIMEOUT
                )
                
                if data:
                    self.current_analysis = data
                    self.display_analysis(data)
                else:
                    self.show_result("⚠️", f"Σφάλμα: {error}", '#ff6666')
            except Exception as e:
                self.show_result("⚠️", f"Σφάλμα: {str(e)}", '#ff6666')
        
        Thread(target=analyze, daemon=True).start()
    
    def display_analysis(self, analysis):
        """Display analysis results with municipal database verification"""
        risk_level = analysis.get('risk_level', 'UNKNOWN')
        risk_score = analysis.get('risk_score', 0)
        
        # Emoji and color mapping
        level_map = {
            'SAFE': ('✅ ΑΣΦΑΛΗΣ', '#00cc00', '0 - 30% Κίνδυνος'),
            'SUSPICIOUS': ('⚠️ ΎΠΟΠΤΟ', '#ffaa00', '30 - 70% Κίνδυνος'),
            'DANGEROUS': ('🚨 ΕΠΙΚΙΝΔΥΝΟ', '#ff3333', '70 - 100% Κίνδυνος')
        }
        
        emoji, color, desc = level_map.get(risk_level, ('—', '#cccccc', 'Άγνωστο'))
        
        self.show_result(emoji, desc, color)
        
        # Get capitalization issues
        caps_issues = analysis.get('patterns_found', {}).get('capitalization_issues', [])
        caps_score = analysis.get('caps_score', 0)
        
        # Display details
        details = f"""
ΑΠΟΤΕΛΕΣΜΑΤΑ ΑΝΙΧΝΕΥΣΗΣ
{'=' * 45}

Επίπεδο Κινδύνου: {risk_level}
Βαθμός Κινδύνου: {risk_score:.1%}

ΣΥΝΘΕΤΙΚΟΙ ΠΑΡΑΓΟΝΤΕΣ:
  • Λέξεις-κλειδιά: {analysis.get('keyword_score', 0):.1%}
  • Μοτίβα: {analysis.get('pattern_score', 0):.1%}
  • ΚΕΦΑΛΑΙΑ: {caps_score:.1%}
  • Μηχανική Μάθηση: {analysis.get('ml_score', 0):.1%}

"""
        
        # Add municipal database verification (local only)
        if self.db:
            # Extract sender email from the original input (robust email regex)
            content = self.email_input.get("1.0", tk.END)
            email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            sender_matches = re.findall(email_regex, content, re.IGNORECASE)

            sender = sender_matches[-1] if sender_matches else None
            if sender:
                details += f"""
📧 ΕΠΑΛΗΘΕΥΣΗ ΔΗΜΟΤΙΚΗΣ ΒΑΣΗΣ:
  Αποστολέας: {sender}
"""
                emp = self.db.verify_employee_email(sender)
                if emp:
                    details += f"  ✅ ΕΠΑΛΗΘΕΥΜΕΝΟΣ: {emp.get('name', 'Unknown')}\n"
                    if emp.get('position'):
                        details += f"     Θέση: {emp.get('position')}\n"
                else:
                    details += f"  ❌ ΔΕΝ ΒΡΕΘΗΚΕ στη τοπική βάση\n"

                # Check domain (case-insensitive)
                if self.db.verify_email_domain(sender):
                    details += f"  ✅ Γνήσιο domain Δήμου\n"
                else:
                    details += f"  ⚠️  ΑΓΝΩΣΤΟ domain (ΟΧΙ Δήμος)\n"

                # Check verified sender
                if self.db.is_verified_sender(sender):
                    details += f"  ✅ Επιβεβαιωμένος αποστολέας\n"

                details += "\n"
        
        # Add capitalization issues if found
        if caps_issues:
            details += "🚨 ΠΡΟΕΙΔΟΠΟΙΗΣΕΙΣ ΚΕΦΑΛΑΙΩΝ:\n"
            for issue in caps_issues:
                details += f"  ⚠️  {issue}\n"
            details += "\n"
        
        details += f"""ΑΠΕΙΛΕΣ ΕΝΤΟΠΙΣΤΗΣΑΝ:
  • Ύποπτες Λέξεις: {len(analysis.get('keywords_found', []))}
  • Links/URLs: {len(analysis.get('patterns_found', {}).get('urls', []))}
  • Email Addresses: {len(analysis.get('patterns_found', {}).get('emails', []))}
  • IP Addresses: {len(analysis.get('patterns_found', {}).get('ips', []))}

{'=' * 45}
ΤΙ ΝΑ ΚΑΝΕΤΕ:

Αν είναι ΑΣΦΑΛΗΣ: ✅
  → Μπορείτε να ανοίξετε το σύνδεσμο με ασφάλεια
  → Δεν υπάρχει κίνδυνος

Αν είναι ΎΠΟΠΤΟ: ⚠️
  → Πάρτε πληροφορίες στις αρχές
  → Μην κάνετε κλικ σε σύνδεσμους
  → Μην δώσετε προσωπικά στοιχεία

Αν είναι ΕΠΙΚΙΝΔΥΝΟ: 🚨
  → ΣΤΑΜΑΤΗΣΤΕ - ΜΗΝ ανοίξετε links
  → Μην ανταποκριθείτε στο email
  → Αναφέρετε στον IT διαχειριστή
  → Διαγράψτε το email
"""
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def show_result(self, emoji, text, color):
        """Show result on risk label"""
        self.risk_label.config(text=emoji, fg=color)
        self.risk_text.config(text=text, fg=color)
    
    def on_clear(self):
        """Clear all"""
        self.email_input.delete("1.0", tk.END)
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)
        self.show_result("—", "Αναμονή...", '#ffaa00')
    
    def load_file(self):
        """Load file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt *.eml"), ("All", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.email_input.delete("1.0", tk.END)
                self.email_input.insert(tk.END, content)
                self.on_analyze()
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η φόρτωση: {e}")
    
    def show_history(self):
        """Show analysis history"""
        if not self.api_connected:
            messagebox.showerror("Σφάλμα", "Σύστημα απενεργοποιημένο")
            return
        
        def fetch():
            data, error = api_request_with_retry('GET', '/api/v1/history?limit=20')
            if data:
                total = data.get('total_count', 0)
                analyses = data.get('analyses', [])
                
                history_text = f"ΣΥΝΟΛΟ ΑΝΑΛΥΣΕΩΝ: {total}\n\n"
                for a in analyses[:10]:
                    history_text += f"""
{a.get('risk_level')} - {a.get('risk_score'):.0%} κίνδυνος
Ώρα: {a.get('timestamp', '—')}
Λέξεις: {', '.join(a.get('keywords_found', [])[:3])}
{'-' * 40}
"""
                
                msgbox = tk.Toplevel(self)
                msgbox.title("Ιστορικό Αναλύσεων")
                msgbox.geometry("600x400")
                
                text = scrolledtext.ScrolledText(msgbox, wrap=tk.WORD)
                text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text.insert(tk.END, history_text)
                # Bind clipboard shortcuts for history viewer
                text.bind('<Control-c>', lambda e, w=text: self.copy_text(w))
                text.bind('<Control-v>', lambda e: 'break')
                text.bind('<Control-x>', lambda e: 'break')
                text.bind('<Control-a>', lambda e, w=text: self.select_all_text(w))
                # Right-click context menu for history
                def show_history_menu(event, widget=text):
                    menu = tk.Menu(self, tearoff=0, bg='#2d2d2d', fg=self.fg_color)
                    menu.add_command(label="📋 Αντιγραφή (Ctrl+C)", command=lambda: self.copy_text(widget))
                    menu.add_separator()
                    menu.add_command(label="🔤 Επιλογή Όλων", command=lambda: self.select_all_text(widget))
                    menu.post(event.x_root, event.y_root)

                text.bind('<Button-3>', show_history_menu)
                text.config(state=tk.DISABLED)
        
        Thread(target=fetch, daemon=True).start()
    
    def show_info(self):
        """Show information dialog"""
        info_text = """
🛡️ CYBERGUARD - Δήμος Αθηναίων Edition

ΣΚΟΠΟΣ:
Προστασία των δημοτικών υπαλλήλων και πολιτών
από απατηλά emails (phishing)

ΠΩΣ ΔΟΥΛΕΥΕΙ:
1. Αντιγράψτε ένα email ή φορτώστε αρχείο
2. Πατήστε "ΑΝΑΛΥΣΗ ΤΩΡΑ"
3. Δείτε τα αποτελέσματα

ΣΗΜΑΙΑ ΚΙΝΔΥΝΟΥ:
✅ ΑΣΦΑΛΗΣ (0-30%)
   → Νόμιμο email, ασφαλές

⚠️ ΎΠΟΠΤΟ (30-70%)
   → Προσοχή, μην κάνετε κλικ

🚨 ΕΠΙΚΙΝΔΥΝΟ (70-100%)
   → Απάτη! Διαγράψτε αμέσως

ΤΙΠΟΤΑ ΔΕΣΜΕΥΤΙΚΟ ΧΡΕΩΘΗΚΕ:
✓ Δεν στέλνει δεδομένα έξω
✓ Τοπική επεξεργασία μόνο
✓ Κανένα πρόβλημα ασφάλειας

ΥΠΟΣΤΗΡΙΞΗ:
Δήμος Αθηναίων - IT Department
210-1234567

Version: 2.2 Municipal Edition
November 2025
"""
        
        msgbox = tk.Toplevel(self)
        msgbox.title("Πληροφορίες")
        msgbox.geometry("600x500")
        msgbox.configure(bg='#1a1a2e')
        
        text = scrolledtext.ScrolledText(
            msgbox,
            wrap=tk.WORD,
            bg='#2d2d2d',
            fg='#e0e0e0',
            font=('Arial', 11)
        )
        text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        text.insert(tk.END, info_text)
        text.config(state=tk.DISABLED)
    
    def on_copy_email(self, event=None):
        """Copy from email input"""
        try:
            text = self.email_input.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            return 'break'
        except:
            pass
    
    def on_paste_email(self, event=None):
        """Paste to email input and analyze"""
        try:
            text = self.clipboard_get()
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, text)
            self.on_analyze()
            return 'break'
        except Exception as e:
            messagebox.showerror("Σφάλμα", "Δεν ήταν δυνατή η επικόλληση")
            return 'break'
    
    def on_select_all_email(self, event=None):
        """Select all in email input"""
        try:
            self.email_input.tag_add(tk.SEL, "1.0", tk.END)
            self.email_input.mark_set(tk.INSERT, "1.0")
            self.email_input.see(tk.INSERT)
            return 'break'
        except:
            pass
    
    def on_cut_email(self, event=None):
        """Cut from email input"""
        try:
            text = self.email_input.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            self.email_input.delete(tk.SEL_FIRST, tk.SEL_LAST)
            return 'break'
        except:
            pass
    
    def on_copy_results(self, event=None):
        """Copy from results"""
        try:
            text = self.details_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            return 'break'
        except:
            pass

    def on_paste_results(self, event=None):
        """Paste into results area (redirect to email input)"""
        try:
            text = self.clipboard_get()
            # Paste into email input for safety/analysis
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, text)
            self.on_analyze()
            return 'break'
        except:
            return 'break'

    def on_cut_results(self, event=None):
        """Cut from results (copy selection to clipboard)"""
        try:
            text = self.details_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            # Do not allow editing of results area; no deletion
            return 'break'
        except:
            pass

    def on_select_all_results(self, event=None):
        """Select all in results"""
        try:
            self.details_text.tag_add(tk.SEL, "1.0", tk.END)
            self.details_text.mark_set(tk.INSERT, "1.0")
            self.details_text.see(tk.INSERT)
            return 'break'
        except:
            pass
    
    def show_context_menu_email(self, event):
        """Right-click menu for email input"""
        menu = tk.Menu(self, tearoff=0, bg='#2d2d2d', fg=self.fg_color)
        menu.add_command(label="✂️  Κόψιμο (Ctrl+X)", command=lambda: self.cut_text(self.email_input))
        menu.add_command(label="📋 Αντιγραφή (Ctrl+C)", command=lambda: self.copy_text(self.email_input))
        menu.add_command(label="📌 Επικόλληση (Ctrl+V)", command=lambda: self.paste_text())
        menu.add_separator()
        menu.add_command(label="🔤 Επιλογή Όλων", command=lambda: self.select_all_text(self.email_input))
        menu.add_command(label="🗑️ Διαγραφή", command=lambda: self.delete_all(self.email_input))
        
        menu.post(event.x_root, event.y_root)
    
    def show_context_menu_results(self, event):
        """Right-click menu for results"""
        menu = tk.Menu(self, tearoff=0, bg='#2d2d2d', fg=self.fg_color)
        menu.add_command(label="📋 Αντιγραφή (Ctrl+C)", command=lambda: self.copy_text(self.details_text))
        menu.add_command(label="📌 Επικόλληση στο Email (Ctrl+V)", command=lambda: self.paste_to_email())
        menu.add_separator()
        menu.add_command(label="🔤 Επιλογή Όλων", command=lambda: self.select_all_text(self.details_text))
        
        menu.post(event.x_root, event.y_root)
    
    def copy_text(self, widget):
        """Copy text from widget"""
        try:
            text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
        except:
            pass
    
    def paste_text(self):
        """Paste to email input"""
        try:
            text = self.clipboard_get()
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, text)
            self.on_analyze()
        except:
            messagebox.showerror("Σφάλμα", "Δεν ήταν δυνατή η επικόλληση")
    
    def paste_to_email(self):
        """Paste results to email"""
        try:
            text = self.clipboard_get()
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, text)
            self.on_analyze()
        except:
            pass
    
    def cut_text(self, widget):
        """Cut text from widget"""
        try:
            text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            if widget == self.email_input:
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def select_all_text(self, widget):
        """Select all text in widget"""
        try:
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        except:
            pass
    
    def delete_all(self, widget):
        """Delete all text in widget"""
        try:
            if widget == self.email_input:
                widget.delete("1.0", tk.END)
        except:
            pass

if __name__ == '__main__':
    app = CyberGuardMunicipal()
    app.mainloop()
