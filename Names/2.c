#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LEN 1000
#define MAX_ENTRIES 5000

typedef struct {
    char name[260];
    int occurrences;
} FolderEntry;

int main(void) {
    FILE *file;
    char line[MAX_LINE_LEN];
    FolderEntry entries[MAX_ENTRIES];
    int entry_count = 0;
    int separator_count = 0;

    // Otwieramy plik do odczytu
    if (fopen_s(&file, "list.txt", "r") != 0) {
        printf("Blad: Plik list.txt nie istnieje.\n");
        return 1;
    }

    // Czytamy plik i zliczamy foldery
    while (fgets(line, MAX_LINE_LEN, file) != NULL) {
        // Usuwamy znaki nowej linii
        line[strcspn(line, "\n")] = '\0';

        // Liczymy separatory
        if (strstr(line, "===") != NULL) {
            separator_count++;
            continue;
        }

        // Pomijamy puste linie
        if (strlen(line) == 0) {
            continue;
        }

        // Szukamy folderu na liście
        int found = 0;
        for (int i = 0; i < entry_count; i++) {
            if (strcmp(entries[i].name, line) == 0) {
                entries[i].occurrences++;
                found = 1;
                break;
            }
        }

        // Dodajemy nowy folder
        if (!found && entry_count < MAX_ENTRIES) {
            strcpy_s(entries[entry_count].name, 260, line);
            entries[entry_count].occurrences = 1;
            entry_count++;
        }
    }

    fclose(file);

    // Wyswietlamy wyniki
    printf("\n========== ANALIZA PLIKU list.txt ==========\n\n");
    printf("Liczba sesji (separatorow): %d\n\n", separator_count);
    printf("Unikalne foldery i liczba ich pojavien:\n");
    printf("-------------------------------------------\n");

    for (int i = 0; i < entry_count; i++) {
        printf("%-40s %d x\n", entries[i].name, entries[i].occurrences);
    }

    printf("-------------------------------------------\n");
    printf("Razem unikalnych folderow: %d\n\n", entry_count);

    return 0;
}
