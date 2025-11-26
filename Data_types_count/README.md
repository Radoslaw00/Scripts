# SCAN TOOL LAUNCHER 🔍

[🇵🇱 POLSKI](#-polski) | [🇬🇧 ENGLISH](#-english)

---

## 🇵🇱 POLSKI

### Opis
**SCAN TOOL LAUNCHER** to wszechstronne narzędzie terminalowe do skanowania, analizy i konwersji plików na systemach Windows. Łączy wiele potrzebnych funkcji w jednym intuicyjnym interfejsie z kolorowymi menu.

### Wymagania
- Python 3.6+
- Windows 10/11 (z obsługą ANSI escape sequences)
- Biblioteka Pillow (wymagana tylko dla konwersji obrazów)

### Instalacja

#### Zainstalowanie biblioteki Pillow (opcjonalnie, tylko dla narzędzia konwersji obrazów)
```bash
pip install pillow
```

### Funkcje

#### 1. **Local / Custom Scan** (Skan lokalny / niestandardowy)
Skanuje wybraną ścieżkę w systemie plików i wyświetla:
- Liczbę znalezionych folderów
- Liczbę znalezionych plików
- Rozkład plików wg. rozszerzeń

**Opcje:**
- Skanowanie bieżącego katalogu
- Skanowanie ścieżki niestandardowej

**Plik:** `what.py`

---

#### 2. **Full System Scan** (Pełny skan systemu)
Przeprowadza pełny skan całego systemu (wszystkich dysków), analizując zawartość i zbierając statystyki.

**Funkcje:**
- Rekurencyjne skanowanie wszystkich dysków
- Raport statystyk plików i folderów
- Wskaźnik postępu skanowania
- Informacje o rozmiarach

**Plik:** `enterieos.py`

---

#### 3. **Select Drive Scan** (Skan wybranego dysku)
Pozwala wybrać konkretny dysk do skanowania.

**Funkcje:**
- Automatyczne wykrycie dostępnych dysków
- Wybór dysku z listy
- Szczegółowa analiza zawartości

**Plik:** `SELfile.py`

---

#### 4. **Installed Programs** (Zainstalowane programy)
Wyświetla listę wszystkich zainstalowanych programów na systemie.

**Funkcje:**
- Pobranie informacji z rejestru Windows
- Informacje o wydawcy i wersji
- Sortowanie i wyszukiwanie

**Plik:** `programlist.py`

---

#### 5. **Image Converter** (Konwerter obrazów)
Konwertuje wszystkie obrazy w wybranym folderze do innego formatu.

**Obsługiwane formaty:**
- WEBP
- PNG
- JPG / JPEG
- BMP
- TIFF
- GIF

**Funkcje:**
- Batch konwersja obrazów
- Opcja usunięcia oryginalnych plików
- Automatyczne obsługiwanie kanału alfa dla JPEG
- Jakość WEBP ustawiona na 90%

**Wymagania:** Biblioteka `Pillow`

**Plik:** `image_converter.py`

---

#### H. **Readme**
Otwiera dokumentację w domyślnej przeglądarce internetowej.

---

#### X. **Quit**
Zamyka aplikację.

---

### Instrukcja obsługi

1. **Uruchomienie programu:**
   ```bash
   python ALL.py
   ```

2. **Menu główne:**
   - Używaj klawiszy numerycznych (1-5) do wybrania narzędzia
   - Naciśnij `H` aby otworzyć README
   - Naciśnij `X` aby wyjść z programu

3. **Po zakończeniu działania narzędzia:**
   - Powrócisz do menu głównego
   - Możesz wybrać inne narzędzie lub wyjść

4. **Ścieżki plików:**
   - Jeśli używasz ścieżki ze spacjami, możesz ją ująć w cudzysłów: `"C:\Moje Dokumenty"`

### Cechy

✅ **Wielokolorowy interfejs** - Kolorowe menu dla lepszej czytelności
✅ **Centrowanie dynamiczne** - Wszystkie okna automatycznie wyśrodkowane w terminalu
✅ **Szybkie skanowanie** - Wielowątkowe przetwarzanie dla szybkości
✅ **Szczegółowe raporty** - Wyświetlanie pełnych statystyk
✅ **Obsługa Windows** - Zoptymalizowane dla systemu Windows
✅ **Intuicyjny interfejs** - Łatwe w użyciu menu terminalowe

### Troubleshooting

**Problem: Kolory się nie wyświetlają poprawnie**
- Upewnij się, że uruchamiasz w Windows PowerShell lub Windows Terminal
- Starsze wersje CMD mogą nie wspierać ANSI escape sequences

**Problem: Biblioteka Pillow nie zainstalowana (dla Image Converter)**
```bash
pip install pillow
```

**Problem: Permutation denied na plikach**
- Upewnij się, że masz uprawnienia do odczytu plików
- Uruchom terminal jako Administrator jeśli to konieczne

**Problem: Terminal się zawiesza**
- Naciśnij `Ctrl+C` aby przerwać
- Program powinien się zamknąć bezpiecznie

### Struktura plików

```
Data_types_count/
├── ALL.py                 # Menu główne (punkt wejściowy)
├── what.py               # Skan lokalny/niestandardowy
├── enterieos.py          # Pełny skan systemu
├── SELfile.py            # Skan wybranego dysku
├── programlist.py        # Lista zainstalowanych programów
├── image_converter.py    # Konwerter obrazów
├── HTMLREAD/
│   └── index.html        # Dokumentacja HTML
└── README.md             # Ten plik
```

### Autorzy
Radoslaw00

### Licencja
MIT License

---

---

## 🇬🇧 ENGLISH

### Description
**SCAN TOOL LAUNCHER** is a comprehensive terminal tool for scanning, analyzing, and converting files on Windows systems. It combines multiple useful functions in a single intuitive interface with colorful menus.

### Requirements
- Python 3.6+
- Windows 10/11 (with ANSI escape sequences support)
- Pillow library (required only for image conversion)

### Installation

#### Installing Pillow library (optional, only for image conversion tool)
```bash
pip install pillow
```

### Features

#### 1. **Local / Custom Scan**
Scans a selected path in the file system and displays:
- Number of found folders
- Number of found files
- File distribution by extension

**Options:**
- Scan current directory
- Scan custom path

**File:** `what.py`

---

#### 2. **Full System Scan**
Performs a full scan of the entire system (all drives), analyzing content and collecting statistics.

**Features:**
- Recursive scanning of all drives
- File and folder statistics report
- Scan progress indicator
- Size information

**File:** `enterieos.py`

---

#### 3. **Select Drive Scan**
Allows you to select a specific drive for scanning.

**Features:**
- Automatic detection of available drives
- Drive selection from list
- Detailed content analysis

**File:** `SELfile.py`

---

#### 4. **Installed Programs**
Displays a list of all programs installed on the system.

**Features:**
- Retrieves information from Windows registry
- Publisher and version information
- Sorting and search capabilities

**File:** `programlist.py`

---

#### 5. **Image Converter**
Converts all images in a selected folder to another format.

**Supported Formats:**
- WEBP
- PNG
- JPG / JPEG
- BMP
- TIFF
- GIF

**Features:**
- Batch image conversion
- Option to delete original files
- Automatic alpha channel handling for JPEG
- WEBP quality set to 90%

**Requirements:** `Pillow` library

**File:** `image_converter.py`

---

#### H. **Readme**
Opens documentation in the default web browser.

---

#### X. **Quit**
Closes the application.

---

### User Guide

1. **Running the program:**
   ```bash
   python ALL.py
   ```

2. **Main Menu:**
   - Use number keys (1-5) to select a tool
   - Press `H` to open README
   - Press `X` to exit the program

3. **After tool completion:**
   - You will return to the main menu
   - You can select another tool or exit

4. **File Paths:**
   - If using paths with spaces, you can enclose them in quotes: `"C:\My Documents"`

### Features

✅ **Colorful Interface** - Color-coded menus for better readability
✅ **Dynamic Centering** - All windows automatically centered in terminal
✅ **Fast Scanning** - Multi-threaded processing for speed
✅ **Detailed Reports** - Full statistics display
✅ **Windows Support** - Optimized for Windows
✅ **Intuitive Interface** - Easy to use terminal menu

### Troubleshooting

**Problem: Colors not displaying correctly**
- Make sure you're running in Windows PowerShell or Windows Terminal
- Older CMD versions may not support ANSI escape sequences

**Problem: Pillow library not installed (for Image Converter)**
```bash
pip install pillow
```

**Problem: Permission denied on files**
- Make sure you have read permissions for the files
- Run terminal as Administrator if necessary

**Problem: Terminal hangs**
- Press `Ctrl+C` to interrupt
- Program should close safely

### File Structure

```
Data_types_count/
├── ALL.py                 # Main menu (entry point)
├── what.py               # Local/custom scan
├── enterieos.py          # Full system scan
├── SELfile.py            # Selected drive scan
├── programlist.py        # Installed programs list
├── image_converter.py    # Image converter
├── HTMLREAD/
│   └── index.html        # HTML documentation
└── README.md             # This file
```

### Authors
Radoslaw00

### License
MIT License

