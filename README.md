# ☀️ Solar Inverter Monitor & Alert System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Pushbullet](https://img.shields.io/badge/Pushbullet-API-green.svg)](https://www.pushbullet.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Junaid--Maqsood-brightgreen)](https://github.com/Junaid-Maqsood)

A powerful Python-based monitoring system that tracks your solar inverters in real-time and sends instant **Pushbullet notifications** when solar production drops below consumption. Perfect for optimizing solar usage and preventing unexpected grid draw!

**Created by [Junaid Maqsood](https://github.com/Junaid-Maqsood)**

---

## ✨ **Features**

| Feature | Description |
|---------|-------------|
| 🔍 **Real-time Monitoring** | Continuously monitors two solar inverters every 5 minutes |
| ⚡ **Load vs Solar Comparison** | Alerts when consumption exceeds production |
| 📱 **Pushbullet Notifications** | Instant alerts to your phone/desktop via channel |
| 🚨 **Error Detection** | Automatically detects and notifies about unhandled inverter errors |
| 🌙 **Solar Window Logic** | Only alerts during daylight hours (6:00 AM - 6:30 PM) |
| 🏠 **Multi-Device Support** | Monitors both Ground Floor and 1st Floor inverters |
| 🔔 **Smart Alerts** | Prevents duplicate notifications for same errors |
| ⏱️ **Persistent Monitoring** | Runs continuously with 5-minute check intervals |

---

## 🚀 **How It Works**

1. **Every 5 minutes**, the script:
   - Fetches real-time data from both inverters via API
   - Calculates total solar production (PV1 + PV2)
   - Reads current load consumption

2. **During solar window** (6 AM - 6:30 PM):
   - Compares load vs solar production
   - Sends alert if load > solar production

3. **Always monitors**:
   - Checks for unhandled inverter errors
   - Tracks which errors have already been reported
   - Sends notifications only for NEW errors

4. **Notifications sent via Pushbullet**:
   - Channel notifications for solar alerts (public/group)
   - Direct notifications for errors and API issues

---

## 📋 **Prerequisites**

- **Python 3.6** or higher
- **Pushbullet account** (free) with:
  - Access token
  - Channel (optional, for public alerts)
- **Internet connection** (to access inverter APIs)

---

## 🔧 **Installation**

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/Junaid-Maqsood/solar-load-monitor.git
cd solar-load-monitor
```

### **Step 2: Install Required Package**
```bash
pip install requests
```

### **Step 3: Configure Your Settings**

Edit `push_alert.py` and update these variables:

```python
# Your Pushbullet access token (get from https://www.pushbullet.com/#settings)
PUSHBULLET_TOKEN = 'your_token_here'

# Your Pushbullet channel tag (for public alerts)
CHANNEL_TAG = "your_channel_tag"

# Solar window timing (adjust for your location/season)
SOLAR_START = 6      # 6:00 AM
SOLAR_END = 18.5     # 6:30 PM
```

---

## ⚙️ **Configuration Details**

### **Pushbullet Setup**

1. **Get Access Token**:
   - Go to [pushbullet.com](https://www.pushbullet.com)
   - Sign in with your Google account
   - Click on **Settings** → **Account**
   - Click **"Create Access Token"**

2. **Create a Channel** (optional):
   - Go to [pushbullet.com/my-channel](https://www.pushbullet.com/my-channel)
   - Create a channel for public alerts
   - Copy the **Channel Tag**

### **Device Configuration**

The script is pre-configured for two inverters:

```python
DEVICES = [
    {"name": "1st Floor", 
     "sn": "96142411101312", 
     "pn": "W0051424410103", 
     "api": API_URL_1},
    
    {"name": "Ground Floor", 
     "sn": "96142411100536", 
     "pn": "W0036398935471", 
     "api": API_URL_2},
]
```

To add more devices, simply extend this list with your own API URLs.

---

## 🏃 **Running the Monitor**

### **Test Run**
```bash
python push_alert.py
```

### **Run Continuously**
```bash
# Using nohup (Linux/Mac)
nohup python push_alert.py &

# Using pythonw (Windows - runs in background)
pythonw push_alert.py

# Using screen (Linux/Mac - more control)
screen -S solar-monitor
python push_alert.py
# Press Ctrl+A then D to detach
```

### **Auto-start on Boot (Linux - systemd)**

Create a service file:
```bash
sudo nano /etc/systemd/system/solar-monitor.service
```

Add:
```ini
[Unit]
Description=Solar Inverter Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/solar-load-monitor/push_alert.py
WorkingDirectory=/path/to/solar-load-monitor
Restart=always
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable solar-monitor
sudo systemctl start solar-monitor
```

---

## 📊 **Notification Examples**

### **Solar Alert** (sent to channel)
```
⚡ Ground Floor Solar Alert

Solar: 850W
Load: 1200W

⚡ Reduce your Load!
```

### **Error Alert** (sent directly)
```
⚠ 1st Floor Error

Ground Floor has new error(s):
Inverter over temperature
Battery low voltage
```

### **API Error** (sent directly)
```
⚠ API Error

⚠ API error: HTTP 500
```

---

## 🔍 **How It Monitors**

### **Data Fetching**
- Uses DESS Monitor API to get real-time inverter data
- Extracts:
  - `bt_inputpower_1` - First PV input
  - `bt_inp_power_2` - Second PV input
  - `bt_load_active_power_sole` - Current load

### **Solar Window Logic**
```python
# Only alerts between 6:00 AM and 6:30 PM
if 6.0 <= current_hour <= 18.5:
    check_solar_vs_load()
```

### **Error Tracking**
- Maintains set of previously reported error IDs
- Only alerts for NEW unhandled errors
- Prevents notification spam

---

## 📁 **Project Structure**

```
solar-load-monitor/
├── 📄 push_alert.py          # Main monitoring script
├── 📄 README.md              # This documentation
└── 📄 requirements.txt       # Python dependencies (optional)
```

---

## 🛠️ **Technical Details**

### **Dependencies**
- `requests` - For API calls to inverter and Pushbullet

### **APIs Used**

| API | Purpose |
|-----|---------|
| **DESS Monitor API** | Fetch solar inverter data |
| **Pushbullet API** | Send notifications |

### **Key Functions**

| Function | Description |
|----------|-------------|
| `get_inverter_data()` | Fetches PV and load from inverter |
| `check_unhandled_errors()` | Monitors for inverter errors |
| `is_solar_window()` | Checks if current time is within solar hours |
| `send_notification_to_channel()` | Sends public alerts to Pushbullet channel |
| `send_notification_to_self()` | Sends private error notifications |

---

## 🤝 **Contributing**

Contributions are welcome! Here's how you can help:

### **Report Bugs**
- Open an [Issue](https://github.com/Junaid-Maqsood/solar-load-monitor/issues)
- Describe the bug and how to reproduce it

### **Suggest Features**
- Open an [Issue](https://github.com/Junaid-Maqsood/solar-load-monitor/issues)
- Label it as "enhancement"
- Describe your idea clearly

### **Submit Code**
1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a [Pull Request](https://github.com/Junaid-Maqsood/solar-load-monitor/pulls)

---

## 📝 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Junaid Maqsood

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 **Acknowledgments**

- **Pushbullet** - For excellent notification API
- **DESS Monitor** - For solar inverter API access
- All **contributors** and **users** who support this project

---

## 📧 **Connect with Me**

**Junaid Maqsood**

- **GitHub**: [@Junaid-Maqsood](https://github.com/Junaid-Maqsood)
- **LinkedIn**: [junaidmksud](https://www.linkedin.com/in/junaidmksud/)
- **Project Repository**: [solar-load-monitor](https://github.com/Junaid-Maqsood/solar-load-monitor)

---

## ⭐ **Support**

If this project helps you:
- ⭐ **Star** the repository on [GitHub](https://github.com/Junaid-Maqsood/solar-load-monitor)
- 📢 **Share** it with others
- 🐛 **Report** issues you find
- 💡 **Suggest** improvements
- 🔗 **Connect** with me on [LinkedIn](https://www.linkedin.com/in/junaidmksud/)
