#include "common.h"
#include <sys/stat.h>
#include <sys/types.h>

/* Создание каталога, если его нет. */
void ensure_directory(const char *path) {
    struct stat st = {0};
    if (stat(path, &st) == -1) {
        mkdir(path, 0755);
    }
}

/* Создание всех рабочих каталогов. */
int create_directories(void) {
    ensure_directory("data");
    ensure_directory("reports");
    ensure_directory("logs");
    return 0;
}
