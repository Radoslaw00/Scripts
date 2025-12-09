#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <ctype.h>

#pragma comment(lib, "kernel32.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "gdi32.lib")

#define MAX_PATH_LEN 260
#define MAX_FOLDERS 1000
#define MAX_LINE_LEN 1000
#define MAX_ENTRIES 5000
#define SEPARATOR "===========================\n"

#define IDC_BTN_SCAN 1001
#define IDC_BTN_ANALYZE 1002
#define IDC_OUTPUT 1003
#define IDC_CLEAR 1004

HWND hwndOutput;
HWND hwndMain;

// ============= FUNKCJE SKANOWANIA FOLDEROW =============

void log_message(const char *message) {
    int len = GetWindowTextLengthA(hwndOutput);
    SetFocus(hwndOutput);
    SendMessageA(hwndOutput, EM_SETSEL, len, len);
    SendMessageA(hwndOutput, EM_REPLACESEL, FALSE, (LPARAM)message);
    SendMessageA(hwndOutput, EM_REPLACESEL, FALSE, (LPARAM)"\r\n");
}

int scan_folders(void) {
    WIN32_FIND_DATAA findFileData;
    HANDLE findHandle;
    FILE *file;
    int folder_count = 0;
    char search_path[MAX_PATH_LEN] = ".\\*";
    char folder_names[MAX_FOLDERS][MAX_PATH_LEN];
    char buffer[512];

    log_message("[>] Skanowanie folderow w biezacym katalogu...");

    findHandle = FindFirstFileA(search_path, &findFileData);

    if (findHandle == INVALID_HANDLE_VALUE) {
        log_message("[!] Blad: Nie mozna odczytac katalogu.");
        return 1;
    }

    do {
        if ((findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) &&
            strcmp(findFileData.cFileName, ".") != 0 &&
            strcmp(findFileData.cFileName, "..") != 0) {
            
            if (folder_count < MAX_FOLDERS) {
                strcpy_s(folder_names[folder_count], MAX_PATH_LEN, findFileData.cFileName);
                sprintf_s(buffer, sizeof(buffer), "    - %s", findFileData.cFileName);
                log_message(buffer);
                folder_count++;
            }
        }
    } while (FindNextFileA(findHandle, &findFileData));

    FindClose(findHandle);

    if (fopen_s(&file, "list.txt", "a") != 0) {
        log_message("[!] Blad: Nie mozna otworzyc pliku list.txt");
        return 1;
    }

    fseek(file, 0, SEEK_END);
    if (ftell(file) > 0) {
        fprintf(file, "\n\n\n");
    }

    fprintf(file, SEPARATOR);

    for (int i = 0; i < folder_count; i++) {
        fprintf(file, "%s\n", folder_names[i]);
    }

    fclose(file);

    sprintf_s(buffer, sizeof(buffer), "[+] Zapisano %d folderow do pliku list.txt", folder_count);
    log_message(buffer);
    log_message("");

    return 0;
}

// ============= FUNKCJE ANALIZY list.txt =============

typedef struct {
    char name[260];
    int occurrences;
} FolderEntry;

int analyze_list(void) {
    FILE *file;
    char line[MAX_LINE_LEN];
    FolderEntry entries[MAX_ENTRIES];
    int entry_count = 0;
    int separator_count = 0;
    char buffer[512];

    log_message("[>] Analiza pliku list.txt...");
    log_message("");

    if (fopen_s(&file, "list.txt", "r") != 0) {
        log_message("[!] Blad: Plik list.txt nie istnieje.");
        return 1;
    }

    while (fgets(line, MAX_LINE_LEN, file) != NULL) {
        line[strcspn(line, "\n")] = '\0';

        if (strstr(line, "===") != NULL) {
            separator_count++;
            continue;
        }

        if (strlen(line) == 0) {
            continue;
        }

        int found = 0;
        for (int i = 0; i < entry_count; i++) {
            if (strcmp(entries[i].name, line) == 0) {
                entries[i].occurrences++;
                found = 1;
                break;
            }
        }

        if (!found && entry_count < MAX_ENTRIES) {
            strcpy_s(entries[entry_count].name, 260, line);
            entries[entry_count].occurrences = 1;
            entry_count++;
        }
    }

    fclose(file);

    log_message("========== WYNIKI ANALIZY ==========");
    sprintf_s(buffer, sizeof(buffer), "Liczba sesji: %d", separator_count);
    log_message(buffer);
    log_message("");
    log_message("Unikalne foldery:");
    log_message("-------------------------------------------");

    for (int i = 0; i < entry_count; i++) {
        sprintf_s(buffer, sizeof(buffer), "  %-40s %d x", entries[i].name, entries[i].occurrences);
        log_message(buffer);
    }

    log_message("-------------------------------------------");
    sprintf_s(buffer, sizeof(buffer), "Razem unikalnych folderow: %d", entry_count);
    log_message(buffer);
    log_message("");

    return 0;
}

// ============= CALLBACK OKNA =============

LRESULT CALLBACK WindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            HFONT hFont = CreateFontA(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                                     ANSI_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                     DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Courier New");

            hwndOutput = CreateWindowExA(
                WS_EX_CLIENTEDGE,
                "EDIT",
                "",
                WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_READONLY,
                10, 60, 560, 320,
                hwnd, (HMENU)IDC_OUTPUT, GetModuleHandleA(NULL), NULL
            );

            SendMessageA(hwndOutput, WM_SETFONT, (WPARAM)hFont, TRUE);

            CreateWindowA(
                "BUTTON",
                "Skanuj Foldery (1)",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                10, 10, 170, 40,
                hwnd, (HMENU)IDC_BTN_SCAN, GetModuleHandleA(NULL), NULL
            );

            CreateWindowA(
                "BUTTON",
                "Analizuj list.txt (2)",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                190, 10, 170, 40,
                hwnd, (HMENU)IDC_BTN_ANALYZE, GetModuleHandleA(NULL), NULL
            );

            CreateWindowA(
                "BUTTON",
                "Wyczyść",
                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                370, 10, 100, 40,
                hwnd, (HMENU)IDC_CLEAR, GetModuleHandleA(NULL), NULL
            );

            break;
        }

        case WM_COMMAND: {
            int button_id = LOWORD(wParam);

            switch (button_id) {
                case IDC_BTN_SCAN:
                    scan_folders();
                    break;

                case IDC_BTN_ANALYZE:
                    analyze_list();
                    break;

                case IDC_CLEAR:
                    SetWindowTextA(hwndOutput, "");
                    break;
            }
            break;
        }

        case WM_DESTROY:
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProcA(hwnd, msg, wParam, lParam);
    }

    return 0;
}

// ============= MAIN =============

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    const char *CLASS_NAME = "LinkuzGUIClass";

    WNDCLASSA wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.hCursor = LoadCursorA(NULL, IDC_ARROW);

    RegisterClassA(&wc);

    hwndMain = CreateWindowExA(
        0,
        CLASS_NAME,
        "Linker - Skanowanie i Analiza Folderow",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 600, 420,
        NULL, NULL, hInstance, NULL
    );

    if (!hwndMain) {
        MessageBoxA(NULL, "Blad: Nie mozna utworzyc okna!", "Blad", MB_ICONERROR);
        return 0;
    }

    ShowWindow(hwndMain, nCmdShow);
    UpdateWindow(hwndMain);

    MSG msg = {0};
    while (GetMessageA(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }

    return msg.wParam;
}
