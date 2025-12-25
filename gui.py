"""
Complete GUI for SecureShare Pro - FINAL VERSION
Copy this ENTIRE file and replace your gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime, timedelta
import webbrowser
from pathlib import Path

import config
import utils
from server import FileServer
from tunnel import TunnelManager


class SecureShareGUI:
    """Main GUI application with all features"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{config.APP_NAME} v{config.VERSION}")
        self.root.geometry("700x600")  # Fixed size

        # State variables
        self.selected_path = None
        self.server = None
        self.tunnel_manager = None
        self.dark_mode = False
        self.current_theme = config.THEME_LIGHT
        self.timer_thread = None
        self.expiration_time = None
        self.password = tk.StringVar()
        self.port = tk.IntVar(value=config.DEFAULT_PORT)
        self.expiration_minutes = tk.IntVar(
            value=config.DEFAULT_EXPIRATION_MINUTES)
        self.use_lan_only = tk.BooleanVar(value=True)  # LAN mode by default
        self.current_url = None

        # Setup GUI
        self.setup_ui()
        self.apply_theme()

        # Start bandwidth monitor
        self.start_bandwidth_monitor()

    def setup_ui(self):
        """Setup the complete user interface"""
        # Create main scrollable canvas
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(
            self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = scrollable_frame
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== HEADER =====
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = tk.Label(
            header_frame,
            text=config.APP_NAME,
            font=('Arial', 24, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # Help button
        help_btn = tk.Button(
            header_frame,
            text="❓ How to Share",
            command=self.show_instructions,
            font=('Arial', 10),
            bg='#4CAF50',
            fg='white'
        )
        help_btn.pack(side=tk.RIGHT, padx=5)

        # History button
        history_btn = tk.Button(
            header_frame,
            text="📋 History",
            command=self.show_history,
            font=('Arial', 10)
        )
        history_btn.pack(side=tk.RIGHT, padx=5)

        # Theme toggle button
        self.theme_btn = tk.Button(
            header_frame,
            text="🌙 Dark",
            command=self.toggle_theme,
            font=('Arial', 10)
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        # ===== FILE SELECTION =====
        selection_frame = tk.LabelFrame(main_frame, text="📁 File Selection", font=(
            'Arial', 12, 'bold'), padx=10, pady=10)
        selection_frame.pack(fill=tk.X, pady=10)

        # File selection info
        info_label = tk.Label(
            selection_frame,
            text="Select a file or folder to share",
            font=('Arial', 11),
            fg='gray'
        )
        info_label.pack(pady=5)

        # Selection buttons
        btn_frame = tk.Frame(selection_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            btn_frame,
            text="📄 Select File",
            command=self.select_file,
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='white',
            height=2,
            width=20
        ).pack(side=tk.LEFT, padx=10, expand=True)

        tk.Button(
            btn_frame,
            text="📂 Select Folder",
            command=self.select_folder,
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='white',
            height=2,
            width=20
        ).pack(side=tk.LEFT, padx=10, expand=True)

        # Selected path display with frame
        path_display_frame = tk.Frame(
            selection_frame, relief=tk.SUNKEN, borderwidth=1, bg='#f5f5f5')
        path_display_frame.pack(fill=tk.X, pady=5)

        self.path_label = tk.Label(
            path_display_frame,
            text="No file/folder selected",
            font=('Arial', 10),
            fg='gray',
            bg='#f5f5f5',
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        self.path_label.pack(fill=tk.X)

        # ===== SETTINGS =====
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ Settings", font=(
            'Arial', 12, 'bold'), padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=10)

        # Port selection
        port_frame = tk.Frame(settings_frame)
        port_frame.pack(fill=tk.X, pady=5)
        tk.Label(port_frame, text="Port:", font=(
            'Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Spinbox(
            port_frame,
            from_=8000,
            to=9000,
            textvariable=self.port,
            width=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)

        # LAN only mode
        tk.Checkbutton(
            port_frame,
            text="🏠 LAN Only (Same WiFi - Recommended)",
            variable=self.use_lan_only,
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=20)

        # Password protection
        pass_frame = tk.Frame(settings_frame)
        pass_frame.pack(fill=tk.X, pady=5)
        tk.Label(pass_frame, text="🔒 Password (Optional):",
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Entry(
            pass_frame,
            textvariable=self.password,
            show="*",
            width=20,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)

        # Expiration timer
        timer_frame = tk.Frame(settings_frame)
        timer_frame.pack(fill=tk.X, pady=5)
        tk.Label(timer_frame, text="⏰ Auto-close after:",
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        tk.Spinbox(
            timer_frame,
            from_=5,
            to=180,
            textvariable=self.expiration_minutes,
            width=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=10)
        tk.Label(timer_frame, text="minutes", font=(
            'Arial', 10)).pack(side=tk.LEFT)

        # ===== CONTROL BUTTONS =====
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=15)

        self.start_btn = tk.Button(
            control_frame,
            text="🚀 START SHARING",
            command=self.start_sharing,
            font=('Arial', 14, 'bold'),
            bg='#4CAF50',
            fg='white',
            height=2,
            width=25,
            cursor='hand2'
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.stop_btn = tk.Button(
            control_frame,
            text="🛑 STOP SHARING",
            command=self.stop_sharing,
            font=('Arial', 14, 'bold'),
            bg='#f44336',
            fg='white',
            height=2,
            width=25,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True)

        # ===== STATUS & URL DISPLAY =====
        status_frame = tk.LabelFrame(main_frame, text="📡 Sharing Status", font=(
            'Arial', 12, 'bold'), padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Status label
        self.status_label = tk.Label(
            status_frame,
            text="⚫ Ready to share",
            font=('Arial', 14, 'bold'),
            fg='gray'
        )
        self.status_label.pack(pady=10)

        # Timer display
        self.timer_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 11, 'bold'),
            fg='orange'
        )
        self.timer_label.pack(pady=5)

        # URL display
        url_container = tk.Frame(status_frame)
        url_container.pack(fill=tk.X, pady=10)

        tk.Label(url_container, text="📤 Share this URL:", font=(
            'Arial', 11, 'bold')).pack(anchor=tk.W, pady=5)

        self.url_text = scrolledtext.ScrolledText(
            url_container,
            height=3,
            font=('Courier', 10, 'bold'),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#f5f5f5',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.url_text.pack(fill=tk.X, pady=5)

        # URL action buttons
        url_btn_frame = tk.Frame(url_container)
        url_btn_frame.pack(fill=tk.X, pady=10)

        self.copy_btn = tk.Button(
            url_btn_frame,
            text="📋 Copy URL",
            command=self.copy_url,
            state=tk.DISABLED,
            font=('Arial', 11, 'bold'),
            bg='#2196F3',
            fg='white',
            height=1,
            cursor='hand2'
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.open_btn = tk.Button(
            url_btn_frame,
            text="🌐 Open in Browser",
            command=self.open_url,
            state=tk.DISABLED,
            font=('Arial', 11, 'bold'),
            bg='#FF9800',
            fg='white',
            height=1,
            cursor='hand2'
        )
        self.open_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # QR Code display
        qr_container = tk.Frame(status_frame)
        qr_container.pack(pady=10)

        tk.Label(qr_container, text="📱 Scan QR Code:",
                 font=('Arial', 11, 'bold')).pack()

        self.qr_frame = tk.Frame(
            qr_container, relief=tk.SUNKEN, borderwidth=2, bg='white', width=220, height=220)
        self.qr_frame.pack(pady=10)
        self.qr_frame.pack_propagate(False)

        self.qr_label = tk.Label(
            self.qr_frame, text="QR code will appear here", bg='white', fg='gray')
        self.qr_label.pack(expand=True)

        # ===== BANDWIDTH MONITOR =====
        bandwidth_frame = tk.LabelFrame(
            main_frame, text="📊 Real-time Bandwidth Monitor", font=('Arial', 11, 'bold'), padx=10, pady=10)
        bandwidth_frame.pack(fill=tk.X, pady=10)

        self.bandwidth_label = tk.Label(
            bandwidth_frame,
            text="⬇️ Download: 0 B/s | ⬆️ Upload: 0 B/s | 📦 Total: 0 B",
            font=('Arial', 11, 'bold'),
            fg='blue',
            pady=10
        )
        self.bandwidth_label.pack()

    def select_file(self):
        """Select a file to share"""
        filepath = filedialog.askopenfilename(
            title="Select File to Share",
            filetypes=[("All Files", "*.*")]
        )
        if filepath:
            self.selected_path = filepath
            self.update_path_display()

    def select_folder(self):
        """Select a folder to share"""
        folderpath = filedialog.askdirectory(title="Select Folder to Share")
        if folderpath:
            self.selected_path = folderpath
            self.update_path_display()

    def update_path_display(self):
        """Update the path display label"""
        if self.selected_path:
            path = Path(self.selected_path)
            size = utils.format_bytes(utils.get_file_size(path))
            file_count = utils.get_file_count(path)

            if path.is_file():
                info = f"✅ Selected File: {path.name}\n📏 Size: {size}"
            else:
                info = f"✅ Selected Folder: {path.name}\n📁 Files: {file_count} | 📏 Total Size: {size}"

            self.path_label.config(text=info, fg='green',
                                   font=('Arial', 11, 'bold'))

    def start_sharing(self):
        """Start the file sharing server"""
        if not self.selected_path:
            messagebox.showwarning(
                "No Selection", "⚠️ Please select a file or folder to share first!")
            return

        if not Path(self.selected_path).exists():
            messagebox.showerror(
                "File Not Found", "❌ The selected file/folder no longer exists!")
            return

        # Disable start button immediately
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="⏳ Starting server...", fg='orange')
        self.root.update()

        # Find free port
        port = utils.find_free_port(self.port.get())
        if not port:
            messagebox.showerror(
                "Port Error", "❌ Could not find an available port!")
            self.start_btn.config(state=tk.NORMAL)
            self.status_label.config(text="⚫ Ready to share", fg='gray')
            return

        self.port.set(port)

        # Start server
        password = self.password.get() if self.password.get() else None
        self.server = FileServer(
            self.selected_path,
            port,
            password=password,
            activity_callback=self.log_activity
        )

        if not self.server.start():
            messagebox.showerror(
                "Server Error", "❌ Failed to start server!\n\nPlease try a different port.")
            self.start_btn.config(state=tk.NORMAL)
            self.status_label.config(text="⚫ Ready to share", fg='gray')
            return

        # Small delay to ensure server is ready
        time.sleep(0.5)

        # Generate URL
        local_ip = utils.get_local_ip()
        local_url = f"http://{local_ip}:{port}"

        if self.use_lan_only.get():
            # LAN only mode
            self.current_url = local_url
            self.display_url(local_url, "LAN")
            mode = "LAN"
        else:
            # Internet mode with ngrok
            self.status_label.config(
                text="⏳ Creating public URL...", fg='orange')
            self.root.update()

            self.tunnel_manager = TunnelManager(port)
            public_url = self.tunnel_manager.start_tunnel()

            if not public_url:
                messagebox.showerror(
                    "Tunnel Error",
                    "❌ Failed to create public URL!\n\n" +
                    "Possible reasons:\n" +
                    "• No internet connection\n" +
                    "• Ngrok service unavailable\n\n" +
                    "✅ TIP: Use LAN-only mode instead!\n" +
                    "(Check the 'LAN Only' box)"
                )
                self.server.stop()
                self.start_btn.config(state=tk.NORMAL)
                self.status_label.config(text="⚫ Ready to share", fg='gray')
                return

            self.current_url = public_url
            display_text = f"🌐 Public URL:\n{public_url}\n\n🏠 Local URL:\n{local_url}"
            self.display_url(display_text, "Internet")
            mode = "Internet"

        # Save to history
        utils.save_transfer_history(self.selected_path, self.current_url, mode)

        # Update UI
        self.status_label.config(text="🟢 Sharing Active!", fg='green')
        self.stop_btn.config(state=tk.NORMAL)
        self.copy_btn.config(state=tk.NORMAL)
        self.open_btn.config(state=tk.NORMAL)

        # Start expiration timer
        self.start_expiration_timer()

        # Success message
        success_msg = f"✅ Sharing started successfully!\n\n"
        success_msg += f"🌐 Mode: {mode}\n"
        success_msg += f"📡 Port: {port}\n"
        success_msg += f"📂 Sharing: {Path(self.selected_path).name}"
        if password:
            success_msg += f"\n🔒 Password protected"

        if mode == "LAN":
            success_msg += f"\n\n💡 TIP: Send URL via WhatsApp to share!"

        messagebox.showinfo("Success!", success_msg)

    def stop_sharing(self):
        """Stop the file sharing server"""
        if self.server:
            self.server.stop()
            self.server = None

        if self.tunnel_manager:
            self.tunnel_manager.stop_tunnel()
            self.tunnel_manager = None

        self.current_url = None

        # Update UI
        self.status_label.config(text="⚫ Sharing Stopped", fg='gray')
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.timer_label.config(text="")

        self.url_text.config(state=tk.NORMAL)
        self.url_text.delete(1.0, tk.END)
        self.url_text.config(state=tk.DISABLED)

        # Clear QR code
        for widget in self.qr_frame.winfo_children():
            widget.destroy()
        self.qr_label = tk.Label(
            self.qr_frame, text="QR code will appear here", bg='white', fg='gray')
        self.qr_label.pack(expand=True)

        messagebox.showinfo("Stopped", "🛑 File sharing stopped successfully!")

    def display_url(self, url, mode):
        """Display the sharing URL and QR code"""
        self.url_text.config(state=tk.NORMAL)
        self.url_text.delete(1.0, tk.END)
        self.url_text.insert(1.0, url)
        self.url_text.config(state=tk.DISABLED)

        # Generate and display QR code
        primary_url = url.split('\n')[0] if '\n' in url else url
        # Remove any emoji or extra text
        qr_url = primary_url.replace('🌐 Public URL:', '').replace(
            '🏠 Local URL:', '').strip()

        try:
            qr_img = utils.generate_qr_code(qr_url, size=200)
            qr_photo = ImageTk.PhotoImage(qr_img)

            # Clear old widgets
            for widget in self.qr_frame.winfo_children():
                widget.destroy()

            # Display new QR code
            self.qr_label = tk.Label(self.qr_frame, image=qr_photo, bg='white')
            self.qr_label.image = qr_photo  # Keep a reference
            self.qr_label.pack(expand=True)
        except Exception as e:
            print(f"Error generating QR code: {e}")
            messagebox.showwarning(
                "QR Code Error", f"Could not generate QR code: {e}")

    def copy_url(self):
        """Copy URL to clipboard"""
        if self.current_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_url)
            self.root.update()
            messagebox.showinfo(
                "Copied!", "✅ URL copied to clipboard!\n\nNow paste it in WhatsApp or any messenger!")

    def open_url(self):
        """Open URL in browser"""
        if self.current_url:
            webbrowser.open(self.current_url)

    def start_expiration_timer(self):
        """Start countdown timer for auto-close"""
        self.expiration_time = datetime.now() + timedelta(minutes=self.expiration_minutes.get())

        def update_timer():
            while self.server and self.expiration_time:
                remaining = self.expiration_time - datetime.now()
                if remaining.total_seconds() <= 0:
                    self.root.after(0, self.stop_sharing)
                    break

                time_str = utils.format_time(remaining.total_seconds())
                self.root.after(0, lambda: self.timer_label.config(
                    text=f"⏰ Auto-close in: {time_str}"
                ))
                time.sleep(1)

        self.timer_thread = threading.Thread(target=update_timer, daemon=True)
        self.timer_thread.start()

    def start_bandwidth_monitor(self):
        """Start monitoring bandwidth usage"""
        def monitor():
            while True:
                if self.server:
                    stats = self.server.get_bandwidth_stats()
                    download_speed = utils.format_bytes(
                        stats['download_speed']) + '/s'
                    upload_speed = utils.format_bytes(
                        stats['upload_speed']) + '/s'
                    total = utils.format_bytes(
                        stats['download_bytes'] + stats['upload_bytes'])

                    text = f"⬇️ Download: {download_speed} | ⬆️ Upload: {upload_speed} | 📦 Total: {total}"
                    self.root.after(
                        0, lambda t=text: self.bandwidth_label.config(text=t))

                time.sleep(1)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def log_activity(self, method, path):
        """Log server activity"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {method} {path}")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.current_theme = config.THEME_DARK if self.dark_mode else config.THEME_LIGHT
        self.apply_theme()
        self.theme_btn.config(text="☀️ Light" if self.dark_mode else "🌙 Dark")

    def apply_theme(self):
        """Apply the current theme"""
        self.root.config(bg=self.current_theme['bg'])

    def show_history(self):
        """Show transfer history in a new window"""
        history = utils.load_transfer_history()

        if not history:
            messagebox.showinfo("History", "📋 No transfer history found")
            return

        # Create history window
        hist_window = tk.Toplevel(self.root)
        hist_window.title("Transfer History")
        hist_window.geometry("750x450")

        # Create treeview
        tree = ttk.Treeview(hist_window, columns=(
            'Time', 'File', 'Mode', 'Size'), show='headings')
        tree.heading('Time', text='Timestamp')
        tree.heading('File', text='File/Folder')
        tree.heading('Mode', text='Mode')
        tree.heading('Size', text='Size')

        tree.column('Time', width=150)
        tree.column('File', width=350)
        tree.column('Mode', width=100)
        tree.column('Size', width=100)

        for entry in reversed(history[-50:]):  # Show last 50
            try:
                timestamp = datetime.fromisoformat(
                    entry['timestamp']).strftime('%Y-%m-%d %H:%M')
                filename = Path(entry['file_path']).name
                size = utils.format_bytes(entry['size'])
                tree.insert('', 0, values=(
                    timestamp, filename, entry['mode'], size))
            except:
                pass

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            hist_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def show_instructions(self):
        """Show how to share instructions"""
        instructions = """
🎯 HOW TO SHARE FILES - Step by Step Guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 QUICK TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ LAN mode = FASTER, no internet needed
✅ Works for: Photos, videos, documents, any file!
✅ Password protection = Optional security
✅ Auto-closes after 30 minutes (configurable)

🔴 ALWAYS CLICK "STOP SHARING" WHEN DONE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        # Create instructions window
        inst_window = tk.Toplevel(self.root)
        inst_window.title("📖 How to Share Files")
        inst_window.geometry("650x700")

        # Add scrolled text
        text = scrolledtext.ScrolledText(
            inst_window,
            font=('Courier', 9),
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(1.0, instructions)
        text.config(state=tk.DISABLED)

        # Close button
        tk.Button(
            inst_window,
            text="✅ Got it!",
            command=inst_window.destroy,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            height=2
        ).pack(pady=10, fill=tk.X, padx=20)

    def on_closing(self):
        """Handle window close event"""
        if self.server:
            if messagebox.askokcancel("Quit", "⚠️ Stop sharing and close application?"):
                self.stop_sharing()
                self.root.destroy()
        else:
            self.root.destroy()
