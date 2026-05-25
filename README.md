# SNI Spoof - Linux GUI
A small PySide6 desktop UI for running the **sni-spoof** core binary on Linux.

<br>

## 🔎 Features
- Start/stop the core binary from a GUI
- Edit and persist core configuration
- Live log output with clear/reset
- Status indicators for core/config presence

<br>

## ⚙️ Requirements
- Python 3.10+
- Core binary

<br>

## 📚 Configuration
Configuration is stored in `config.json` in the same directory. If the file is missing or invalid, defaults are used and the file is created on first save.

**Default values:**
```json
{
  "LISTEN_HOST": "0.0.0.0",
  "LISTEN_PORT": 40443,
  "CONNECT_IP": "104.19.229.21",
  "CONNECT_PORT": 443,
  "FAKE_SNI": "www.hcaptcha.com"
}
```

<br>

## 🚀 Quick Start
- **Download:** Grab the archive from our [Releases](https://github.com/Vauth/sni-spoof-linux-gui/releases) .
- **Connect:** Extract, Launch `sni-spoof-gui` and hit the Start Core button.

<br>

## 🧪 Troubleshooting
- **Core binary missing**: Ensure `sni-spoof-linux-<arch>` is in the same directory and is executable.
- **No permission to start**: Verify `pkexec` is available (`policykit-1` package) and that you approve the prompt.
- **Config not loading**: Delete `config.json` to restore defaults.
