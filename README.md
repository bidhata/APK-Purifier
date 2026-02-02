# APK Purifier

A cross-platform desktop application for Windows and Linux that purifies Android APK files by removing advertisements and basic malware, then generates signed APKs ready for installation.

**Made by:** Krishnendu Paul  
**Website:** https://krishnendu.com  
**GitHub:** https://github.com/bidhata/APK-Purifier  
**Contact:** me@krishnendu.com

## 📸 Screenshots

### Main Interface
![APK Purifier Main Window](screenshots/main-window.png)

### Processing in Action
![APK Processing](screenshots/processing.png)

### Settings Dialog
![Settings Configuration](screenshots/settings.png)

## ✨ Features

- **🎯 Ad Removal**: Remove advertisements using multiple detection methods
- **🛡️ Malware Detection**: Basic malware pattern detection and removal
- **✍️ APK Signing**: Automatically sign patched APKs for installation
- **🔄 Dual Decompiler Support**: Uses APKTool and JADX for maximum compatibility
- **🖥️ Cross-Platform**: Works on Windows and Linux
- **🎨 GUI Interface**: User-friendly desktop interface
- **📦 Batch Processing**: Process multiple APKs at once
- **💾 Backup**: Automatic backup of original APKs

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Java 8 or higher (for APKTool, JADX, and signing tools)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bidhata/APK-Purifier.git
cd APK-Purifier
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Download required tools**
```bash
python download_tools.py
```

4. **Run the application**
```bash
python src/main.py
```

### Alternative: CLI Usage
```bash
python src/cli.py --help
```

## 🛠️ Technology Stack

- **Python 3.8+**: Core application logic
- **PyQt6**: Cross-platform GUI framework
- **APKTool**: Primary APK decompilation and recompilation
- **JADX**: Alternative decompiler for better compatibility
- **uber-apk-signer**: APK signing with v1/v2/v3 schemes

## 📋 Usage

1. **Launch APK Purifier**: Run `python src/main.py`
2. **Add APK Files**: Click "Add APK Files" to select APKs for processing
3. **Configure Options**:
   - Choose ad removal methods
   - Enable/disable malware scanning
   - Configure decompiler preferences
4. **Start Processing**: Click "Start Patching" to begin purification
5. **Get Results**: Processed APKs will be saved with `_patched_signed.apk` suffix

## ⚙️ Configuration Options

### Ad Removal Methods
- **Domain Replacement**: Replace ad domains with invalid ones
- **Class Removal**: Remove ad-related Java classes
- **Manifest Cleanup**: Remove ad permissions and components
- **Resource Cleanup**: Remove ad-related layouts and drawables

### Decompiler Options
- **Use JADX as fallback**: Automatically tries JADX if APKTool fails
- **Prefer JADX for analysis**: Use JADX for analysis-only operations

## 🧪 Testing

Run the installation test to verify everything is working:
```bash
python test_installation.py
```

## 📁 Project Structure

```
apk-purifier/
├── src/
│   ├── core/
│   │   ├── apk_analyzer.py      # APK analysis and decompilation
│   │   ├── jadx_analyzer.py     # JADX decompiler integration
│   │   ├── ad_patcher.py        # Ad removal logic
│   │   ├── malware_scanner.py   # Basic malware detection
│   │   ├── apk_signer.py        # APK signing and alignment
│   │   └── utils.py             # Utility functions
│   ├── gui/
│   │   ├── main_window.py       # Main GUI window
│   │   ├── progress_dialog.py   # Progress tracking
│   │   └── settings_dialog.py   # Configuration settings
│   ├── data/
│   │   ├── ad_domains.txt       # Known ad domains
│   │   ├── ad_classes.txt       # Ad class patterns
│   │   ├── malware_patterns.txt # Malware signatures
│   │   └── suspicious_permissions.txt
│   ├── cli.py                   # Command-line interface
│   └── main.py                  # Application entry point
├── tools/                       # External tools (downloaded)
├── requirements.txt
├── setup.py
├── download_tools.py
├── test_installation.py
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with applicable laws and terms of service. The authors are not responsible for any misuse of this software.

## 🆘 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/bidhata/APK-Purifier/issues)
- **Documentation**: Check [INSTALL.md](INSTALL.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Contact**: me@krishnendu.com

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes and improvements.