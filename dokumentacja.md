Dokumentacja wdrożeniowa
Aplikacja Ecotrack

Aplikacja internetowa do  obliczania i predykcji śladu węglowego użytkownika






Uczelnia: 
Politechnika Częstochowska
Przedmiot: 
Projekt zespołowy






Autorzy: 
Marcin Kowalski
Mariusz Gruś
Jakub Kredens						Data wydania: 05.01.2026
1.	Wprowadzenie

Niniejsza dokumentacja wdrożeniowa opisuje proces instalacji, konfiguracji oraz uruchomienia aplikacji Ecotrack w środowisku serwerowym.
 Dokument przeznaczony jest dla administratorów systemu oraz osób odpowiedzialnych za wdrożenie i utrzymanie aplikacji. Zawarte informacje umożliwiają poprawne uruchomienie systemu zarówno w środowisku testowym, jak i produkcyjnym.
2.	Charakterystyka środowiska docelowego

Aplikacja Ecotrack została zaprojektowana jako aplikacja webowa. 
Backend aplikacji działa w środowisku Python, natomiast interfejs użytkownika dostępny jest poprzez przeglądarkę internetową. System może zostać wdrożony na serwerze VPS lub hostingu współdzielonym obsługującym aplikacje Python. Testy można wykonywać w środowisku lokalnym przy użyciu pliku run_tests.py.
3.	Wymagania sprzętowe i programowe

Minimalne wymagania sprzętowe obejmują serwer z 1 GB pamięci RAM, procesorem jednordzeniowym oraz dostępem do dysku twardego umożliwiającego przechowywanie danych aplikacji. Wymagania programowe obejmują system operacyjny Linux, Python w wersji 3.10 lub nowszej, relacyjną bazę danych MySQL oraz dostęp do narzędzia pip.
Ecotrack może zostać wdrożona na zewnętrznym serwerze VPS lub hostingu obsługującym aplikacje Python. Proces wdrożenia rozpoczyna się od przygotowania środowiska serwerowego, w tym instalacji Pythona w odpowiedniej wersji oraz utworzenia środowiska wirtualnego dla aplikacji.
W kolejnym kroku należy sklonować repozytorium projektu na serwer lub przesłać pliki aplikacji za pomocą protokołu SFTP. Po umieszczeniu plików na serwerze konieczna jest instalacja zależności z pliku requirements.txt oraz konfiguracja pliku .env zawierającego zmienne środowiskowe, takie jak dane dostępowe do bazy danych oraz klucze szyfrujące.
Po skonfigurowaniu środowiska aplikacja może zostać uruchomiona w trybie produkcyjnym z wykorzystaniem serwera WSGI (np. Gunicorn). Zaleca się umieszczenie aplikacji za serwerem pośredniczącym (np. Nginx), który odpowiada za obsługę połączeń HTTPS oraz przekazywanie żądań do aplikacji backendowej.
Po zakończeniu wdrożenia należy przeprowadzić testy poprawności działania aplikacji, w szczególności sprawdzić dostępność interfejsu użytkownika, poprawność działania endpointów API oraz zapis i odczyt danych z bazy danych. Wdrożenie na serwer zewnętrzny umożliwia udostępnienie aplikacji użytkownikom końcowym oraz jej eksploatację w środowisku produkcyjnym.

4.	Struktura katalogów projektu

Struktura katalogów aplikacji jest zgodna z repozytorium projektu:

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

Taki podział umożliwia czytelne rozdzielenie warstwy backendowej, frontendowej oraz konfiguracji i wyglądu.
5.	Przygotowanie środowiska

Przed rozpoczęciem wdrożenia należy upewnić się, że serwer posiada zainstalowaną odpowiednią wersję Pythona oraz skonfigurowane środowisko wirtualne. Zaleca się utworzenie środowiska venv w celu izolacji zależności projektu.
Przykład uruchomienia na hostingu hostido.pl
6.	Konfiguracja pliku .env

