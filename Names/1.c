#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <io.h>

#define MAX_PATH_LEN 260
#define MAX_FOLDERS 1000
#define SEPARATOR "===========================\n"

int main(void) {
    WIN32_FIND_DATAA findFileData;
    HANDLE findHandle;
    FILE *file;
    int folder_count = 0;
    char search_path[MAX_PATH_LEN] = ".\\*";
    char folder_names[MAX_FOLDERS][MAX_PATH_LEN];

    // Szukamy folderów w bieżącym katalogu
    findHandle = FindFirstFileA(search_path, &findFileData);

    if (findHandle == INVALID_HANDLE_VALUE) {
        printf("Blad: Nie mozna odczytac katalogu.\n");
        return 1;
    }

    // Zbieramy nazwy folderów
    do {
        if ((findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) &&
            strcmp(findFileData.cFileName, ".") != 0 &&
            strcmp(findFileData.cFileName, "..") != 0) {
            
            if (folder_count < MAX_FOLDERS) {
                strcpy_s(folder_names[folder_count], MAX_PATH_LEN, findFileData.cFileName);
                folder_count++;
            }
        }
    } while (FindNextFileA(findHandle, &findFileData));

    FindClose(findHandle);

    // Otwieramy plik w trybie dopisywania
    if (fopen_s(&file, "list.txt", "a") != 0) {
        printf("Blad: Nie mozna otworzyc pliku list.txt\n");
        return 1;
    }

    // Jeśli plik ma zawartość, dodajemy 3 linie odstępu
    fseek(file, 0, SEEK_END);
    if (ftell(file) > 0) {
        fprintf(file, "\n\n\n");
    }

    // Dodajemy separator
    fprintf(file, SEPARATOR);

    // Zapisujemy foldery
    for (int i = 0; i < folder_count; i++) {
        fprintf(file, "%s\n", folder_names[i]);
    }

    fclose(file);

    printf("Zapisano %d folderow do pliku list.txt\n", folder_count);

    return 0;
}
