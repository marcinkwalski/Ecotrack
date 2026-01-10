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

Niniejsza dokumentacja wdrożeniowa opisuje proces instalacji, konfiguracji oraz uruchomienia aplikacji **Ecotrack** w środowisku serwerowym.

Dokument przeznaczony jest dla administratorów systemu oraz osób odpowiedzialnych za wdrożenie i utrzymanie aplikacji. Zawarte informacje umożliwiają poprawne uruchomienie systemu zarówno w środowisku testowym, jak i produkcyjnym.

---

## 2. Charakterystyka środowiska docelowego

Aplikacja Ecotrack została zaprojektowana jako aplikacja webowa typu klient–serwer.

Backend aplikacji działa w środowisku **Python**, natomiast interfejs użytkownika dostępny jest poprzez przeglądarkę internetową.

System może zostać wdrożony na:
- serwerze VPS,
- hostingu współdzielonym obsługującym aplikacje Python.

Testy aplikacji mogą być wykonywane lokalnie przy użyciu pliku `run_tests.py`.

---

## 3. Wymagania sprzętowe i programowe

### Wymagania sprzętowe
- minimum 1 GB pamięci RAM,
- procesor jednordzeniowy,
- przestrzeń dyskowa umożliwiająca przechowywanie danych aplikacji.

### Wymagania programowe
- system operacyjny Linux,
- Python w wersji 3.10 lub nowszej,
- relacyjna baza danych MySQL,
- narzędzie `pip`.

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

## 5. Przygotowanie środowiska

Przed rozpoczęciem wdrożenia aplikacji Ecotrack konieczne jest przygotowanie środowiska serwerowego. W pierwszej kolejności należy upewnić się, że na serwerze zainstalowana jest odpowiednia wersja języka Python oraz że możliwe jest uruchamianie aplikacji w środowisku wirtualnym.

Zaleca się utworzenie środowiska `venv`, które pozwala na izolację zależności projektu od pozostałych aplikacji działających na serwerze. Takie podejście ułatwia utrzymanie systemu oraz ogranicza ryzyko konfliktów pomiędzy bibliotekami.

Aplikacja była testowana m.in. na hostingu **hostido.pl**, jednak proces przygotowania środowiska jest analogiczny dla innych serwerów obsługujących aplikacje Python.

---

## 6. Konfiguracja pliku `.env`

Plik `.env` służy do przechowywania zmiennych środowiskowych niezbędnych do prawidłowego działania aplikacji Ecotrack. Zastosowanie tego pliku umożliwia oddzielenie konfiguracji środowiska od kodu źródłowego oraz zwiększa bezpieczeństwo systemu.

W pliku `.env` definiowane są między innymi dane dostępowe do bazy danych MySQL, klucz szyfrujący `FERNET_KEY` oraz ustawienia trybu pracy aplikacji. Poprawna konfiguracja tych wartości jest warunkiem koniecznym do uruchomienia systemu.

Po każdej zmianie w pliku `.env` aplikacja powinna zostać ponownie uruchomiona, aby nowe wartości zmiennych środowiskowych zostały poprawnie załadowane. Plik ten nie powinien być udostępniany publicznie ani wersjonowany w repozytorium.

---

## 7. Instalacja zależności

Instalacja bibliotek wymaganych przez aplikację Ecotrack odbywa się na podstawie pliku `requirements.txt`. Plik ten zawiera listę wszystkich zależności niezbędnych do poprawnego działania systemu.

Proces instalacji realizowany jest przy użyciu narzędzia `pip`. W zależności od środowiska serwerowego możliwe jest wykonanie tego etapu zarówno z poziomu terminala, jak i poprzez panel administracyjny hostingu.

Poprawnie zainstalowane zależności są niezbędne do uruchomienia backendu aplikacji oraz jej komunikacji z bazą danych.

---

## 8. Konfiguracja bazy danych

Przed uruchomieniem aplikacji Ecotrack konieczne jest przygotowanie relacyjnej bazy danych MySQL. W tym celu należy utworzyć bazę danych oraz użytkownika posiadającego odpowiednie uprawnienia.

Dane dostępowe do bazy danych definiowane są w pliku `.env` i wykorzystywane przez backend aplikacji do nawiązania połączenia. Struktura tabel tworzona jest na podstawie modeli ORM zdefiniowanych w kodzie aplikacji.

Poprawna konfiguracja bazy danych jest kluczowa dla działania funkcji zapisu danych emisyjnych oraz ich dalszej analizy.

---

## 9. Uruchomienie aplikacji

Aplikacja Ecotrack może zostać uruchomiona w trybie testowym przy użyciu wbudowanego serwera frameworka Flask. Tryb ten przeznaczony jest głównie do celów deweloperskich i umożliwia szybkie sprawdzenie poprawności działania systemu.

W środowisku produkcyjnym zaleca się uruchamianie aplikacji z wykorzystaniem serwera WSGI, który pełni rolę pośrednika pomiędzy serwerem WWW a aplikacją Python. Takie rozwiązanie zapewnia większą stabilność systemu oraz umożliwia obsługę wielu jednoczesnych żądań.

W typowym scenariuszu produkcyjnym aplikacja backendowa działa za serwerem pośredniczącym obsługującym połączenia HTTPS i przekazującym żądania do serwera WSGI.

---

## 10. Weryfikacja poprawności wdrożenia

Po uruchomieniu aplikacji należy przeprowadzić weryfikację poprawności wdrożenia. Obejmuje ona sprawdzenie dostępności interfejsu użytkownika oraz podstawowych funkcjonalności systemu.

W szczególności należy zweryfikować poprawność logowania użytkownika, możliwość dodawania danych emisyjnych, generowanie wykresów oraz działanie modułu predykcji rocznej emisji CO₂.

Testy manualne stanowią najpewniejszy sposób potwierdzenia poprawnego działania aplikacji w środowisku serwerowym.

---

## 11. Zarządzanie błędami i logowanie

Backend aplikacji Ecotrack posiada mechanizm obsługi błędów oraz logowania zdarzeń systemowych. W przypadku wystąpienia błędu użytkownik otrzymuje ogólną informację o niepowodzeniu operacji.

Szczegółowe informacje o błędach zapisywane są w pliku `error.log` po stronie serwera. Rozwiązanie to ułatwia diagnozowanie problemów oraz wspiera proces utrzymania aplikacji.

---

## 12. Kopie zapasowe i utrzymanie

W środowisku produkcyjnym zaleca się wykonywanie regularnych kopii zapasowych bazy danych aplikacji Ecotrack. Kopie zapasowe powinny być realizowane przy użyciu narzędzi dedykowanych dla serwera lub systemu bazodanowego.

System Ecotrack nie posiada wbudowanego mechanizmu tworzenia kopii zapasowych, dlatego odpowiedzialność za ten proces spoczywa na administratorze systemu.

---

## 13. Uwagi końcowe

Dokumentacja wdrożeniowa opisuje kompletny proces uruchomienia aplikacji Ecotrack w środowisku serwerowym. Przedstawione procedury umożliwiają poprawne wdrożenie, konfigurację oraz utrzymanie systemu.

Aplikacja jest prosta w konfiguracji i stanowi solidną podstawę do dalszego rozwoju oraz rozbudowy funkcjonalnej w przyszłości.
