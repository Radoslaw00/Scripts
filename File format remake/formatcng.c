/*
Simple image batch converter in C using ImageMagick CLI ("magick").
- Shows language choice (Polish / English)
- Centered, colored ASCII box menu with borders
- Converts files in current directory (skips this source file and directories)

Requirements:
- ImageMagick must be installed and "magick" must be on PATH (Windows) or "convert" on some systems
- Compile with a standard C compiler (gcc/clang). On Windows use MinGW or MSYS2.

Usage:
> gcc -o formatcng formatcng.c
> ./formatcng
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

#ifdef _WIN32
#include <windows.h>
#define PATH_SEP "\\"
#else
#define PATH_SEP "/"
#endif

#define MAX_LINE 1024

const char *supported[] = { "webp", "png", "jpg", "jpeg", "bmp", "tiff", "gif" };
const int supported_count = sizeof(supported) / sizeof(supported[0]);

/* ANSI colors (works on many terminals; on Windows 10+ enable Virtual Terminal Processing in console if needed) */
const char *COL_RESET = "\x1b[0m";
const char *COL_BRIGHT = "\x1b[1m";
const char *COL_RED = "\x1b[31m";
const char *COL_GREEN = "\x1b[32m";
const char *COL_YELLOW = "\x1b[33m";
const char *COL_CYAN = "\x1b[36m";
const char *COL_MAGENTA = "\x1b[35m";
const char *COL_BLUE = "\x1b[34m";

int get_term_width(void) {
    const char *env = getenv("COLUMNS");
    if (env) {
        int w = atoi(env);
        if (w > 0) return w;
    }
#ifdef _WIN32
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    if (GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &csbi)) {
        return csbi.srWindow.Right - csbi.srWindow.Left + 1;
    }
#endif
    return 80;
}

void print_centered_box(char **lines, int count) {
    int width = get_term_width();
    int maxlen = 0;
    for (int i = 0; i < count; ++i) {
        int l = (int)strlen(lines[i]);
        if (l > maxlen) maxlen = l;
    }
    int pad = 4;
    int inner = maxlen + pad * 2;
    int box_width = inner + 2; // borders
    int left_pad = (width - box_width) / 2;
    if (left_pad < 0) left_pad = 0;

    char horiz[MAX_LINE];
    snprintf(horiz, sizeof(horiz), "%s+%.*s+%s", "", inner, "------------------------------------------------------------------------", "");
    // build dynamic horizontal since inner can be large
    char *horizontal = (char *)malloc(inner + 3);
    if (!horizontal) return;
    horizontal[0] = '+';
    for (int i = 1; i <= inner; ++i) horizontal[i] = '-';
    horizontal[inner + 1] = '+';
    horizontal[inner + 2] = '\0';

    for (int i = 0; i < left_pad; ++i) putchar(' ');
    puts(horizontal);
    for (int i = 0; i < count; ++i) {
        int len = (int)strlen(lines[i]);
        int left = (inner - len) / 2;
        int right = inner - len - left;
        for (int j = 0; j < left_pad; ++j) putchar(' ');
        putchar('|');
        for (int s = 0; s < left; ++s) putchar(' ');
        fputs(lines[i], stdout);
        for (int s = 0; s < right; ++s) putchar(' ');
        puts("|");
    }
    for (int i = 0; i < left_pad; ++i) putchar(' ');
    puts(horizontal);
    free(horizontal);
}

int has_image_ext(const char *name) {
    const char *dot = strrchr(name, '.');
    if (!dot || dot == name) return 0;
    const char *ext = dot + 1;
    for (int i = 0; i < supported_count; ++i) {
        if (strcasecmp(ext, supported[i]) == 0) return 1;
    }
    /* also recognize some common types */
    const char *others[] = { "ico", "svg", "webp" };
    for (size_t i = 0; i < sizeof(others)/sizeof(others[0]); ++i) {
        if (strcasecmp(ext, others[i]) == 0) return 1;
    }
    return 0;
}

int is_regular_file(const char *path) {
    struct stat st;
    if (stat(path, &st) != 0) return 0;
#ifdef _WIN32
    return (st.st_mode & S_IFREG) != 0;
#else
    return S_ISREG(st.st_mode);
#endif
}