Plik .env służy do przechowywania zmiennych środowiskowych niezbędnych do prawidłowego działania aplikacji Ecotrack. Zastosowanie pliku konfiguracyjnego pozwala na oddzielenie konfiguracji środowiska od kodu źródłowego oraz zwiększa bezpieczeństwo systemu poprzez niewłączanie wrażliwych danych do repozytorium.
W pliku .env należy zdefiniować dane dostępowe do bazy danych MySQL, takie jak adres serwera bazy danych, nazwa bazy, nazwa użytkownika oraz hasło. Dane te wykorzystywane są przez backend aplikacji do nawiązania połączenia z bazą danych.
Kolejnym istotnym elementem konfiguracji jest klucz szyfrujący FERNET_KEY, wykorzystywany do zabezpieczenia wybranych danych oraz tokenów. Klucz ten musi posiadać odpowiednią długość i format oraz być unikalny dla danego środowiska wdrożeniowego.
W pliku .env mogą zostać również zdefiniowane ustawienia trybu pracy aplikacji, takie jak przełączenie pomiędzy trybem deweloperskim i produkcyjnym, a także dodatkowe parametry konfiguracyjne związane z bezpieczeństwem i działaniem aplikacji.
Po wprowadzeniu zmian w pliku .env konieczne jest ponowne uruchomienie aplikacji, aby nowe wartości zmiennych środowiskowych zostały załadowane. Plik .env nie powinien być publicznie udostępniany ani wersjonowany w systemie kontroli wersji.

7.	Instalacja zależności

Instalacja bibliotek wymaganych przez aplikację odbywa się z wykorzystaniem pliku requirements.txt. Proces instalacji realizowany jest za pomocą narzędzia pip. Na niektórych serwerach można to zrobić korzystając z gotowych pól.

8.	Konfiguracja bazy danych

Przed uruchomieniem aplikacji należy utworzyć bazę danych MySQL oraz użytkownika bazy danych. Struktura tabel tworzona jest na podstawie modeli ORM zdefiniowanych w backendzie aplikacji. Poniżej zrzut bazy z naszego wdrożenia:

9.	Uruchomienie aplikacji

Aplikacja Ecotrack może zostać uruchomiona w trybie testowym przy użyciu wbudowanego serwera frameworka Flask. Tryb ten przeznaczony jest głównie do celów deweloperskich i testowych, umożliwiając szybkie uruchomienie aplikacji oraz weryfikację poprawności działania podstawowych funkcjonalności, takich jak logowanie użytkownika, zapis danych emisyjnych czy komunikacja z bazą danych. Wbudowany serwer Flask nie jest jednak przeznaczony do obsługi większego obciążenia ani pracy w środowisku produkcyjnym.
W środowisku produkcyjnym zaleca się uruchamianie aplikacji z wykorzystaniem serwera WSGI, który pełni rolę pośrednika pomiędzy serwerem WWW a aplikacją Python. Zastosowanie serwera WSGI zwiększa stabilność systemu, umożliwia obsługę wielu jednoczesnych żądań oraz poprawia bezpieczeństwo działania aplikacji. Serwer WSGI odpowiada za zarządzanie procesami aplikacji, ich restart w przypadku awarii oraz kontrolę obciążenia.
W typowym scenariuszu produkcyjnym aplikacja backendowa uruchamiana jest za serwerem pośredniczącym, który obsługuje połączenia HTTPS oraz przekazuje żądania do serwera WSGI. Takie rozwiązanie pozwala na separację warstwy aplikacyjnej od warstwy sieciowej, ułatwia konfigurację zabezpieczeń oraz zwiększa niezawodność całego systemu. Zastosowanie architektury opartej na serwerze WSGI stanowi standardowe i rekomendowane podejście przy wdrażaniu aplikacji webowych opartych na języku Python.
W rozdziale 5 widać sposób uruchomienia aplikacji na serwerze WWW hostido.pl

10.	Weryfikacja poprawności wdrożenia

Po uruchomieniu systemu należy przeprowadzić testy manualne obejmujące logowanie użytkownika, dodawanie danych emisyjnych, generowanie wykresów oraz predykcji rocznej emisji CO₂. To najpewniejszy sposób sprawdzenia aplikacji już na etapie serwera.
11.	Zarządzanie błędami i logowanie

Aplikacja posiada mechanizm logowania błędów po stronie backendu. Szczegóły błędów zapisywane są w pliku error.log, co ułatwia diagnostykę i utrzymanie systemu.

12.	Kopie zapasowe i utrzymanie

Zaleca się wykonywanie regularnych kopii zapasowych bazy danych oraz monitorowanie poprawności działania aplikacji w środowisku produkcyjnym. Do tworzenia kopii zapasowych zalecamy korzystanie z rozwiązań dedykowanych dla serwerów. Sam system Ecotrack nie posiada takiej funkcjonalności.

13.	Uwagi końcowe

Dokumentacja wdrożeniowa opisuje kompletny proces uruchomienia systemu Ecotrack i stanowi podstawę do dalszego rozwoju oraz utrzymania aplikacji. System jest prosty we wdrożeniu i konfiguracji.

