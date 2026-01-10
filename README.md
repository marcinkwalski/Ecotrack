# Ecotrack – Dokumentacja wdrożeniowa

Aplikacja internetowa do obliczania i predykcji śladu węglowego użytkownika.

---

**Uczelnia:** Politechnika Częstochowska  
**Przedmiot:** Projekt zespołowy  

**Autorzy:**  
- Marcin Kowalski  
- Mariusz Gruś  
- Jakub Kredens  

**Data wydania:** 05.01.2026

---

## 1. Wprowadzenie

Niniejsza dokumentacja opisuje proces instalacji, konfiguracji oraz uruchomienia aplikacji **Ecotrack** w środowisku serwerowym. Dokument przeznaczony jest dla administratorów systemu oraz osób odpowiedzialnych za wdrożenie i utrzymanie aplikacji. Informacje zawarte w dokumencie umożliwiają poprawne uruchomienie systemu zarówno w środowisku testowym, jak i produkcyjnym.

---

## 2. Charakterystyka środowiska docelowego

Ecotrack jest aplikacją webową typu klient–serwer.  
Backend aplikacji działa w środowisku **Python**, natomiast interfejs użytkownika dostępny jest poprzez przeglądarkę internetową. System może zostać wdrożony na serwerze VPS lub hostingu współdzielonym obsługującym aplikacje Python. Testy można wykonywać lokalnie przy użyciu pliku `run_tests.py`.

---

## 3. Wymagania sprzętowe i programowe

**Minimalne wymagania sprzętowe:**
- 1 GB pamięci RAM
- procesor jednordzeniowy
- przestrzeń dyskowa na dane aplikacji

**Wymagania programowe:**
- system operacyjny Linux
- Python 3.10 lub nowszy
- relacyjna baza danych MySQL
- narzędzie `pip`

Aplikacja może zostać wdrożona na zewnętrznym serwerze VPS lub hostingu obsługującym aplikacje Python. Proces wdrożenia obejmuje przygotowanie środowiska serwerowego, instalację Pythona oraz utworzenie środowiska wirtualnego.

---

## 4. Struktura katalogów projektu

Struktura katalogów aplikacji jest zgodna z repozytorium projektu:

```text
Ecotrack/
├── app/
│   ├── app.py
│   ├── prediction.py
│   ├── run_tests.py
│   ├── templates/
│   ├── static/
│   └── error.log
├── requirements.txt
├── .env
└── README.md
