# 🌿 Ecotrack — Aplikacja do monitorowania i redukcji emisji CO₂

**Ecotrack** to pełnoprawna aplikacja webowa zbudowana w Python/Flask, która pozwala użytkownikom:
- monitorować emisje CO₂ w różnych kategoriach (transport, energia, jedzenie, inne),
- analizować trendy emisji na wykresach,
- porównywać emisję z średnią krajową,
- otrzymywać automatyczne rekomendacje redukcji CO₂,
- generować backupy danych i eksporty CSV/PDF,
- korzystać z REST API do integrowania danych.

Projekt powstał jako kompletna aplikacja edukacyjno-analityczna z rozbudowaną logiką backendową oraz nowoczesnym frontendem.

---

# 🚀 Funkcje

### 🧾 **Rejestracja i logowanie**
- szyfrowane hasła (werkzeug)
- sesje użytkownika (Flask-Login)
- resetowanie hasła przez email

### 📝 **Dodawanie i usuwanie emisji**
- kategorie: transport, food, energy, other  
- notatki szyfrowane (Fernet AES)

### 📊 **Dashboard analityczny**
- wykres liniowy emisji w czasie  
- wykres kołowy udziałów kategorii  
- filtrowanie zakresu dat: 7, 30, 365 dni  
- boxy statystyczne z ikonami SVG  
- przewidywanie emisji rocznej (model regresji)

### 🧠 **System rekomendacji**
Na podstawie emisji użytkownika generowane są wskazówki:
- transport,
- jedzenie,
- energia,
- styl życia.

### 📦 **Eksport danych**
- eksport CSV
- eksport PDF (ReportLab)

### 🔐 **Bezpieczeństwo**
- szyfrowanie notatek i emaili (Fernet AES256)
- MySQL/MariaDB (port 3307)
- obsługa zmiennych środowiskowych `.env`

### 🔄 **Backup bazy**
- automatyczny backup co 48 godzin (script + scheduler)

### 🧪 **Testy**
- testy jednostkowe (pytest)
- testy integracyjne API
- testy autoryzacji
- mockowanie bazy

---

# 🛠️ Technologie

| Warstwa | Technologie |
|--------|-------------|
| Backend | Python 3.11, Flask, Flask-Login, Flask-SQLAlchemy |
| Frontend | HTML5, CSS3, Chart.js, własny responsive design |
| Baza danych | MariaDB 10.x (port 3307) |
| Szyfrowanie | cryptography.Fernet |
| Testy | pytest |
| Backup | Python + cron/scheduler |
| API | Flask JSON REST API |

---

# 📦 Instalacja lokalna

### 1. Sklonuj repo:
```bash
git clone https://github.com/marcinkwalski/ecotrack.git
cd ecotrack
