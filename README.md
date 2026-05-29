# SNI Spoof - Linux GUI
A small PySide6 desktop UI for running the **sni-spoof** core binary on Linux.

<br>

## ✨ Features
- Start/stop the core binary from a GUI
- Edit and persist core configuration
- Live log output with clear/reset
- Status indicators for core/config presence

<br>

## ⚙️ Requirements
- Linux (arm64, amd64)
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
Point your client (xray, etc.) at `LISTEN_HOST:LISTEN_PORT` instead of the real upstream.

<br>

## 🚀 Quick Start
- **Download:** Grab the archive from our [Releases](https://github.com/Vauth/sni-spoof-linux-gui/releases) .
- **Connect:** Extract, Launch `sni-spoof-gui` and hit the Start Core button.

<br>

## 📷 Screenshot
<a href="#Screenshot"><img src="https://github.com/user-attachments/assets/33039128-00e5-4e75-bf8e-7b78744db0ff" width="600px"></a>

<br>

## 🧪 Troubleshooting
- **Core binary missing**: Ensure `sni-spoof-linux-<arch>` is in the same directory and is executable.
- **No permission to start**: Verify `pkexec` is available (`policykit-1` package) and that you approve the prompt.
- **Config not loading**: Delete `config.json` to restore defaults.

<br>

## 🔗 Contributing
Contributions are welcome! Feel free to submit a pull request or report an issue.

<br>

## 🔎 License
```
MIT License

Copyright (c) 2026 Vauth

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
