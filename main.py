

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import socket
import threading
import qrcode
import os
import zipfile
import io
import secrets
import time
import json
import subprocess
import platform
import sys
from PIL import Image, ImageTk
from flask import Flask, send_file, render_template_string, request, session, redirect, url_for
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from pyngrok import ngrok
    NGROK_OK = True
except:
    NGROK_OK = False

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app_data = {
    'files': [],
    'password_hash': None,
    'download_count': 0,
    'start_time': None,
    'unique_ips': set(),
    'download_log': []
}

# Beautiful mobile-optimized HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ShareFast Pro</title>
    <style>
        :root {
            --bg: #fff;
            --card: #f8f9fa;
            --txt: #333;
            --sub: #666;
            --g1: #667eea;
            --g2: #764ba2;
            --ok: #10b981;
            --err: #ef4444;
            --sh: rgba(0,0,0,.1);
        }

        [data-theme=dark] {
            --bg: #1a1a2e;
            --card: #16213e;
            --txt: #fff;
            --sub: #b8b8b8;
            --sh: rgba(0,0,0,.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--g1), var(--g2));
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: var(--bg);
            border-radius: 24px;
            box-shadow: 0 20px 60px var(--sh);
            max-width: 650px;
            width: 100%;
            padding: 40px;
            text-align: center;
            animation: slideUp 0.5s;
            position: relative;
            color: var(--txt);
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--card);
            border: none;
            border-radius: 50px;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.5rem;
            transition: 0.3s;
            box-shadow: 0 4px 15px var(--sh);
        }

        .theme-toggle:hover {
            transform: rotate(180deg) scale(1.1);
        }

        .logo {
            font-size: 4.5rem;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        h1 {
            background: linear-gradient(135deg, var(--g1), var(--g2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 10px;
        }

        .subtitle {
            color: var(--sub);
            margin-bottom: 30px;
            font-size: 1.1rem;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            background: var(--card);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
            box-shadow: 0 4px 15px var(--sh);
        }

        .stat {
            text-align: center;
            flex: 1;
            min-width: 100px;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--g1);
        }

        .stat-label {
            font-size: 0.85rem;
            color: var(--sub);
            margin-top: 5px;
        }

        .file-box {
            background: var(--card);
            padding: 25px;
            border-radius: 20px;
            margin: 25px 0;
            box-shadow: 0 4px 15px var(--sh);
        }

        .file-box h3 {
            color: var(--txt);
            margin-bottom: 20px;
            font-size: 1.3rem;
        }

        .file-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 18px;
            background: var(--bg);
            border-radius: 12px;
            margin: 12px 0;
            box-shadow: 0 4px 15px var(--sh);
            transition: 0.3s;
        }

        .file-item:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px var(--sh);
        }

        .file-info {
            text-align: left;
            flex: 1;
        }

        .file-name {
            font-weight: 600;
            color: var(--txt);
            word-break: break-all;
            margin-bottom: 5px;
        }

        .file-size {
            color: var(--sub);
            font-size: 0.9rem;
        }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            background: linear-gradient(135deg, var(--ok), #059669);
            color: #fff;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .download-btn {
            background: linear-gradient(135deg, var(--g1), var(--g2));
            color: #fff;
            padding: 18px 45px;
            border: none;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: 700;
            cursor: pointer;
            transition: 0.4s;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .download-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
        }

        .download-btn:active {
            transform: translateY(-2px);
        }

        .input {
            padding: 15px 25px;
            border: 2px solid var(--card);
            border-radius: 12px;
            font-size: 1.1rem;
            width: 100%;
            max-width: 350px;
            margin-bottom: 15px;
            background: var(--bg);
            color: var(--txt);
            transition: 0.3s;
        }

        .input:focus {
            outline: 0;
            border-color: var(--g1);
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        .error {
            color: var(--err);
            margin-top: 15px;
            font-weight: 600;
            padding: 12px;
            background: rgba(239, 68, 68, 0.1);
            border-radius: 10px;
        }

        .success {
            color: var(--ok);
            margin-top: 15px;
            font-weight: 600;
            font-size: 1.1rem;
        }

        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--card);
            color: var(--sub);
            font-size: 0.9rem;
        }

        @media (max-width: 600px) {
            .container {
                padding: 25px;
            }
            h1 {
                font-size: 2.2rem;
            }
            .logo {
                font-size: 3.5rem;
            }
            .stats {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">🌙</button>

        <div class="logo">⚡</div>
        <h1>ShareFast Pro</h1>
        <p class="subtitle">Professional File Sharing</p>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{downloads}}</div>
                <div class="stat-label">Downloads</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{users}}</div>
                <div class="stat-label">Users</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{uptime}}</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>

        {% if password_required %}
        <div class="file-box">
            <h3>🔐 Password Required</h3>
            <form method="POST">
                <input type="password" name="password" class="input" placeholder="Enter password" required autofocus>
                <button type="submit" class="download-btn">🔓 Unlock</button>
            </form>
            {% if error %}
            <p class="error">❌ {{error}}</p>
            {% endif %}
        </div>
        {% else %}
        <div class="file-box">
            <h3>📦 {{file_count}} File(s) Ready</h3>
            {% for file in files %}
            <div class="file-item">
                <div class="file-info">
                    <div class="file-name">📄 {{file.name}}</div>
                    <div class="file-size">{{file.size}}</div>
                </div>
                <span class="badge">Ready</span>
            </div>
            {% endfor %}
            <p class="success">✅ Ready to download!</p>
        </div>
        <a href="/download" class="download-btn">
            ⬇️ Download {% if file_count > 1 %}All Files{% else %}File{% endif %}
        </a>
        {% endif %}

        <div class="footer">
            <p>🚀 ShareFast Pro v5.1</p>
            <p style="margin-top: 10px; font-size: 0.85rem;">Secure • Fast • Professional</p>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const btn = document.getElementById('theme-btn');
            const currentTheme = html.getAttribute('data-theme');

            if (currentTheme === 'dark') {
                html.removeAttribute('data-theme');
                btn.textContent = '🌙';
                localStorage.setItem('theme', 'light');
            } else {
                html.setAttribute('data-theme', 'dark');
                btn.textContent = '☀️';
                localStorage.setItem('theme', 'dark');
            }
        }

        // Load saved theme
        window.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            const btn = document.getElementById('theme-btn');
            if (savedTheme === 'dark') {
                document.documentElement.setAttribute('data-theme', 'dark');
                btn.textContent = '☀️';
            }
        });
    </script>