int main(void) {
    /* language selection */
    char buf[256];
    int lang = 0; /* 0 = pl, 1 = en */

    char *lang_lines[] = { "Wybierz jêzyk / Choose the language", "1. Polski", "2. English" };
    printf("%s%s", COL_BRIGHT, COL_CYAN);
    print_centered_box(lang_lines, 3);
    printf("%s", COL_RESET);
    printf("> ");
    if (!fgets(buf, sizeof(buf), stdin)) return 0;
    if (buf[0] == '2' || buf[0] == 'e' || buf[0] == 'E') lang = 1;

    /* build menu lines based on language */
    char header[128];
    if (lang == 0) snprintf(header, sizeof(header), "Wybierz format docelowy:");
    else snprintf(header, sizeof(header), "Choose target format:");

    char *menu_lines[16];
    menu_lines[0] = header;
    menu_lines[1] = "";
    for (int i = 0; i < supported_count; ++i) {
        char *line = (char *)malloc(64);
        snprintf(line, 64, "%d. %s", i+1, supported[i]);
        menu_lines[i+2] = line;
    }

    printf("%s%s", COL_BRIGHT, COL_GREEN);
    print_centered_box(menu_lines, supported_count + 2);
    printf("%s", COL_RESET);
    printf("> ");
    if (!fgets(buf, sizeof(buf), stdin)) return 0;
    int choice = atoi(buf);
    int target_idx = -1;
    if (choice >= 1 && choice <= supported_count) target_idx = choice - 1;
    else {
        /* maybe user typed extension name */
        char *p = strtok(buf, "\r\n \t");
        if (p) {
            for (int i = 0; i < supported_count; ++i) {
                if (strcasecmp(p, supported[i]) == 0) { target_idx = i; break; }
            }
        }
    }
    if (target_idx < 0) {
        printf("%s\n", lang==0?"Nieprawid³owy wybór.":"Invalid choice.");
        return 1;
    }
    const char *target_ext = supported[target_idx];

    /* scan current directory */
    DIR *d = opendir(".");
    if (!d) { perror("opendir"); return 1; }
    struct dirent *entry;
    int converted = 0, skipped = 0;
    const char *self_name = "formatcng.c"; /* skip this file */

    while ((entry = readdir(d)) != NULL) {
        const char *name = entry->d_name;
        if (strcmp(name, self_name) == 0) continue;
        if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) continue;

        if (!has_image_ext(name)) { skipped++; continue; }

        if (!is_regular_file(name)) { skipped++; continue; }

        /* build output filename */
        char out[MAX_LINE];
        strncpy(out, name, sizeof(out)-1);
        out[sizeof(out)-1] = '\0';
        char *dot = strrchr(out, '.');
        if (dot) *dot = '\0';
        strncat(out, ".", sizeof(out)-strlen(out)-1);
        strncat(out, target_ext, sizeof(out)-strlen(out)-1);

        /* skip if already target ext */
        const char *ext = strrchr(name, '.');
        if (ext && strcasecmp(ext+1, target_ext) == 0) { skipped++; continue; }

        /* build command: using ImageMagick's magick */
        char cmd[MAX_LINE*2];
        /* quote filenames to handle spaces */
#ifdef _WIN32
        snprintf(cmd, sizeof(cmd), "magick \"%s\" \"%s\"", name, out);
#else
        snprintf(cmd, sizeof(cmd), "magick '%s' '%s'", name, out);
#endif
        printf("%sConverting %s -> %s...%s\n", COL_YELLOW, name, out, COL_RESET);
        int r = system(cmd);
        if (r == 0) converted++; else { skipped++; fprintf(stderr, "%sFailed: %s%s\n", COL_RED, name, COL_RESET); }
    }
    closedir(d);

    if (lang == 0) printf("%sGotowe. Przekonwertowano: %d. Pomiñniêto: %d.%s\n", COL_MAGENTA, converted, skipped, COL_RESET);
    else printf("%sDone. Converted: %d. Skipped: %d.%s\n", COL_MAGENTA, converted, skipped, COL_RESET);

    printf("%s%s%s ", COL_BLUE, (lang==0?"Czy usun¹æ oryginalne pliki (tak/nie)?":"Remove original files (yes/no)?"), COL_RESET);
    if (!fgets(buf, sizeof(buf), stdin)) return 0;
    if (buf[0] == 't' || buf[0] == 'T' || buf[0] == 'y' || buf[0] == 'Y') {
        DIR *d2 = opendir(".");
        if (!d2) return 0;
        while ((entry = readdir(d2)) != NULL) {
            const char *name = entry->d_name;
            if (strcmp(name, self_name) == 0) continue;
            if (!has_image_ext(name)) continue;
            /* delete original only if converted file exists */
            char out[MAX_LINE];
            strncpy(out, name, sizeof(out)-1); out[sizeof(out)-1]='\0';
            char *dot = strrchr(out, '.'); if (dot) *dot='\0';
            strncat(out, ".", sizeof(out)-strlen(out)-1); strncat(out, target_ext, sizeof(out)-strlen(out)-1);
            struct stat st;
            if (stat(out, &st) == 0) {
                if (remove(name) == 0) printf("%sDeleted: %s%s\n", COL_GREEN, name, COL_RESET);
                else fprintf(stderr, "%sFailed to delete %s%s\n", COL_RED, name, COL_RESET);
            }
        }
        closedir(d2);
    }

    /* free allocated menu lines */
    for (int i = 2; i < supported_count + 2; ++i) free(menu_lines[i]);

    return 0;
}
