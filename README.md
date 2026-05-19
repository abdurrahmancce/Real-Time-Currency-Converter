# 💱 Real-Time Currency Converter

A modern and professional **Real-Time Currency Converter** built with **Python Tkinter** and powered by live exchange rate APIs.  
This application features a beautiful UI, dark/light mode, animated buttons, conversion history, CSV export, and real-time currency conversion using multiple API fallbacks.

---

# 📌 Features

- 🌍 Real-time currency conversion
- 💹 Live exchange rates
- 🎨 Modern Tkinter GUI
- 🌙 Dark & Light mode toggle
- 📋 Conversion history tracking
- 📤 Export history to CSV
- 🔄 Currency swap feature
- ⚡ Fast API fallback system
- 🧠 Smart cross-rate calculation
- ⌨ Keyboard shortcuts support
- 📱 Responsive desktop UI
- 🃏 Card-style modern layout
- 📈 Live trend indicator (▲▼)
- 🔔 Input validation & error handling
- 🔄 Auto-refresh exchange rates

---

# 🖼️ Project Preview

## Light Mode
- Indigo → Violet gradient header
- Smooth UI cards
- Live conversion panel
- Conversion history section

## Dark Mode
- Professional dark theme
- Enhanced readability
- Modern purple gradients

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Tkinter | GUI Framework |
| Requests | API requests |
| CSV Module | Export conversion history |
| Threading | Background API fetching |
| ExchangeRate API | Live currency rates |

---

# 📂 Project Structure

```bash
📦 Real-Time-Currency-Converter
 ┣ 📜 main.py
 ┣ 📜 README.md
 ┗ 📂 screenshots
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/currency-converter.git
```

---

## 2️⃣ Navigate to Project Folder

```bash
cd currency-converter
```

---

## 3️⃣ Install Required Packages

```bash
pip install requests
```

---

# ▶️ Run The Application

```bash
python main.py
```

---

# 🌐 Supported Currencies

| Code | Currency |
|---|---|
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| BDT | Bangladeshi Taka |
| INR | Indian Rupee |
| JPY | Japanese Yen |
| CAD | Canadian Dollar |
| AUD | Australian Dollar |
| CHF | Swiss Franc |
| CNY | Chinese Yuan |
| SAR | Saudi Riyal |
| AED | UAE Dirham |
| SGD | Singapore Dollar |
| MYR | Malaysian Ringgit |
| NZD | New Zealand Dollar |
| KRW | South Korean Won |
| THB | Thai Baht |
| PKR | Pakistani Rupee |
| NOK | Norwegian Krone |
| SEK | Swedish Krona |

---

# 🧠 How It Works

The converter uses a cross-rate formula for accurate conversion:

```python
result = amount * (rate_to / rate_from)
```

This ensures:
- Faster conversion
- No repeated API requests
- Accurate exchange calculations

---

# 🔌 APIs Used

The app automatically switches between APIs if one fails.

```python
https://open.er-api.com/v6/latest/USD
https://api.exchangerate-api.com/v4/latest/USD
```

---

# 🎨 UI Components

## Header
- Gradient background
- Live status updates
- Theme toggle button

## Input Card
- Currency amount input
- Currency symbol preview
- Focus animations

## Currency Selector
- From/To dropdowns
- Swap button
- Live exchange rate pill

## Result Card
- Converted result display
- Real-time conversion details

## History Section
- Scrollable conversion history
- CSV export support

---

# ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Enter | Convert |
| Ctrl + W | Swap currencies |
| Ctrl + L | Clear fields |
| F5 | Refresh live rates |

---

# 📤 CSV Export

The application allows users to export conversion history into CSV format.

Example exported fields:

```csv
time,amount,from_currency,to_currency,result,rate
```

---

# 🔄 Auto Refresh

Exchange rates automatically refresh every:

```python
30 Minutes
```

---

# 🧩 Main Functionalities

## ✅ Live Rate Fetching
- Multi-API support
- Background thread fetching
- Automatic failover

## ✅ Smart Conversion
- Cross-rate conversion logic
- High precision formatting

## ✅ Theme System
- Light mode
- Dark mode
- Dynamic recoloring

## ✅ History Management
- Stores last 15 conversions
- Alternating row colors
- Scrollable listbox

---

# 📸 Recommended Screenshots

Light Mode : 

<img width="676" height="1012" alt="image" src="https://github.com/user-attachments/assets/dc6acb3c-dc0b-4c4f-b0c3-a17a3ef61ad3" />

Dark Mode :

<img width="685" height="992" alt="image" src="https://github.com/user-attachments/assets/525e19c8-be23-4afa-bbf9-789196ba67df" />

Conversion History :

<img width="675" height="1009" alt="image" src="https://github.com/user-attachments/assets/3b04507d-d04b-4124-83b6-857a008bfefe" />

 Export-CSV :
 
 <img width="839" height="88" alt="image" src="https://github.com/user-attachments/assets/95eeddcc-87fa-4468-8ba2-2b7bb94a46b3" />


---

# 🚀 Future Improvements

- 📊 Exchange rate charts
- 🌎 More currencies
- 🔔 Currency alerts
- 💾 Local database storage
- ☁ Cloud sync
- 📱 Mobile app version
- 🧮 Crypto currency support
- 🌐 Multi-language support

---

# 🛡️ Error Handling

The project includes:
- Input validation
- Internet connection checking
- API fallback support
- Safe threading
- User-friendly error messages

---

# 📈 Performance Optimizations

- Single API fetch strategy
- Cached USD rates
- Cross-rate calculations
- Background threading
- Lightweight UI rendering

---

# 🤝 Contributing

Contributions are welcome!

## Steps

1. Fork the repository

2. Create your feature branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Added new feature"
```

4. Push branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

```text
MIT License © 2026
```

---

# 👨‍💻 Author

## Abdur Rahman

- Python Developer
- GUI Application Enthusiast
- Open Source Learner

---

# ⭐ Support

If you like this project:

- ⭐ Star the repository
- 🍴 Fork the project
- 🐛 Report issues
- 💡 Suggest features

---

# 📬 Contact

```text
Email: akash.abdur.2002@gmail.com
GitHub: github.com/abdurrahmancce
LinkedIn: linkedin.com/in/abdur-rahman-akash-60450b2aa
```

---

# 🏁 Final Note

This project demonstrates:
- Modern Python GUI development
- API integration
- Real-time data handling
- Professional UI/UX design
- Threading and performance optimization

A perfect beginner-to-intermediate level Python desktop application project.