</body>
</html>"""


def get_uptime():
    """Calculate uptime in human-readable format"""
    if app_data['start_time']:
        seconds = int(time.time() - app_data['start_time'])
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m"
    return "0s"


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with file list"""
    password_required = app_data['password_hash'] is not None

    # Handle password authentication
    if request.method == 'POST' and password_required:
        entered_password = request.form.get('password', '')
        if check_password_hash(app_data['password_hash'], entered_password):
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(
                HTML_TEMPLATE,
                password_required=True,
                error="Incorrect password!",
                files=[],
                file_count=0,
                downloads=app_data['download_count'],
                users=len(app_data['unique_ips']),
                uptime=get_uptime()
            )

    # Check if password is required and user is not authenticated
    if password_required and not session.get('authenticated'):
        return render_template_string(
            HTML_TEMPLATE,
            password_required=True,
            error=None,
            files=[],
            file_count=0,
            downloads=app_data['download_count'],
            users=len(app_data['unique_ips']),
            uptime=get_uptime()
        )

    # Track unique IPs
    app_data['unique_ips'].add(request.remote_addr)

    # Prepare file information
    file_info = []
    for file_path in app_data['files']:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_str = f"{size / (1024*1024):.2f} MB" if size > 1024 * \
                1024 else f"{size / 1024:.2f} KB"
            file_info.append({
                'name': os.path.basename(file_path),
                'size': size_str
            })

    return render_template_string(
        HTML_TEMPLATE,
        password_required=False,
        error=None,
        files=file_info,
        file_count=len(file_info),
        downloads=app_data['download_count'],
        users=len(app_data['unique_ips']),
        uptime=get_uptime()
    )


@app.route('/download')
def download():
    """Handle file downloads"""
    # Check authentication
    if app_data['password_hash'] and not session.get('authenticated'):
        return redirect(url_for('index'))

    # Increment download count
    app_data['download_count'] += 1

    # Log download
    now = datetime.now()
    app_data['download_log'].append({
        'ip': request.remote_addr,
        'time': now.strftime('%I:%M:%S %p'),
        'date': now.strftime('%d-%b-%Y')
    })

    files = app_data['files']

    if not files:
        return "No files available", 404

    # Single file download
    if len(files) == 1:
        file_path = files[0]
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=os.path.basename(file_path)
            )
        else:
            return "File not found", 404

    # Multiple files - create ZIP
    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in files:
                if os.path.exists(file_path):
                    zip_file.write(file_path, os.path.basename(file_path))

        zip_buffer.seek(0)
        zip_name = f'ShareFast_{now.strftime("%d%b%Y_%I%M%p")}.zip'

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_name
        )
    except Exception as e:
        return f"Error creating ZIP: {e}", 500


