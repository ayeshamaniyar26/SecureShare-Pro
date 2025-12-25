# ⚡ ShareFast Pro v5.1

**Professional File Sharing Application** - Perfect for Resume & Portfolio

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

## 🌟 Features

- **📱 Mobile-Optimized** - Beautiful, responsive web interface
- **🏠 LAN Mode** - Lightning-fast local network sharing
- **🌍 Internet Mode** - Share with anyone, anywhere (via Ngrok)
- **🔐 Password Protection** - Secure your shared files
- **📊 Analytics Dashboard** - Track transfers and downloads
- **🎨 Dark/Light Theme** - Toggle in web interface
- **⏰ Auto-Stop Timer** - Automatic shutdown after set duration
- **📱 QR Code** - Quick mobile access
- **🔥 Auto Firewall Config** - Windows Firewall setup (Admin)

## 📸 Screenshots

### Desktop Application

![ShareFast Desktop](https://via.placeholder.com/800x600/667eea/ffffff?text=ShareFast+Desktop+App)

### Mobile Download Page

![ShareFast Mobile](https://via.placeholder.com/400x800/764ba2/ffffff?text=Mobile+Download+Page)

### Analytics Dashboard

![Analytics](https://via.placeholder.com/800x600/10b981/ffffff?text=Analytics+Dashboard)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/sharefast-pro.git
cd sharefast-pro

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Requirements

```
flask>=3.0.0
pillow>=10.0.0
qrcode>=7.4.2
werkzeug>=3.0.0
pyngrok>=6.0.0  # Optional, for internet mode
```

## 💡 Usage

1. **Select Files** - Choose files or entire folders
2. **Configure** - Set password, timer, and mode (LAN/Internet)
3. **Start Sharing** - Click "START SHARING"
4. **Share Link** - Send URL or QR code to recipients
5. **Download** - Recipients access files via web browser

### LAN Mode (Recommended)

- Both devices on same WiFi
- Fast local transfer
- No internet required
- URL: `http://YOUR_IP:5000`

### Internet Mode (Ngrok)

- Works from anywhere
- Requires internet
- Public URL provided

## 🔧 Troubleshooting

### Phone Can't Connect?

1. **Check WiFi** - Both devices on SAME network
2. **Disable Firewall** - Temporarily disable Windows Firewall
3. **Run as Admin** - For automatic firewall configuration
4. **Check Router** - Disable AP/Client isolation

### Firewall Configuration

**Windows (Automatic):**

```
Run as Administrator → Allow firewall exception
```

**Windows (Manual):**

1. Windows Security → Firewall
2. Allow an app → Add Python
3. Path: `C:\Users\...\python.exe`

## 📊 Analytics

Track all transfers with comprehensive analytics:

- Total transfers and downloads
- Data shared (GB)
- Transfer history with timestamps
- Export reports

## 🎨 Web Interface

Beautiful, mobile-optimized design:

- Dark/Light theme toggle
- Animated transitions
- Touch-friendly buttons
- Responsive layout
- File previews with icons

## 🔐 Security

- Password protection (bcrypt hashing)
- Session-based authentication
- No file storage on server
- Auto-stop timer
- Local network isolation (LAN mode)

## 📱 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Tkinter (Desktop)
- **Networking**: Socket, Ngrok
- **Security**: Werkzeug, Sessions
- **QR**: qrcode, PIL

## 🎯 Project Structure

```
sharefast-pro/
│
├── main.py                 # Main application
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── LICENSE                # MIT License
├── sharefast_history.json # Analytics data (auto-generated)
│
└── screenshots/           # App screenshots
    ├── desktop.png
    ├── mobile.png
    └── analytics.png
```

## 👨‍💻 Author

**AYESHA MANIYAR**

- GitHub: [ayeshamaniyar26](https://github.com/ayeshamaniyar26)
- LinkedIn: [Ayesha Maniyar](https://www.linkedin.com/in/ayesha-maniyar-6771692a5)
  -Email: ayeshamaniyar2601@gmail.com

## 🙏 Acknowledgments

- Flask for the amazing web framework
- Ngrok for public URL tunneling
- Python community for excellent libraries

## ⭐ Star This Repository!

If you find this project useful, please give it a star! It helps others discover the project.

---

**Made with ❤️ for the developer community**
