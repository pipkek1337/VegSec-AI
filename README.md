# VegSecAI 🥕  
A secure AI-driven system for vegetable image classification, integrating cybersecurity measures to ensure reliable and efficient data handling.  
*Note: Some documentation and comments are in Hebrew.*

---

## 🔧 Getting Started  
This repository contains **only the code**.

To run the system, follow the instructions for both server and client setup.

---

## 🖥️ Server Requirements

### Prerequisites:
- [Ollama](https://ollama.com/)
- [Moondream v2](https://ollama.com/library/moondream:v2)

### Install Python dependencies:
First, install the necessary Python packages:

```bash
pip install bcrypt cryptography python-dotenv pillow transformers torch moondream
```

### Setup Instructions:
1. Install and run **Moondream** using Ollama.
2. Place the provided server-side scripts where needed.
3. Launch the server process.  
   > ⚠️ The server currently supports **LAN connections only**.

---

## 💻 Client Requirements

### Install Python dependencies:
First, install the necessary Python packages:

```bash
pip install pillow opencv-python
```

Once dependencies are installed and the server is running, the client can connect over the LAN and start classifying vegetable images.

---

## 📜 License
[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)  
You are free to use, modify, and distribute this code **as long as any derivative works remain open-source** under the same license.

