#include "logger.h"
#include <stdarg.h>
#include <time.h>
#include <pthread.h>

static FILE      *g_log_file = NULL;
static LogLevel   g_min_level = LOG_DEBUG;
static pthread_mutex_t g_log_mutex = PTHREAD_MUTEX_INITIALIZER;

/* Преобразование уровня в строку. */
static const char *level_str(LogLevel l) {
    switch (l) {
        case LOG_DEBUG: return "DEBUG";
        case LOG_INFO:  return "INFO ";
        case LOG_WARN:  return "WARN ";
        case LOG_ERROR: return "ERROR";
    }
    return "?????";
}

int logger_init(const char *log_file) {
    g_log_file = fopen(log_file, "a");
    return g_log_file ? 0 : -1;
}

void logger_close(void) {
    if (g_log_file) { fclose(g_log_file); g_log_file = NULL; }
}

void logger_set_level(LogLevel level) { g_min_level = level; }

/* Потокобезопасная запись лога. */
void logger_log(LogLevel level, const char *fmt, ...) {
    if (level < g_min_level) return;

    pthread_mutex_lock(&g_log_mutex);

    /* Временная метка. */
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);
    char time_buf[32];
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", &tm_info);

    if (g_log_file) {
        fprintf(g_log_file, "[%s] [%s] [tid:%lu] ",
                time_buf, level_str(level), (unsigned long)pthread_self());
        va_list args;
        va_start(args, fmt);
        vfprintf(g_log_file, fmt, args);
        va_end(args);
        fprintf(g_log_file, "\n");
        fflush(g_log_file);
    }

    /* Дублирование ошибок в stderr. */
    if (level >= LOG_WARN) {
        fprintf(stderr, "[%s] [%s] ", time_buf, level_str(level));
        va_list args;
        va_start(args, fmt);
        vfprintf(stderr, fmt, args);
        va_end(args);
        fprintf(stderr, "\n");
    }

    pthread_mutex_unlock(&g_log_mutex);
}
