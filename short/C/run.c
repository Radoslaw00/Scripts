#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <windows.h>
#include <ctype.h>

#define TARGET_FORMAT "webp"
#define RESIZE_WIDTH 1000
#define MAX_PATH_LEN 4096
#define MAX_SKIP_FILES 10
#define QUALITY_HIGH 90
#define QUALITY_LOW 75

typedef struct {
    char names[MAX_SKIP_FILES][256];
    int count;
} SkipFiles;

typedef struct {
    char filename[256];
    char ext[50];
} FileInfo;

// Initialize skip files list
SkipFiles init_skip_files() {
    SkipFiles skip = {0};
    strcpy(skip.names[0], "run.c");
    strcpy(skip.names[1], "run.exe");
    strcpy(skip.names[2], "run.py");
    strcpy(skip.names[3], "Sort_folder_filetypes.py");
    strcpy(skip.names[4], "p.py");
    strcpy(skip.names[5], "x.bat");
    strcpy(skip.names[6], ".sort_backup.json");
    strcpy(skip.names[7], "readme.md");
    strcpy(skip.names[8], "create_link.vbs");
    skip.count = 9;
    return skip;
}

// Check if file should be skipped
int should_skip(const char *filename, SkipFiles *skip) {
    for (int i = 0; i < skip->count; i++) {
        if (strcmp(filename, skip->names[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

// Get file extension
void get_extension(const char *filename, char *ext) {
    char *dot = strrchr(filename, '.');
    if (dot && dot != filename) {
        strcpy(ext, dot + 1);
        for (int i = 0; ext[i]; i++) {
            ext[i] = toupper(ext[i]);
        }
    } else {
        strcpy(ext, "NO_EXTENSION");
    }
}

// Get file extension (lowercase)
void get_extension_lower(const char *filename, char *ext) {
    char *dot = strrchr(filename, '.');
    if (dot && dot != filename) {
        strcpy(ext, dot + 1);
        for (int i = 0; ext[i]; i++) {
            ext[i] = tolower(ext[i]);
        }
    } else {
        strcpy(ext, "");
    }
}

// Check if file exists
int file_exists(const char *path) {
    return access(path, F_OK) != -1;
}

// Check if path is directory
int is_directory(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        return S_ISDIR(st.st_mode);
    }
    return 0;
}

// Create directory if not exists
void create_directory_if_not_exists(const char *path) {
    if (!file_exists(path)) {
        mkdir(path);
    }
}

// Check if file is an image
int is_image_file(const char *filename) {
    char ext[50] = {0};
    get_extension_lower(filename, ext);
    
    const char *image_exts[] = {"jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp", "ico", 0};
    for (int i = 0; image_exts[i]; i++) {
        if (strcmp(ext, image_exts[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

// Sort files by extension
void sort_by_extension() {
    SkipFiles skip = init_skip_files();
    DIR *dir = opendir(".");
    struct dirent *entry;
    char current_dir[MAX_PATH_LEN];
    struct stat file_stat;
    
    getcwd(current_dir, MAX_PATH_LEN);
    
    if (dir == NULL) {
        perror("Cannot open directory");
        return;
    }
    
    printf("Sorting files by extension...\n");
    
    while ((entry = readdir(dir)) != NULL) {
        char full_path[MAX_PATH_LEN];
        snprintf(full_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
        
        if (stat(full_path, &file_stat) == 0 && S_ISREG(file_stat.st_mode) && !should_skip(entry->d_name, &skip)) {
            char ext[50] = {0};
            get_extension(entry->d_name, ext);
            
            char ext_dir_path[MAX_PATH_LEN];
            snprintf(ext_dir_path, MAX_PATH_LEN, "%s\\%s", current_dir, ext);
            
            create_directory_if_not_exists(ext_dir_path);
            
            char src[MAX_PATH_LEN];
            char dst[MAX_PATH_LEN];
            snprintf(src, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
            snprintf(dst, MAX_PATH_LEN, "%s\\%s", ext_dir_path, entry->d_name);
            
            if (rename(src, dst) == 0) {
                printf("  Moved: %s -> %s\n", entry->d_name, ext);
            }
        }
    }
    
    closedir(dir);
}

// Get bigger dimension for aspect ratio calculation
void get_best_dimension(int width, int height, int *bigger, int *smaller) {
    if (width > height) {
        *bigger = width;
        *smaller = height;
    } else {
        *bigger = height;
        *smaller = width;
    }
}

// List files in directory
int list_files(const char *dirname, FileInfo **files) {
    DIR *dir = opendir(dirname);
    struct dirent *entry;
    int count = 0;
    FileInfo *file_list = malloc(sizeof(FileInfo) * 1000);
    
    if (dir == NULL) {
        return 0;
    }
    
    while ((entry = readdir(dir)) != NULL && count < 1000) {
        if (strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0) {
            strcpy(file_list[count].filename, entry->d_name);
            count++;
        }
    }
    
    closedir(dir);
    *files = file_list;
    return count;
}

// Convert image to WebP format using ImageMagick
void convert_to_webp() {
    SkipFiles skip = init_skip_files();
    DIR *dir = opendir(".");
    struct dirent *entry;
    char current_dir[MAX_PATH_LEN];
    struct stat file_stat;
    char ext[50] = {0};
    
    getcwd(current_dir, MAX_PATH_LEN);
    
    if (dir == NULL) {
        perror("Cannot open directory");
        return;
    }
    
    printf("Converting images to WebP format...\n");
    
    while ((entry = readdir(dir)) != NULL) {
        char full_path[MAX_PATH_LEN];
        snprintf(full_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
        
        if (stat(full_path, &file_stat) == 0 && S_ISREG(file_stat.st_mode) && !should_skip(entry->d_name, &skip)) {
            if (is_image_file(entry->d_name)) {
                get_extension_lower(entry->d_name, ext);
                
                // Skip if already webp
                if (strcmp(ext, "webp") == 0) {
                    continue;
                }
                
                // Create new filename with .webp extension
                char new_filename[MAX_PATH_LEN];
                char *dot = strrchr(entry->d_name, '.');
                int name_len = dot ? (dot - entry->d_name) : strlen(entry->d_name);
                strncpy(new_filename, entry->d_name, name_len);
                new_filename[name_len] = '\0';
                strcat(new_filename, ".webp");
                
                char src_path[MAX_PATH_LEN];
                char dst_path[MAX_PATH_LEN];
                snprintf(src_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
                snprintf(dst_path, MAX_PATH_LEN, "%s\\%s", current_dir, new_filename);
                
                // Use ImageMagick convert command if available, otherwise use ffmpeg
                char command[MAX_PATH_LEN * 2];
                snprintf(command, MAX_PATH_LEN * 2, 
                    "magick \"%s\" -quality %d \"%s\" 2>nul || ffmpeg -i \"%s\" -q:v %d \"%s\" -y 2>nul",
                    src_path, QUALITY_HIGH, dst_path, src_path, QUALITY_HIGH, dst_path);
                
                if (system(command) == 0) {
                    printf("  Converted: %s -> %s\n", entry->d_name, new_filename);
                }
            }
        }
    }
    
    closedir(dir);
}

// Resize images in extension folders using ImageMagick
void resize_images() {
    SkipFiles skip = init_skip_files();
    DIR *dir = opendir(".");
    struct dirent *entry;
    char current_dir[MAX_PATH_LEN];
    struct stat file_stat;
    int resized_count = 0;
    
    getcwd(current_dir, MAX_PATH_LEN);
    
    if (dir == NULL) {
        perror("Cannot open directory");
        return;
    }
    
    printf("Resizing images...\n");
    
    while ((entry = readdir(dir)) != NULL) {
        char ext_dir_path[MAX_PATH_LEN];
        snprintf(ext_dir_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
        
        if (stat(ext_dir_path, &file_stat) == 0 && S_ISDIR(file_stat.st_mode) && !should_skip(entry->d_name, &skip)) {
            DIR *ext_dir = opendir(ext_dir_path);
            if (ext_dir == NULL) continue;
            
            char resized_dir_path[MAX_PATH_LEN];
            snprintf(resized_dir_path, MAX_PATH_LEN, "%s\\RESIZED", ext_dir_path);
            
            struct dirent *file_entry;
            resized_count = 0;
            
            while ((file_entry = readdir(ext_dir)) != NULL) {
                char file_path[MAX_PATH_LEN];
                snprintf(file_path, MAX_PATH_LEN, "%s\\%s", ext_dir_path, file_entry->d_name);
                
                struct stat file_info;
                if (stat(file_path, &file_info) == 0 && S_ISREG(file_info.st_mode)) {
                    if (is_image_file(file_entry->d_name)) {
                        // Create RESIZED folder on first resize
                        if (resized_count == 0) {
                            create_directory_if_not_exists(resized_dir_path);
                        }
                        
                        char resized_path[MAX_PATH_LEN];
                        snprintf(resized_path, MAX_PATH_LEN, "%s\\%s", resized_dir_path, file_entry->d_name);
                        
                        // Resize using ImageMagick: scale to fit width 1000 maintaining aspect ratio
                        char command[MAX_PATH_LEN * 2];
                        snprintf(command, MAX_PATH_LEN * 2,
                            "magick \"%s\" -resize %dx -quality %d \"%s\" 2>nul || ffmpeg -i \"%s\" -vf scale=%d:-1 \"%s\" -y 2>nul",
                            file_path, RESIZE_WIDTH, QUALITY_HIGH, resized_path, file_path, RESIZE_WIDTH, resized_path);
                        
                        if (system(command) == 0) {
                            printf("  Resized: %s\n", file_entry->d_name);
                            resized_count++;
                        }
                    }
                }
            }
            
            closedir(ext_dir);
        }
    }
    
    closedir(dir);
}

// Optimize images using ImageMagick
void optimize_images() {
    DIR *dir = opendir(".");
    struct dirent *entry;
    char current_dir[MAX_PATH_LEN];
    struct stat file_stat;
    
    getcwd(current_dir, MAX_PATH_LEN);
    
    if (dir == NULL) {
        perror("Cannot open directory");
        return;
    }
    
    printf("Optimizing images...\n");
    
    while ((entry = readdir(dir)) != NULL) {
        char ext_dir_path[MAX_PATH_LEN];
        snprintf(ext_dir_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
        
        if (stat(ext_dir_path, &file_stat) == 0 && S_ISDIR(file_stat.st_mode)) {
            char resized_dir_path[MAX_PATH_LEN];
            snprintf(resized_dir_path, MAX_PATH_LEN, "%s\\RESIZED", ext_dir_path);
            
            if (file_exists(resized_dir_path)) {
                DIR *resized_dir = opendir(resized_dir_path);
                if (resized_dir == NULL) continue;
                
                char optimized_dir_path[MAX_PATH_LEN];
                snprintf(optimized_dir_path, MAX_PATH_LEN, "%s\\OPTIMIZED", resized_dir_path);
                create_directory_if_not_exists(optimized_dir_path);
                
                struct dirent *file_entry;
                while ((file_entry = readdir(resized_dir)) != NULL) {
                    char file_path[MAX_PATH_LEN];
                    snprintf(file_path, MAX_PATH_LEN, "%s\\%s", resized_dir_path, file_entry->d_name);
                    
                    struct stat file_info;
                    if (stat(file_path, &file_info) == 0 && S_ISREG(file_info.st_mode)) {
                        if (is_image_file(file_entry->d_name)) {
                            char optimized_path[MAX_PATH_LEN];
                            snprintf(optimized_path, MAX_PATH_LEN, "%s\\%s", optimized_dir_path, file_entry->d_name);
                            
                            char ext_lower[50] = {0};
                            get_extension_lower(file_entry->d_name, ext_lower);
                            
                            // Optimize with lower quality settings
                            char command[MAX_PATH_LEN * 2];
                            if (strcmp(ext_lower, "webp") == 0) {
                                snprintf(command, MAX_PATH_LEN * 2,
                                    "magick \"%s\" -quality %d -define webp:method=6 \"%s\" 2>nul",
                                    file_path, QUALITY_LOW, optimized_path);
                            } else {
                                snprintf(command, MAX_PATH_LEN * 2,
                                    "magick \"%s\" -quality %d -strip \"%s\" 2>nul",
                                    file_path, QUALITY_LOW, optimized_path);
                            }
                            
                            if (system(command) == 0) {
                                printf("  Optimized: %s\n", file_entry->d_name);
                            }
                        }
                    }
                }
                
                closedir(resized_dir);
            }
        }
    }
    
    closedir(dir);
}

// Create Windows shortcuts to OPTIMIZED folders
void create_shortcut() {
    DIR *dir = opendir(".");
    struct dirent *entry;
    char current_dir[MAX_PATH_LEN];
    struct stat file_stat;
    
    getcwd(current_dir, MAX_PATH_LEN);
    
    if (dir == NULL) {
        perror("Cannot open directory");
        return;
    }
    
    printf("Creating shortcuts...\n");
    
    while ((entry = readdir(dir)) != NULL) {
        char ext_dir_path[MAX_PATH_LEN];
        snprintf(ext_dir_path, MAX_PATH_LEN, "%s\\%s", current_dir, entry->d_name);
        
        if (stat(ext_dir_path, &file_stat) == 0 && S_ISDIR(file_stat.st_mode)) {
            char optimized_dir_path[MAX_PATH_LEN];
            snprintf(optimized_dir_path, MAX_PATH_LEN, "%s\\RESIZED\\OPTIMIZED", ext_dir_path);
            
            if (file_exists(optimized_dir_path)) {
                char shortcut_path[MAX_PATH_LEN];
                snprintf(shortcut_path, MAX_PATH_LEN, "%s\\OPTIMIZED & RESIZED (%s).lnk", current_dir, entry->d_name);
                
                // Create VBS script for Windows shortcut
                char vbs_path[MAX_PATH_LEN];
                snprintf(vbs_path, MAX_PATH_LEN, "%s\\create_link_%s.vbs", current_dir, entry->d_name);
                
                FILE *vbs_file = fopen(vbs_path, "w");
                if (vbs_file) {
                    fprintf(vbs_file, "Set oWS = WScript.CreateObject(\"WScript.Shell\")\n");
                    fprintf(vbs_file, "Set oLink = oWS.CreateShortcut(\"%s\")\n", shortcut_path);
                    fprintf(vbs_file, "oLink.TargetPath = \"%s\"\n", optimized_dir_path);
                    fprintf(vbs_file, "oLink.Save\n");
                    fclose(vbs_file);
                    
                    // Execute VBS script
                    char command[MAX_PATH_LEN * 2];
                    snprintf(command, MAX_PATH_LEN * 2, "cscript \"%s\" >nul 2>&1", vbs_path);
                    system(command);
                    
                    // Clean up VBS file
                    remove(vbs_path);
                    printf("  Created shortcut for: %s\n", entry->d_name);
                }
            }
        }
    }
    
    closedir(dir);
}

// Main execution
int main() {
    printf("========================================\n");
    printf("Image Organization & Processing Tool (C)\n");
    printf("========================================\n\n");
    
    printf("Note: This program uses ImageMagick or FFmpeg for image processing.\n");
    printf("Make sure ImageMagick (convert/magick) or FFmpeg is installed and in PATH.\n\n");
    
    printf("Step 1: Converting images to WebP...\n");
    convert_to_webp();
    printf("\n");
    
    printf("Step 2: Sorting files by extension...\n");
    sort_by_extension();
    printf("\n");
    
    printf("Step 3: Resizing images...\n");
    resize_images();
    printf("\n");
    
    printf("Step 4: Optimizing images...\n");
    optimize_images();
    printf("\n");
    
    printf("Step 5: Creating shortcuts...\n");
    create_shortcut();
    printf("\n");
    
    printf("========================================\n");
    printf("Process Complete!\n");
    printf("========================================\n");
    
    return 0;
}
