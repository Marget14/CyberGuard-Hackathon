"""
CyberGuard Desktop Application - API Integrated Version
Modern phishing email detection with API backend
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

# API Configuration
API_BASE_URL = "http://localhost:5000"
API_ENABLED = True
API_TIMEOUT = 5
API_RETRIES = 3
API_RETRY_DELAY = 1  # seconds

# ==================== API Helper Functions ====================

def api_request_with_retry(method, endpoint, **kwargs):
    """Make API request with retry logic"""
    url = f"{API_BASE_URL}{endpoint}"
    
    # Remove timeout from kwargs if present to avoid duplicate parameter
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
                return None, f"API Error {response.status_code}: {response.text}"
        
        except requests.exceptions.Timeout:
            error_msg = f"Timeout (attempt {attempt + 1}/{API_RETRIES})"
            if attempt < API_RETRIES - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return None, error_msg
        
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection Error (attempt {attempt + 1}/{API_RETRIES})"
            if attempt < API_RETRIES - 1:
                time.sleep(API_RETRY_DELAY)
                continue
            return None, error_msg
        
        except Exception as e:
            return None, str(e)
    
    return None, "Max retries exceeded"

class CyberGuardDesktop(tk.Tk):
    def __init__(self, root=None):
        super().__init__(root)
        
        self.title("CyberGuard - Phishing Email Detection")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # App state
        self.current_email = ""
        self.current_analysis = None
        self.dark_mode = True
        self.language = "en"
        self.api_connected = False
        
        # Languages
        self.texts = {
            'en': {
                'title': 'CyberGuard - Phishing Email Detection',
                'analyze': 'Analyze',
                'clear': 'Clear',
                'load_file': 'Load File',
                'save_history': 'Save History',
                'copy': 'Copy',
                'paste': 'Paste',
                'cut': 'Cut',
                'select_all': 'Select All',
                'risk_level': 'Risk Level',
                'risk_score': 'Risk Score',
                'status': 'Status',
                'safe': 'SAFE',
                'suspicious': 'SUSPICIOUS',
                'dangerous': 'DANGEROUS',
                'api_connected': 'API Connected',
                'api_disconnected': 'API Disconnected',
                'history': 'History',
                'statistics': 'Statistics',
                'about': 'About',
            },
            'el': {
                'title': 'CyberGuard - Ανίχνευση Φishing Emails',
                'analyze': 'Ανάλυση',
                'clear': 'Καθαρισμός',
                'load_file': 'Φόρτωση Αρχείου',
                'save_history': 'Αποθήκευση Ιστορικού',
                'copy': 'Αντιγραφή',
                'paste': 'Επικόλληση',
                'cut': 'Αποκοπή',
                'select_all': 'Επιλογή Όλων',
                'risk_level': 'Επίπεδο Κινδύνου',
                'risk_score': 'Βαθμολογία Κινδύνου',
                'status': 'Κατάσταση',
                'safe': 'ΑΣΦΑΛΗΣ',
                'suspicious': 'ΎΠΟΠΤΗ',
                'dangerous': 'ΕΠΙΚΙΝΔΥΝΗ',
                'api_connected': 'API Συνδεδεμένο',
                'api_disconnected': 'API Αποσυνδεδεμένο',
                'history': 'Ιστορικό',
                'statistics': 'Στατιστικά',
                'about': 'Σχετικά',
            }
        }
        
        self.setup_styles()
        self.setup_ui()
        self.check_api_connection()
    
    def get_text(self, key):
        """Get translated text"""
        return self.texts[self.language].get(key, key)
    
    def setup_styles(self):
        """Setup color schemes"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        if self.dark_mode:
            self.bg_color = '#1e1e1e'
            self.fg_color = '#e0e0e0'
            self.input_bg = '#2d2d2d'
            self.button_bg = '#0066cc'
            self.button_fg = '#ffffff'
            self.safe_color = '#00cc00'
            self.suspicious_color = '#ffaa00'
            self.dangerous_color = '#ff0000'
        else:
            self.bg_color = '#ffffff'
            self.fg_color = '#000000'
            self.input_bg = '#f5f5f5'
            self.button_bg = '#0066cc'
            self.button_fg = '#ffffff'
            self.safe_color = '#00aa00'
            self.suspicious_color = '#ff8800'
            self.dangerous_color = '#dd0000'
        
        self.configure(bg=self.bg_color)
    
    def setup_ui(self):
        """Setup user interface"""
        # Header
        header = tk.Frame(self, bg='#004499', height=50)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(
            header,
            text="🛡️ CyberGuard - Phishing Detection",
            font=('Arial', 16, 'bold'),
            bg='#004499',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # API Status
        self.api_status_label = tk.Label(
            header,
            text="🔴 API Disconnected",
            font=('Arial', 10),
            bg='#004499',
            fg='white'
        )
        self.api_status_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Main content
        content = tk.Frame(self, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Analyzer tab
        self.setup_analyzer_tab()
        
        # History tab
        self.setup_history_tab()
        
        # Stats tab
        self.setup_stats_tab()
        
        # About tab
        self.setup_about_tab()
        
        # Bottom toolbar
        self.setup_toolbar()
    
    def update_theme_colors(self):
        """Update all widgets with new theme colors"""
        self.configure(bg=self.bg_color)
        
        # Update main frames
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=self.bg_color)
        
        # Update text widgets
        try:
            self.email_input.configure(bg=self.input_bg, fg=self.fg_color)
            self.details_text.configure(bg=self.input_bg, fg=self.fg_color)
            self.history_text.configure(bg=self.input_bg, fg=self.fg_color)
            self.stats_text.configure(bg=self.input_bg, fg=self.fg_color)
        except:
            pass
        
        # Update labels
        self.risk_label.configure(bg=self.bg_color, fg=self.fg_color)
        self.score_label.configure(bg=self.bg_color, fg=self.fg_color)
        self.analysis_status.configure(bg=self.bg_color)
        
        messagebox.showinfo("Success", f"Switched to {'Dark' if self.dark_mode else 'Light'} Mode")
    
    def setup_analyzer_tab(self):
        """Setup email analyzer tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text=" 📧 Analyzer ")
        
        # Email input
        input_label = tk.Label(tab, text="Email Content:", bg=self.bg_color, fg=self.fg_color)
        input_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.email_input = scrolledtext.ScrolledText(
            tab,
            height=12,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.fg_color,
            font=('Courier', 10)
        )
        self.email_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.email_input.bind('<KeyRelease>', self.on_email_change)
        self.email_input.bind('<Button-3>', self.show_context_menu)
        self.email_input.bind('<Control-c>', self.on_copy_shortcut)
        self.email_input.bind('<Control-v>', self.on_paste_shortcut)
        self.email_input.bind('<Control-x>', self.on_cut_shortcut)
        
        # Analysis results
        results_frame = tk.Frame(tab, bg=self.bg_color)
        results_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicator
        self.analysis_status = tk.Label(
            results_frame,
            text="",
            font=('Arial', 9),
            bg=self.bg_color,
            fg='#ffaa00'
        )
        self.analysis_status.pack(side=tk.RIGHT, padx=5)
        
        # Risk level display
        self.risk_label = tk.Label(
            results_frame,
            text="Risk Level: -",
            font=('Arial', 12, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.risk_label.pack(side=tk.LEFT, padx=5)
        
        self.score_label = tk.Label(
            results_frame,
            text="Risk Score: -",
            font=('Arial', 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # Details
        details_label = tk.Label(tab, text="Analysis Details:", bg=self.bg_color, fg=self.fg_color)
        details_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.details_text = scrolledtext.ScrolledText(
            tab,
            height=6,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.fg_color,
            state=tk.DISABLED,
            font=('Courier', 9)
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.details_text.bind('<Button-3>', self.show_context_menu)
        self.details_text.bind('<Control-c>', self.on_copy_shortcut)
    
    def setup_history_tab(self):
        """Setup history tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text=" 📋 History ")
        
        button_frame = tk.Frame(tab, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_history,
            bg=self.button_bg,
            fg=self.button_fg
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = tk.Button(
            button_frame,
            text="📥 Export CSV",
            command=self.export_history_csv,
            bg='#009900',
            fg='white'
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        filter_label = tk.Label(button_frame, text="Filter:", bg=self.bg_color, fg=self.fg_color)
        filter_label.pack(side=tk.LEFT, padx=5)
        
        self.risk_filter = ttk.Combobox(
            button_frame,
            values=['All', 'SAFE', 'SUSPICIOUS', 'DANGEROUS'],
            state='readonly',
            width=15
        )
        self.risk_filter.set('All')
        self.risk_filter.pack(side=tk.LEFT, padx=5)
        self.risk_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_history())
        
        self.history_text = scrolledtext.ScrolledText(
            tab,
            height=20,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.fg_color,
            state=tk.DISABLED,
            font=('Courier', 9)
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.history_text.bind('<Button-3>', self.show_context_menu)
        self.history_text.bind('<Control-c>', self.on_copy_shortcut)
    
    def setup_stats_tab(self):
        """Setup statistics tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text=" 📊 Statistics ")
        
        button_frame = tk.Frame(tab, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh Statistics",
            command=self.refresh_stats,
            bg=self.button_bg,
            fg=self.button_fg
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.stats_text = scrolledtext.ScrolledText(
            tab,
            height=20,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.fg_color,
            state=tk.DISABLED,
            font=('Courier', 10)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.stats_text.bind('<Button-3>', self.show_context_menu)
        self.stats_text.bind('<Control-c>', self.on_copy_shortcut)
        
        self.refresh_stats()
    
    def setup_about_tab(self):
        """Setup about tab"""
        tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(tab, text=" ℹ️  About ")
        
        about_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            bg=self.input_bg,
            fg=self.fg_color,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        about_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_text.config(state=tk.NORMAL)
        about_text.insert(tk.END, """
CyberGuard v2.1 - API Integration Edition
Email Phishing Detection System

🛡️ FEATURES:
  • Multi-level threat detection (Keyword + Pattern + ML)
  • Real-time email analysis as you type
  • REST API backend for integration
  • Analysis history and statistics
  • Greek language support (Ελληνικά)
  • Dark/Light theme toggle
  • File format support (PDF, DOCX, TXT, HTML)
  • Copy/Paste from external applications
  • Secure local processing (no cloud)

🔬 DETECTION METHODS:
  1. Keyword Detection - Scans for 60+ suspicious keywords
  2. Pattern Detection - Identifies URLs, IPs, suspicious phrases
  3. Machine Learning - Logistic Regression classifier
  
🌐 API INTEGRATION:
  • Flask-based REST API server
  • JSON database storage
  • Analysis history and threat tracking
  • Real-time statistics endpoint

📊 STATISTICS:
  • Total analyses performed
  • Risk distribution (Safe/Suspicious/Dangerous)
  • Average risk scores
  • Threat trending

🏛️ MUNICIPALITY:
  Δήμος Αθηναίων (Athens Municipality)
  City Challenge Crowdhackathon 2025

👨‍💻 DEVELOPER:
  CyberGuard Development Team
  Created: November 2025

📝 LICENSE:
  Open Source - MIT License

🔒 SECURITY NOTES:
  • All processing is local to your machine
  • No internet connectivity required
  • No cloud services used
  • Encrypted database storage recommended

📧 CONTACT:
  For issues or suggestions, contact your administrator

Version: 2.1 (API Integrated)
Python 3.13 | Tkinter | scikit-learn | Flask
""")
        about_text.config(state=tk.DISABLED)
    
    def setup_toolbar(self):
        """Setup bottom toolbar"""
        toolbar = tk.Frame(self, bg='#2d2d2d', height=40)
        toolbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_font = ('Arial', 9)
        
        btn_analyze = tk.Button(
            toolbar,
            text="📊 Analyze",
            command=self.on_analyze,
            font=btn_font,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=15
        )
        btn_analyze.pack(side=tk.LEFT, padx=5, pady=8)
        
        btn_clear = tk.Button(
            toolbar,
            text="🗑️ Clear",
            command=self.on_clear,
            font=btn_font,
            bg='#cc0000',
            fg='white',
            padx=15
        )
        btn_clear.pack(side=tk.LEFT, padx=5, pady=8)
        
        btn_load = tk.Button(
            toolbar,
            text="📂 Load File",
            command=self.load_file,
            font=btn_font,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=15
        )
        btn_load.pack(side=tk.LEFT, padx=5, pady=8)
        
        btn_toggle_theme = tk.Button(
            toolbar,
            text="🌙 Theme",
            command=self.toggle_theme,
            font=btn_font,
            bg='#666666',
            fg='white',
            padx=15
        )
        btn_toggle_theme.pack(side=tk.RIGHT, padx=5, pady=8)
        
        # Language selector
        lang_label = tk.Label(toolbar, text="Language:", font=btn_font, bg='#2d2d2d', fg='white')
        lang_label.pack(side=tk.RIGHT, padx=5, pady=8)
        
        self.lang_combo = ttk.Combobox(
            toolbar,
            values=['EN', 'EL'],
            state='readonly',
            width=5,
            font=btn_font
        )
        self.lang_combo.set('EN')
        self.lang_combo.pack(side=tk.RIGHT, padx=5, pady=8)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)
    
    def check_api_connection(self):
        """Check if API server is running with retry logic"""
        def check():
            global API_ENABLED
            for attempt in range(API_RETRIES):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=2)
                    if response.status_code == 200:
                        self.api_connected = True
                        self.api_status_label.config(text="🟢 API Connected")
                        return
                except:
                    if attempt < API_RETRIES - 1:
                        time.sleep(API_RETRY_DELAY)
                        continue
            
            # All retries failed
            self.api_connected = False
            self.api_status_label.config(text="🔴 API Disconnected (Offline Mode)")
        
        Thread(target=check, daemon=True).start()
    
    def on_email_change(self, event=None):
        """Real-time analysis as user types"""
        self.current_email = self.email_input.get("1.0", tk.END)
        if len(self.current_email.strip()) > 20:
            self.on_analyze()
    
    def on_analyze(self):
        """Analyze email via API with progress indicator"""
        email_text = self.email_input.get("1.0", tk.END).strip()
        
        if not email_text:
            messagebox.showwarning("Warning", "Please enter email content")
            return
        
        # Show analyzing status
        self.analysis_status.config(text="⏳ Analyzing...", fg='#ffaa00')
        self.update_idletasks()
        
        if not self.api_connected:
            self.analysis_status.config(text="⚠️ Offline Mode (Limited Analysis)", fg='#ff8800')
            # Could implement fallback local analysis here
            return
        
        # Analyze via API with retry
        def analyze():
            try:
                data, error = api_request_with_retry(
                    'POST',
                    '/api/v1/analyze',
                    json={'email_text': email_text, 'subject': 'Email Analysis'},
                    timeout=API_TIMEOUT
                )
                
                if data:
                    self.current_analysis = data
                    self.display_analysis()
                    self.analysis_status.config(text="✅ Analysis Complete", fg='#00cc00')
                else:
                    self.analysis_status.config(text=f"❌ {error}", fg='#ff0000')
            except Exception as e:
                self.analysis_status.config(text=f"❌ Error: {str(e)}", fg='#ff0000')
        
        Thread(target=analyze, daemon=True).start()
    
    def display_analysis(self):
        """Display analysis results"""
        if not self.current_analysis:
            return
        
        analysis = self.current_analysis
        risk_level = analysis.get('risk_level', 'UNKNOWN')
        risk_score = analysis.get('risk_score', 0)
        
        # Update risk label
        risk_colors = {
            'SAFE': self.safe_color,
            'SUSPICIOUS': self.suspicious_color,
            'DANGEROUS': self.dangerous_color
        }
        
        self.risk_label.config(
            text=f"Risk Level: {risk_level}",
            fg=risk_colors.get(risk_level, self.fg_color)
        )
        self.score_label.config(text=f"Risk Score: {risk_score:.3f}")
        
        # Update details
        details = f"""
ANALYSIS RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Risk Level:     {risk_level}
Risk Score:     {risk_score:.3f}

COMPONENT SCORES:
  Keyword Score:  {analysis.get('keyword_score', 0):.3f}
  Pattern Score:  {analysis.get('pattern_score', 0):.3f}
  ML Score:       {analysis.get('ml_score', 0):.3f}

THREATS DETECTED:
  Keywords Found: {len(analysis.get('keywords_found', []))}
  Patterns Found: {len(analysis.get('patterns_found', {}))}

KEYWORDS:
  {', '.join(analysis.get('keywords_found', [])[:10]) if analysis.get('keywords_found') else 'None'}

PATTERNS:
  URLs: {len(analysis.get('patterns_found', {}).get('urls', []))}
  Emails: {len(analysis.get('patterns_found', {}).get('emails', []))}
  IPs: {len(analysis.get('patterns_found', {}).get('ips', []))}

Analysis ID: {analysis.get('analysis_id', 'N/A')}
Timestamp: {analysis.get('timestamp', 'N/A')}
"""
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)
        self.details_text.config(state=tk.DISABLED)
    
    def on_clear(self):
        """Clear input"""
        self.email_input.delete("1.0", tk.END)
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state=tk.DISABLED)
        self.risk_label.config(text="Risk Level: -", fg=self.fg_color)
        self.score_label.config(text="Risk Score: -")
    
    def load_file(self):
        """Load email from file with better error handling"""
        filetypes = [
            ("All Supported", "*.txt *.eml *.html *.htm *.csv *.msg"),
            ("Text Files", "*.txt *.eml *.html *.htm *.csv *.msg"),
            ("PDF Files", "*.pdf"),
            ("Word Documents", "*.docx *.doc"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if not filename:
            return
        
        try:
            content = ""
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                try:
                    import PyPDF2
                    with open(filename, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            content += page.extract_text() + "\n"
                except ImportError:
                    messagebox.showwarning("Warning", "PyPDF2 not installed.\nInstall with: pip install PyPDF2")
                    return
            
            elif file_ext in ['.docx', '.doc']:
                try:
                    import docx
                    if file_ext == '.docx':
                        doc = docx.Document(filename)
                        for para in doc.paragraphs:
                            content += para.text + "\n"
                    else:
                        messagebox.showwarning("Warning", ".doc files require additional library.\nPlease convert to .docx")
                        return
                except ImportError:
                    messagebox.showwarning("Warning", "python-docx not installed.\nInstall with: pip install python-docx")
                    return
            
            else:
                # Text-based files
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            if not content.strip():
                messagebox.showwarning("Warning", "File is empty or could not be read.")
                return
            
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, content)
            
            messagebox.showinfo("Success", f"Loaded {len(content)} characters from file")
            self.on_analyze()
        
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load file: {str(e)}")
    
    def refresh_history(self):
        """Refresh analysis history from API"""
        if not self.api_connected:
            messagebox.showerror("Error", "API is not connected")
            return
        
        def fetch():
            try:
                risk_filter = self.risk_filter.get()
                if risk_filter == 'All':
                    data, error = api_request_with_retry('GET', '/api/v1/history?limit=50')
                else:
                    data, error = api_request_with_retry('GET', f'/api/v1/history?limit=50&risk_level={risk_filter}')
                
                if data:
                    history_text = f"Total Analyses: {data.get('total_count', 0)}\nFiltered: {data.get('filtered_count', 0)}\n\n"
                    
                    for analysis in data.get('analyses', []):
                        history_text += f"""
{'─' * 70}
Subject: {analysis.get('subject', 'N/A')}
Risk: {analysis.get('risk_level')} ({analysis.get('risk_score')})
Time: {analysis.get('timestamp', 'N/A')}
Keywords: {len(analysis.get('keywords_found', []))}
"""
                    
                    self.history_text.config(state=tk.NORMAL)
                    self.history_text.delete("1.0", tk.END)
                    self.history_text.insert(tk.END, history_text)
                    self.history_text.config(state=tk.DISABLED)
                    
                    # Store for export
                    self.last_history_data = data.get('analyses', [])
                else:
                    messagebox.showerror("Error", f"Cannot fetch history: {error}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot fetch history: {str(e)}")
        
        Thread(target=fetch, daemon=True).start()
    
    def export_history_csv(self):
        """Export analysis history to CSV file"""
        if not hasattr(self, 'last_history_data') or not self.last_history_data:
            messagebox.showwarning("Warning", "No history data to export. Refresh history first.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Timestamp', 'Subject', 'Risk Level', 'Risk Score', 'Keyword Score', 'Pattern Score', 'ML Score', 'Keywords Found']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for analysis in self.last_history_data:
                    writer.writerow({
                        'Timestamp': analysis.get('timestamp', ''),
                        'Subject': analysis.get('subject', ''),
                        'Risk Level': analysis.get('risk_level', ''),
                        'Risk Score': f"{analysis.get('risk_score', 0):.3f}",
                        'Keyword Score': f"{analysis.get('keyword_score', 0):.3f}",
                        'Pattern Score': f"{analysis.get('pattern_score', 0):.3f}",
                        'ML Score': f"{analysis.get('ml_score', 0):.3f}",
                        'Keywords Found': ', '.join(analysis.get('keywords_found', [])[:10])
                    })
            
            messagebox.showinfo("Success", f"History exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot export: {str(e)}")
    
    def refresh_stats(self):
        """Refresh statistics from API"""
        if not self.api_connected:
            stats_text = "API Not Connected\n\nStart the API server to view statistics."
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            return
        
        def fetch():
            try:
                data, error = api_request_with_retry('GET', '/api/v1/statistics')
                
                if data:
                    stats = data
                    stats_text = f"""
ANALYSIS STATISTICS
{'═' * 60}

Total Analyses:        {stats.get('total_analyses', 0)}

RISK DISTRIBUTION:
  Safe Emails:         {stats.get('safe_count', 0)} ({stats.get('safe_percentage', 0):.1f}%)
  Suspicious Emails:   {stats.get('suspicious_count', 0)} ({stats.get('suspicious_percentage', 0):.1f}%)
  Dangerous Emails:    {stats.get('dangerous_count', 0)} ({stats.get('dangerous_percentage', 0):.1f}%)

METRICS:
  Average Risk Score:  {stats.get('average_risk_score', 0):.3f}

{'═' * 60}

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    
                    self.stats_text.config(state=tk.NORMAL)
                    self.stats_text.delete("1.0", tk.END)
                    self.stats_text.insert(tk.END, stats_text)
                    self.stats_text.config(state=tk.DISABLED)
                else:
                    error_text = f"Cannot fetch statistics:\n{error}"
                    self.stats_text.config(state=tk.NORMAL)
                    self.stats_text.delete("1.0", tk.END)
                    self.stats_text.insert(tk.END, error_text)
                    self.stats_text.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot fetch statistics: {str(e)}")
        
        Thread(target=fetch, daemon=True).start()
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        menu = tk.Menu(self, tearoff=0, bg='#2d2d2d', fg=self.fg_color)
        menu.add_command(label="Copy", command=self.copy_text)
        menu.add_command(label="Paste", command=self.paste_text)
        menu.add_command(label="Cut", command=self.cut_text)
        menu.add_separator()
        menu.add_command(label="Select All", command=self.select_all)
        menu.add_command(label="Clear", command=self.on_clear)
        
        menu.post(event.x_root, event.y_root)
    
    def get_focused_widget(self):
        """Get the currently focused text widget"""
        try:
            focused = self.focus_get()
            if isinstance(focused, scrolledtext.ScrolledText):
                return focused
            # Try to find any selected widget
            for widget in [self.email_input, self.details_text, self.history_text, self.stats_text]:
                try:
                    if widget.get(tk.SEL_FIRST, tk.SEL_LAST):
                        return widget
                except:
                    pass
            return self.email_input  # Default to email input
        except:
            return self.email_input
    
    def on_copy_shortcut(self, event=None):
        """Handle Ctrl+C shortcut"""
        self.copy_text()
        return 'break'
    
    def on_paste_shortcut(self, event=None):
        """Handle Ctrl+V shortcut"""
        self.paste_text()
        return 'break'
    
    def on_cut_shortcut(self, event=None):
        """Handle Ctrl+X shortcut"""
        self.cut_text()
        return 'break'
    
    def copy_text(self):
        """Copy selected text from any text widget"""
        try:
            widget = self.get_focused_widget()
            text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            
            self.clipboard_clear()
            self.clipboard_append(text)
            # Don't show message for keyboard shortcuts
        except:
            pass
    
    def paste_text(self):
        """Paste text from clipboard to email input"""
        try:
            text = self.clipboard_get()
            self.email_input.delete("1.0", tk.END)
            self.email_input.insert(tk.END, text)
            self.on_analyze()
        except:
            messagebox.showerror("Error", "Cannot paste from clipboard")
    
    def cut_text(self):
        """Cut selected text from email input"""
        try:
            widget = self.get_focused_widget()
            text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)
            
            # Only delete if it's the email_input (writable widget)
            if widget == self.email_input:
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def select_all(self):
        """Select all text in focused widget"""
        try:
            widget = self.get_focused_widget()
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
        except:
            pass
    
    def toggle_theme(self):
        """Toggle dark/light theme in real-time"""
        self.dark_mode = not self.dark_mode
        self.setup_styles()
        self.update_theme_colors()
    
    def on_language_change(self, event=None):
        """Change language dynamically"""
        new_lang = 'el' if self.lang_combo.get() == 'EL' else 'en'
        if new_lang != self.language:
            self.language = new_lang
            self.update_ui_text()
    
    def update_ui_text(self):
        """Update all UI text based on current language"""
        try:
            # Update window title
            self.title(self.get_text('title'))
            
            # Update tab names
            for tab_index, tab_name in enumerate(['📧 Analyzer', '📋 History', '📊 Statistics', 'ℹ️  About']):
                self.notebook.tab(tab_index, text=tab_name)
        except:
            pass

if __name__ == '__main__':
    app = CyberGuardDesktop()
    app.mainloop()
