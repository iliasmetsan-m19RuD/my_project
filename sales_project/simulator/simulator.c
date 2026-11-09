#include "../include/common.h"
#include "../include/logger.h"
#include "../include/data_loader.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <time.h>

/* Параметры по умолчанию. */
#define DEFAULT_THREADS     5
#define MIN_INTERVAL_MS     100
#define MAX_INTERVAL_MS     2000
#define SIM_DURATION_SEC    30

static volatile sig_atomic_t g_stop = 0;
static pthread_mutex_t       g_file_lock = PTHREAD_MUTEX_INITIALIZER;
static int64_t               g_sale_counter = 0;

/* Обработчик сигналов завершения. */
static void on_signal(int sig) { (void)sig; g_stop = 1; }

/* Аргументы потока-продавца. */
typedef struct {
    int thread_id;
    int product_id;
    char product_name[MAX_NAME_LEN];
    int min_interval_ms;
    int max_interval_ms;
    int customer_count;
} ThreadArg;

/* Случайное число в диапазоне [a, b]. */
static int random_between(int a, int b) {
    if (a >= b) return a;
    return a + rand() % (b - a + 1);
}

/* Функция потока-продавца: имитирует продажи одного товара. */
static void *seller_thread(void *arg) {
    ThreadArg *ta = (ThreadArg *)arg;
    LOG_I("[Поток %d] Запущен для товара '%s'", ta->thread_id, ta->product_name);

    while (!g_stop) {
        /* Случайная пауза. */
        int delay_ms = random_between(ta->min_interval_ms, ta->max_interval_ms);
        struct timespec ts = { delay_ms / 1000, (delay_ms % 1000) * 1000000L };
        nanosleep(&ts, NULL);

        if (g_stop) break;

        /* Формируем и записываем продажу. */
        Sale s;
        s.id          = __sync_fetch_and_add(&g_sale_counter, 1);
        s.timestamp   = time(NULL);
        s.customer_id = random_between(1, ta->customer_count);
        s.product_id  = ta->product_id;

        if (append_sale(SALES_FILE, &s, &g_file_lock) == 0) {
            LOG_D("[Поток %d] Продажа #%lld", ta->thread_id, (long long)s.id);
        }
    }

    LOG_I("[Поток %d] Завершён", ta->thread_id);
    return NULL;
}

/* Справка по использованию. */
static void print_usage(const char *prog) {
    fprintf(stderr,
            "Использование: %s [опции]\n"
            "  -t <N>     потоков (по умолчанию %d)\n"
            "  -d <сек>   длительность (по умолчанию %d)\n"
            "  -min <мс>  минимальный интервал\n"
            "  -max <мс>  максимальный интервал\n",
            prog, DEFAULT_THREADS, SIM_DURATION_SEC);
}

int main(int argc, char **argv) {
    create_directories();
    logger_init("logs/simulator.log");
    logger_set_level(LOG_INFO);

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);
    srand((unsigned)time(NULL) ^ (unsigned)getpid());

    /* Параметры из командной строки. */
    int num_threads     = DEFAULT_THREADS;
    int duration_sec    = SIM_DURATION_SEC;
    int min_interval_ms = MIN_INTERVAL_MS;
    int max_interval_ms = MAX_INTERVAL_MS;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-t") == 0 && i + 1 < argc)
            num_threads = atoi(argv[++i]);
        else if (strcmp(argv[i], "-d") == 0 && i + 1 < argc)
            duration_sec = atoi(argv[++i]);
        else if (strcmp(argv[i], "-min") == 0 && i + 1 < argc)
            min_interval_ms = atoi(argv[++i]);
        else if (strcmp(argv[i], "-max") == 0 && i + 1 < argc)
            max_interval_ms = atoi(argv[++i]);
        else if (strcmp(argv[i], "-h") == 0) { print_usage(argv[0]); return 0; }
    }

    LOG_I("=== Симулятор: потоков=%d, длительность=%d сек ===",
          num_threads, duration_sec);

    if (generate_test_data() != 0) { LOG_E("Ошибка тестовых данных"); return 1; }

    ProductList products;
    CustomerList customers;
    if (load_products(PRODUCTS_FILE, &products) != 0) return 1;
    if (load_customers(CUSTOMERS_FILE, &customers) != 0) return 1;

    if (num_threads > products.count) num_threads = products.count;

    /* Запуск потоков. */
    pthread_t *threads = calloc(num_threads, sizeof(pthread_t));
    ThreadArg *args    = calloc(num_threads, sizeof(ThreadArg));

    for (int i = 0; i < num_threads; i++) {
        args[i].thread_id       = i + 1;
        args[i].product_id      = products.items[i].id;
        strncpy(args[i].product_name, products.items[i].name, MAX_NAME_LEN - 1);
        args[i].min_interval_ms = min_interval_ms;
        args[i].max_interval_ms = max_interval_ms;
        args[i].customer_count  = customers.count;
        pthread_create(&threads[i], NULL, seller_thread, &args[i]);
    }

    /* Основной цикл: ждём окончания или сигнала. */
    for (int sec = 0; sec < duration_sec && !g_stop; sec++) {
        sleep(1);
        if (sec % 5 == 0)
            LOG_I("Продаж: %lld", (long long)g_sale_counter);
    }

    g_stop = 1;
    for (int i = 0; i < num_threads; i++) pthread_join(threads[i], NULL);

    LOG_I("=== Симулятор завершён. Всего продаж: %lld ===",
          (long long)g_sale_counter);

    free(threads);
    free(args);
    logger_close();
    return 0;
}