class ShareFastGUI:
    def __init__(self, root):
        self.root = root
        self.files = []
        self.port = None
        self.sharing = False
        self.flask_thread = None
        self.ngrok_tunnel = None
        self.timer_thread = None
        self.exp_time = None
        self.history_file = "sharefast_history.json"

        root.title("⚡ ShareFast Pro v5.1 - Professional Edition")
        root.geometry("800x950")

        self.setup_ui()
        threading.Thread(target=self.monitor_stats, daemon=True).start()
        self.check_firewall()

    def check_firewall(self):
        """Check and configure Windows Firewall"""
        if platform.system() != 'Windows':
            return

        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'currentprofile'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if 'ON' in result.stdout:
                if messagebox.askyesno(
                    "🔥 Firewall Detected",
                    "⚠️ Windows Firewall is ON\n\n"
                    "This WILL block phone access!\n\n"
                    "Add ShareFast exception?\n"
                    "(Requires Administrator privileges)"
                ):
                    self.configure_firewall()
        except:
            pass

    def configure_firewall(self):
        """Add firewall exception"""
        try:
            exe_path = sys.executable
            rule_name = "ShareFast Pro"

            # Remove old rule if exists
            subprocess.run(
                f'netsh advfirewall firewall delete rule name="{rule_name}"',
                shell=True,
                capture_output=True
            )

            # Add new rule
            cmd = (
                f'netsh advfirewall firewall add rule '
                f'name="{rule_name}" '
                f'dir=in '
                f'action=allow '
                f'program="{exe_path}" '
                f'enable=yes '
                f'profile=any'
            )

            result = subprocess.run(cmd, shell=True, capture_output=True)

            if result.returncode == 0:
                messagebox.showinfo(
                    "✅ Success!",
                    "Firewall exception added successfully!\n\n"
                    "✅ Phones can now connect to your shared files\n\n"
                    "Click START SHARING to begin"
                )
            else:
                raise Exception("Failed to add firewall rule")

        except Exception as e:
            messagebox.showwarning(
                "Manual Setup Required",
                f"Please add Python to Windows Firewall manually:\n\n"
                f"1. Open Windows Security\n"
                f"2. Firewall & network protection\n"
                f"3. Allow an app through firewall\n"
                f"4. Add this program:\n{sys.executable}\n\n"
                f"Or temporarily disable Windows Firewall"
            )

    def setup_ui(self):
        """Setup the GUI"""
        # Main scrollable frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            int(-1*(e.delta/120)), "units"))

        # Header
        header = tk.Frame(scrollable_frame, bg='#667eea', height=100)
        header.pack(fill=tk.X, pady=(0, 12))

        header_top = tk.Frame(header, bg='#667eea')
        header_top.pack(fill=tk.X, padx=18, pady=(10, 0))

        tk.Label(
            header_top,
            text="⚡ ShareFast Pro",
            font=("Arial", 32, "bold"),
            bg='#667eea',
            fg='white'
        ).pack(side=tk.LEFT)

        theme_btn = tk.Button(
            header_top,
            text="🌙",
            font=("Arial", 16),
            bg='#764ba2',
            fg='white',
            bd=0,
            cursor='hand2',
            command=lambda: messagebox.showinfo(
                "Theme Toggle",
                "Theme toggle is available in the web interface!\n\n"
                "Click the 🌙/☀️ button on the download page."
            )
        )
        theme_btn.pack(side=tk.RIGHT, padx=8)

        tk.Label(
            header,
            text="Professional File Sharing",
            font=("Arial", 10),
            bg='#667eea',
            fg='white'
        ).pack(pady=(5, 10))

        # File Selection Card
        file_card = tk.LabelFrame(
            scrollable_frame,
            text="📁 Select Files",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=12
        )
        file_card.pack(fill=tk.X, padx=12, pady=6)

        btn_row = tk.Frame(file_card)
        btn_row.pack(pady=6)

        tk.Button(
            btn_row,
            text="📂 Choose Files",
            command=self.select_files,
            font=("Arial", 10, "bold"),
            bg='#667eea',
            fg='white',
            padx=20,
            pady=10,
            bd=0,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row,
            text="📁 Choose Folder",
            command=self.select_folder,
            font=("Arial", 10, "bold"),
            bg='#764ba2',
            fg='white',
            padx=20,
            pady=10,
            bd=0,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=4)

        self.files_label = tk.Label(
            file_card,
            text="No files selected",
            font=("Arial", 9),
            fg='gray'
        )
        self.files_label.pack(pady=4)

        self.files_listbox = tk.Listbox(file_card, height=4, font=("Arial", 8))
        self.files_listbox.pack(fill=tk.X, pady=4)

        # Configuration Card
        config_card = tk.LabelFrame(
            scrollable_frame,
            text="⚙️ Configuration",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=12
        )
        config_card.pack(fill=tk.X, padx=12, pady=6)

        self.lan_only_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            config_card,
            text="🏠 LAN Mode Only (Same WiFi - Secure & Fast)",
            variable=self.lan_only_var,
            font=("Arial", 9, "bold")
        ).pack(anchor=tk.W, pady=3)

        timer_row = tk.Frame(config_card)
        timer_row.pack(fill=tk.X, pady=4)

        tk.Label(timer_row, text="⏰ Auto-stop after:",
                 font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        self.timer_var = tk.IntVar(value=30)
        tk.Spinbox(
            timer_row,
            from_=5,
            to=180,
            textvariable=self.timer_var,
            width=8,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=8)
        tk.Label(timer_row, text="minutes", font=(
            "Arial", 9)).pack(side=tk.LEFT)

        self.password_var = tk.BooleanVar()
        tk.Checkbutton(
            config_card,
            text="🔐 Password Protection",
            variable=self.password_var,
            command=self.toggle_password,
            font=("Arial", 9, "bold")
        ).pack(anchor=tk.W, pady=3)

        pass_row = tk.Frame(config_card)
        pass_row.pack(fill=tk.X, pady=3)
        tk.Label(pass_row, text="Password:", font=(
            "Arial", 8)).pack(side=tk.LEFT, padx=(12, 6))
        self.password_entry = tk.Entry(
            pass_row,
            show="*",
            font=("Arial", 9),
            state='disabled',
            width=25
        )
        self.password_entry.pack(side=tk.LEFT)

        # Action Buttons
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=12)

        self.start_btn = tk.Button(
            button_frame,
            text="🚀 START SHARING",
            font=("Arial", 12, "bold"),
            bg='#10b981',
            fg='white',
            padx=28,
            pady=12,
            bd=0,
            cursor='hand2',
            command=self.start_sharing
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ STOP",
            font=("Arial", 12, "bold"),
            bg='#ef4444',
            fg='white',
            padx=28,
            pady=12,
            bd=0,
            cursor='hand2',
            command=self.stop_sharing,
            state='disabled'
        )
        self.stop_btn.grid(row=0, column=1, padx=6)

        tk.Button(
            button_frame,
            text="📊 Analytics",
            font=("Arial", 10, "bold"),
            bg='#3b82f6',
            fg='white',
            padx=24,
            pady=12,
            bd=0,
            cursor='hand2',
            command=self.show_analytics
        ).grid(row=0, column=2, padx=6)

        # Status Card
        status_card = tk.LabelFrame(
            scrollable_frame,
            text="📊 Live Dashboard",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=12
        )
        status_card.pack(fill=tk.BOTH, padx=12, pady=6, expand=True)

        self.status_label = tk.Label(
            status_card,
            text="⚪ Ready to Share",
            font=("Arial", 10, "bold"),
            fg='#666'
        )
        self.status_label.pack(pady=6)

        self.timer_label = tk.Label(
            status_card,
            text="",
            font=("Arial", 9, "bold"),
            fg='orange'
        )
        self.timer_label.pack()

        self.stats_label = tk.Label(
            status_card,
            text="📊 Downloads: 0 | 👥 Users: 0 | ⏱️ Uptime: 0s",
            font=("Arial", 8, "bold"),
            fg='blue'
        )
        self.stats_label.pack(pady=3)

        tk.Label(
            status_card,
            text="📎 Share These Links:",
            font=("Arial", 8, "bold")
        ).pack(pady=(6, 3))

        self.url_text = scrolledtext.ScrolledText(
            status_card,
            height=5,
            font=("Courier", 8),
            wrap=tk.WORD,
            state='disabled'
        )
        self.url_text.pack(fill=tk.BOTH, pady=3)

        tk.Button(
            status_card,
            text="📋 Copy Links",
            command=self.copy_urls,
            font=("Arial", 9, "bold"),
            bg='#667eea',
            fg='white',
            padx=18,
            pady=8,
            bd=0,
            cursor='hand2'
        ).pack(pady=3)

        tk.Label(
            status_card,
            text="📱 QR Code (Scan with Phone):",
            font=("Arial", 8, "bold")
        ).pack(pady=(6, 3))

        self.qr_container = tk.Frame(
            status_card,
            bg='#f0f0f0',
            width=240,
            height=240,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.qr_container.pack(pady=3)
        self.qr_container.pack_propagate(False)

        self.qr_label = tk.Label(
            self.qr_container,
            text="QR code will appear here",
            bg='#f0f0f0',
            font=("Arial", 8)
        )
        self.qr_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Footer
        footer = tk.Frame(scrollable_frame, bg='#e8f5e9')
        footer.pack(fill=tk.X, pady=(12, 0))

        footer_text = """ "🚀 ShareFast Pro v5.1 - Professional Edition" """

        tk.Label(
            footer,
            text=footer_text,
            font=("Arial", 8),
            bg='#e8f5e9',
            fg='#1b5e20',
            justify='left'
        ).pack(pady=12, padx=20)

    def toggle_password(self):
        """Toggle password entry state"""
        state = 'normal' if self.password_var.get() else 'disabled'
        self.password_entry.config(state=state)
        if state == 'normal':
            self.password_entry.focus()
        else:
            self.password_entry.delete(0, tk.END)

    def select_files(self):
        """Select multiple files"""
        files = filedialog.askopenfilenames(title="Select files to share")
        if files:
            self.files = list(files)
            total_size = sum(os.path.getsize(f) for f in files) / (1024 * 1024)

            self.files_label.config(
                text=f"✅ {len(files)} file(s) selected • {total_size:.2f} MB",
                fg='#10b981',
                font=("Arial", 9, "bold")
            )

            self.files_listbox.delete(0, tk.END)
            for file in files[:8]:
                size = os.path.getsize(file) / (1024 * 1024)
                self.files_listbox.insert(
                    tk.END,
                    f"📄 {os.path.basename(file)} ({size:.2f} MB)"
                )

            if len(files) > 8:
                self.files_listbox.insert(
                    tk.END, f"... and {len(files) - 8} more files")

    def select_folder(self):
        """Select entire folder"""
        folder = filedialog.askdirectory(title="Select folder to share")
        if folder:
            files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))
            ]

            if files:
                self.files = files
                total_size = sum(os.path.getsize(f)
                                 for f in files) / (1024 * 1024)

                self.files_label.config(
                    text=f"✅ {len(files)} file(s) from folder • {total_size:.2f} MB",
                    fg='#10b981',
                    font=("Arial", 9, "bold")
                )

                self.files_listbox.delete(0, tk.END)
                for file in files[:8]:
                    size = os.path.getsize(file) / (1024 * 1024)
                    self.files_listbox.insert(
                        tk.END,
                        f"📄 {os.path.basename(file)} ({size:.2f} MB)"
                    )

                if len(files) > 8:
                    self.files_listbox.insert(
                        tk.END, f"... and {len(files) - 8} more files")
            else:
                messagebox.showwarning(
                    "Empty Folder", "Selected folder contains no files!")

    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def find_free_port(self):
        """Find available port"""
        for port in range(5000, 5100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except:
                continue
        return 5000

    def generate_qr(self, url):
        """Generate QR code"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color='#667eea', back_color='white')
            img = img.resize((220, 220), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=photo, text="", bg='white')
            self.qr_label.image = photo
        except Exception as e:
            self.qr_label.config(text=f"QR Error: {e}")

    def copy_urls(self):
        """Copy URLs to clipboard"""
        urls = self.url_text.get("1.0", tk.END).strip()
        if urls and "Ready" not in urls:
            self.root.clipboard_clear()
            self.root.clipboard_append(urls)
            messagebox.showinfo(
                "✅ Copied!",
                "Links copied to clipboard!\n\n"
                "Paste in WhatsApp, Telegram, or any messaging app!"
            )

    def timer_countdown(self):
        """Countdown timer"""
        minutes = self.timer_var.get()
        self.exp_time = datetime.now() + timedelta(minutes=minutes)

        while self.sharing and self.exp_time:
            remaining = (self.exp_time - datetime.now()).total_seconds()
            if remaining <= 0:
                self.root.after(0, self.stop_sharing)
                break

            mins, secs = divmod(int(remaining), 60)
            self.root.after(
                0,
                lambda m=mins, s=secs: self.timer_label.config(
                    text=f"⏰ Auto-stop in: {m}m {s}s"
                )
            )
            time.sleep(1)

    def monitor_stats(self):
        """Monitor and update statistics"""
        while True:
            if self.sharing and app_data['start_time']:
                uptime_secs = int(time.time() - app_data['start_time'])
                downloads = app_data['download_count']
                users = len(app_data['unique_ips'])

                text = f"📊 Downloads: {downloads} | 👥 Users: {users} | ⏱️ Uptime: {uptime_secs}s"
                self.root.after(
                    0, lambda t=text: self.stats_label.config(text=t))
            time.sleep(1)

    def save_history(self, url, mode):
        """Save transfer history"""
        try:
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)

            now = datetime.now()
            entry = {
                'timestamp': now.strftime('%d/%m/%Y %I:%M:%S %p'),
                'files': [os.path.basename(f) for f in self.files],
                'file_count': len(self.files),
                'total_size_mb': sum(os.path.getsize(f) for f in self.files) / (1024 * 1024),
                'url': url,
                'mode': mode,
                'downloads': 0
            }

            history.append(entry)
            history = history[-100:]  # Keep last 100 entries

            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            print(f"Failed to save history: {e}")

    def show_analytics(self):
        """Show analytics dashboard"""
        if not os.path.exists(self.history_file):
            messagebox.showinfo(
                "📊 Analytics",
                "No transfer history yet!\n\n"
                "Start sharing files to see analytics."
            )
            return

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)

            # Create analytics window
            analytics_win = tk.Toplevel(self.root)
            analytics_win.title("📊 ShareFast Pro - Analytics Dashboard")
            analytics_win.geometry("900x600")
            analytics_win.configure(bg='#f5f5f5')

            # Header
            header = tk.Frame(analytics_win, bg='#667eea', height=80)
            header.pack(fill=tk.X)
            header.pack_propagate(False)

            tk.Label(
                header,
                text="📊 Analytics Dashboard",
                font=("Arial", 24, "bold"),
                bg='#667eea',
                fg='white'
            ).pack(pady=20)

            # Summary statistics
            summary_frame = tk.Frame(
                analytics_win, bg='white', relief=tk.RAISED, bd=2)
            summary_frame.pack(fill=tk.X, padx=20, pady=20)

            total_transfers = len(history)
            total_files = sum(h.get('file_count', 0) for h in history)
            total_size_gb = sum(h.get('total_size_mb', 0)
                                for h in history) / 1024
            total_downloads = sum(h.get('downloads', 0) for h in history)

            stats = [
                ("📦", "Total Transfers", total_transfers),
                ("📄", "Files Shared", total_files),
                ("💾", "Data Shared", f"{total_size_gb:.2f} GB"),
                ("⬇️", "Total Downloads", total_downloads)
            ]

            for i, (icon, label, value) in enumerate(stats):
                stat_frame = tk.Frame(
                    summary_frame, bg='white', padx=15, pady=15)
                stat_frame.grid(row=0, column=i, padx=10, pady=10)

                tk.Label(
                    stat_frame,
                    text=icon,
                    font=("Arial", 30),
                    bg='white'
                ).pack()

                tk.Label(
                    stat_frame,
                    text=str(value),
                    font=("Arial", 18, "bold"),
                    bg='white',
                    fg='#667eea'
                ).pack()

                tk.Label(
                    stat_frame,
                    text=label,
                    font=("Arial", 9),
                    bg='white',
                    fg='gray'
                ).pack()

            # History table
            table_frame = tk.Frame(analytics_win)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            tk.Label(
                table_frame,
                text="📋 Transfer History",
                font=("Arial", 14, "bold")
            ).pack(pady=10)

            tree_container = tk.Frame(table_frame)
            tree_container.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(tree_container)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            tree = ttk.Treeview(
                tree_container,
                columns=('Timestamp', 'Files', 'Size', 'Mode', 'Downloads'),
                show='headings',
                yscrollcommand=scrollbar.set
            )

            tree.heading('Timestamp', text='Timestamp (IST)')
            tree.heading('Files', text='Files')
            tree.heading('Size', text='Size (MB)')
            tree.heading('Mode', text='Mode')
            tree.heading('Downloads', text='Downloads')

            tree.column('Timestamp', width=180)
            tree.column('Files', width=100)
            tree.column('Size', width=120)
            tree.column('Mode', width=150)
            tree.column('Downloads', width=120)

            for entry in reversed(history):
                mode = '🌍 Internet' if 'ngrok' in entry.get(
                    'url', '') else '🏠 LAN'
                tree.insert('', 0, values=(
                    entry.get('timestamp', 'N/A'),
                    f"{entry.get('file_count', 0)} file(s)",
                    f"{entry.get('total_size_mb', 0):.2f}",
                    mode,
                    entry.get('downloads', 0)
                ))

            tree.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=tree.yview)

            # Buttons
            btn_frame = tk.Frame(analytics_win, bg='#f5f5f5')
            btn_frame.pack(pady=15)

            tk.Button(
                btn_frame,
                text="💾 Export Report",
                font=("Arial", 10, "bold"),
                bg='#10b981',
                fg='white',
                padx=20,
                pady=10,
                bd=0,
                cursor='hand2',
                command=lambda: self.export_analytics(history)
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                btn_frame,
                text="✅ Close",
                font=("Arial", 10, "bold"),
                bg='#667eea',
                fg='white',
                padx=20,
                pady=10,
                bd=0,
                cursor='hand2',
                command=analytics_win.destroy
            ).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load analytics:\n{e}")

    def export_analytics(self, history):
        """Export analytics to text file"""
        try:
            filename = f"ShareFast_Analytics_{datetime.now().strftime('%Y%m%d_%I%M%p')}.txt"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=filename,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("SHAREFAST PRO - ANALYTICS REPORT\n")
                    f.write(
                        f"Generated: {datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')}\n")
                    f.write("=" * 80 + "\n\n")

                    # Summary
                    f.write("SUMMARY STATISTICS\n")
                    f.write("-" * 80 + "\n")
                    total_transfers = len(history)
                    total_files = sum(h.get('file_count', 0) for h in history)
                    total_size_gb = sum(h.get('total_size_mb', 0)
                                        for h in history) / 1024
                    total_downloads = sum(h.get('downloads', 0)
                                          for h in history)

                    f.write(f"Total Transfers: {total_transfers}\n")
                    f.write(f"Total Files Shared: {total_files}\n")
                    f.write(f"Total Data Shared: {total_size_gb:.2f} GB\n")
                    f.write(f"Total Downloads: {total_downloads}\n\n")

                    # Detailed history
                    f.write("DETAILED TRANSFER HISTORY\n")
                    f.write("-" * 80 + "\n\n")

                    for i, entry in enumerate(reversed(history), 1):
                        f.write(f"Transfer #{i}\n")
                        f.write(
                            f"Timestamp: {entry.get('timestamp', 'N/A')}\n")
                        f.write(
                            f"Files: {entry.get('file_count', 0)} ({entry.get('total_size_mb', 0):.2f} MB)\n")
                        mode = 'Internet (Ngrok)' if 'ngrok' in entry.get(
                            'url', '') else 'LAN'
                        f.write(f"Mode: {mode}\n")
                        f.write(f"Downloads: {entry.get('downloads', 0)}\n")

                        if entry.get('files'):
                            f.write("Files shared:\n")
                            for file in entry['files']:
                                f.write(f"  • {file}\n")

                        f.write("\n" + "-" * 80 + "\n\n")

                messagebox.showinfo(
                    "✅ Exported!",
                    f"Analytics exported successfully!\n\n{filepath}"
                )

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def start_sharing(self):
        """Start the file sharing server"""
        if not self.files:
            messagebox.showerror("Error", "❌ Please select files first!")
            return

        # Check password
        password = None
        if self.password_var.get():
            password = self.password_entry.get().strip()
            if not password:
                messagebox.showerror(
                    "Error",
                    "❌ Please enter a password or uncheck password protection!"
                )
                return

        # Update UI
        self.status_label.config(text="🔄 Starting server...", fg='orange')
        self.start_btn.config(state='disabled')
        self.root.update()

        # Setup app data
        app_data['files'] = self.files
        app_data['password_hash'] = generate_password_hash(
            password) if password else None
        app_data['download_count'] = 0
        app_data['start_time'] = time.time()
        app_data['unique_ips'].clear()
        app_data['download_log'].clear()

        # Find free port
        self.port = self.find_free_port()

        # Start Flask server
        def run_flask():
            try:
                # CRITICAL: host='0.0.0.0' allows mobile devices on LAN to connect
                app.run(
                    host='0.0.0.0',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                print(f"Flask error: {e}")

        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        time.sleep(2)

        # Get local IP
        local_ip = self.get_local_ip()
        local_url = f"http://{local_ip}:{self.port}"

        # Build URL text
        url_text = "=" * 60 + "\n"
        url_text += "📱 LAN URL (Same WiFi Network):\n"
        url_text += f"{local_url}\n\n"
        url_text += "✅ Share with devices on same WiFi\n"
        url_text += "✅ Fast local network transfer\n"
        url_text += "✅ Works on phones, tablets, laptops\n"
        url_text += "=" * 60 + "\n\n"

        qr_url = local_url
        mode = "LAN"

        # Ngrok for internet access
        if not self.lan_only_var.get() and NGROK_OK:
            try:
                self.status_label.config(
                    text="🌐 Creating public tunnel...", fg='blue')
                self.root.update()

                self.ngrok_tunnel = ngrok.connect(self.port, "http")
                public_url = self.ngrok_tunnel.public_url

                url_text += "🌍 PUBLIC URL (Internet Access):\n"
                url_text += f"{public_url}\n\n"
                url_text += "✅ Works from anywhere in the world\n"
                url_text += "✅ No WiFi connection needed\n"
                url_text += "=" * 60 + "\n\n"

                qr_url = public_url
                mode = "Internet"

            except Exception as e:
                messagebox.showwarning(
                    "Ngrok Failed",
                    f"Internet mode failed:\n{e}\n\n"
                    "LAN mode is still working!"
                )

        if password:
            url_text += f"🔐 PASSWORD: {password}\n"
            url_text += "Browser will prompt for password\n"
            url_text += "=" * 60 + "\n\n"

        url_text += f"📦 SHARING {len(self.files)} FILE(S):\n"
        url_text += "-" * 60 + "\n"
        for file in self.files[:10]:
            size_mb = os.path.getsize(file) / (1024 * 1024)
            url_text += f"  📄 {os.path.basename(file)} ({size_mb:.2f} MB)\n"
        if len(self.files) > 10:
            url_text += f"  ... and {len(self.files) - 10} more files\n"

        url_text += "\n" + "=" * 60 + "\n"
        url_text += "💡 TROUBLESHOOTING:\n"
        url_text += "=" * 60 + "\n"
        url_text += "1. Both devices on SAME WiFi network\n"
        url_text += "2. Disable Windows Firewall temporarily\n"
        url_text += "3. Check router settings for device isolation\n"
        url_text += "4. Try typing URL manually if QR fails\n"

        # Update UI
        self.url_text.config(state='normal')
        self.url_text.delete('1.0', tk.END)
        self.url_text.insert('1.0', url_text)
        self.url_text.config(state='disabled')

        # Generate QR code
        self.generate_qr(qr_url)

        # Update status
        self.sharing = True
        self.status_label.config(text="✅ SHARING ACTIVE!", fg='#10b981')
        self.stop_btn.config(state='normal')

        # Start timer
        self.timer_thread = threading.Thread(
            target=self.timer_countdown, daemon=True)
        self.timer_thread.start()

        # Save history
        self.save_history(qr_url, mode)

        messagebox.showinfo(
            "✅ Success!",
            f"Sharing started successfully!\n\n"
            f"Your IP: {local_ip}\n"
            f"Port: {self.port}\n\n"
            f"📱 Scan QR or visit:\n{local_url}\n\n"
            f"⏰ Auto-stops in: {self.timer_var.get()} minutes"
        )

    def stop_sharing(self):
        """Stop the sharing server"""
        try:
            self.sharing = False
            self.exp_time = None

            # Clear app data
            app_data.update({
                'files': [],
                'password_hash': None,
                'download_count': 0
            })

            # Disconnect ngrok if active
            if self.ngrok_tunnel:
                try:
                    ngrok.disconnect(self.ngrok_tunnel.public_url)
                except:
                    pass

            # Update UI
            self.url_text.config(state='normal')
            self.url_text.delete('1.0', tk.END)
            self.url_text.insert(
                '1.0', "Sharing stopped. Click START to share again.")
            self.url_text.config(state='disabled')

            self.qr_label.config(
                image='', text="QR code will appear here", bg='#f0f0f0')
            self.timer_label.config(text="")
            self.status_label.config(text="⏹️ Stopped", fg='red')
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')

            messagebox.showinfo(
                "Stopped", "✅ File sharing stopped successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Error stopping server: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    gui_app = ShareFastGUI(root)

    def on_closing():
        """Handle window close"""
        if gui_app.sharing:
            if messagebox.askokcancel(
                "Quit",
                "Stop sharing and exit ShareFast Pro?"
            ):
                gui_app.stop_sharing()
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Show startup tips
    tips = (
        "💡 SHAREFAST PRO v5.1 - STARTUP TIPS\n\n"
        "✅ Both devices must be on SAME WiFi\n"
        "✅ Windows Firewall must allow Python\n"
        "✅ Phone should scan QR or type URL\n"
        "✅ Use LAN mode for faster speeds\n\n"
        "🔥 If phones can't connect:\n"
        "   → Disable Windows Firewall temporarily\n"
        "   → Or run as Administrator\n\n"
        "📊 Analytics tracks all transfers!\n"
        "🎨 Theme toggle in web interface!"
    )
    messagebox.showinfo("⚡ ShareFast Pro v5.1", tips)

    root.mainloop()


if __name__ == "__main__":
    main()
