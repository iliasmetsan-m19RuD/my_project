#include "data_loader.h"
#include "logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <pthread.h>

/* Проверка существования файла. */
static int file_exists(const char *path) {
    struct stat st;
    return stat(path, &st) == 0;
}

/* Удаление символов \n и \r в конце строки. */
static void trim_newline(char *s) {
    size_t len = strlen(s);
    while (len > 0 && (s[len-1] == '\n' || s[len-1] == '\r'))
        s[--len] = '\0';
}

/*
 * Пропуск заголовка CSV.
 * Если первая строка начинается с "id", она считается заголовком.
 * Иначе файл перематывается в начало.
 */
static void skip_header(FILE *f) {
    char line[MAX_LINE_LEN];
    if (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "id", 2) != 0) {
            rewind(f);
        }
    }
}

/* ---------- Загрузка товаров ---------- */

int load_products(const char *path, ProductList *out) {
    FILE *f = fopen(path, "r");
    if (!f) { LOG_E("Нет файла товаров: %s", path); return -1; }

    char line[MAX_LINE_LEN];
    out->count = 0;

    skip_header(f);

    /* Формат CSV: id,name,price */
    while (fgets(line, sizeof(line), f) && out->count < MAX_PRODUCTS) {
        trim_newline(line);
        if (strlen(line) == 0) continue;

        Product *p = &out->items[out->count];
        if (sscanf(line, "%d,%63[^,],%lf", &p->id, p->name, &p->price) == 3) {
            out->count++;
        }
    }

    fclose(f);
    LOG_I("Загружено товаров: %d", out->count);
    return 0;
}

/* ---------- Загрузка покупателей ---------- */

int load_customers(const char *path, CustomerList *out) {
    FILE *f = fopen(path, "r");
    if (!f) { LOG_E("Нет файла покупателей: %s", path); return -1; }

    char line[MAX_LINE_LEN];
    out->count = 0;

    skip_header(f);

    /* Формат CSV: id,name */
    while (fgets(line, sizeof(line), f) && out->count < MAX_CUSTOMERS) {
        trim_newline(line);
        if (strlen(line) == 0) continue;

        Customer *c = &out->items[out->count];
        if (sscanf(line, "%d,%63[^\n]", &c->id, c->name) == 2) {
            out->count++;
        }
    }

    fclose(f);
    LOG_I("Загружено покупателей: %d", out->count);
    return 0;
}

/* ---------- Загрузка продаж ---------- */

int load_sales(const char *path, SaleList *out) {
    FILE *f = fopen(path, "r");
    if (!f) { LOG_E("Нет файла продаж: %s", path); return -1; }

    char line[MAX_LINE_LEN];
    out->count = 0;
    pthread_mutex_init(&out->lock, NULL);

    skip_header(f);

    /* Формат CSV: id,timestamp,customer_id,product_id */
    while (fgets(line, sizeof(line), f) && out->count < MAX_SALES) {
        trim_newline(line);
        if (strlen(line) == 0) continue;

        Sale *s = &out->items[out->count];
        long long ts;
        if (sscanf(line, "%lld,%lld,%d,%d",
                   (long long*)&s->id, &ts,
                   &s->customer_id, &s->product_id) == 4) {
            s->timestamp = (time_t)ts;
            out->count++;
        }
    }

    fclose(f);
    LOG_I("Загружено продаж: %d", out->count);
    return 0;
}

/* ---------- Потокобезопасная запись продажи ---------- */

int append_sale(const char *path, const Sale *sale, pthread_mutex_t *lock) {
    if (lock) pthread_mutex_lock(lock);

    FILE *f = fopen(path, "a");
    if (!f) {
        if (lock) pthread_mutex_unlock(lock);
        return -1;
    }

    fprintf(f, "%lld,%lld,%d,%d\n",
            (long long)sale->id,
            (long long)sale->timestamp,
            sale->customer_id,
            sale->product_id);
    fflush(f);
    fclose(f);

    if (lock) pthread_mutex_unlock(lock);
    return 0;
}

/* ---------- Генерация тестовых данных ---------- */

static const char *product_names[] = {
    "Хлеб", "Молоко", "Сыр", "Яблоки", "Бананы",
    "Кофе", "Чай", "Сахар", "Мука", "Рис",
    "Макароны", "Масло", "Яйца", "Курица", "Говядина",
    "Рыба", "Томаты", "Огурцы", "Картофель", "Лук"
};

static const char *customer_names[] = {
    "Иванов И.И.", "Петров П.П.", "Сидоров С.С.", "Смирнова А.В.",
    "Кузнецов В.И.", "Попова М.А.", "Васильев Н.К.", "Новикова Е.С.",
    "Морозов Д.А.", "Волкова О.Н.", "Соловьёв А.П.", "Михайлова Т.Г."
};

int generate_test_data(void) {
    int n_prod = sizeof(product_names) / sizeof(product_names[0]);
    int n_cust = sizeof(customer_names) / sizeof(customer_names[0]);

    /* Товары. */
    if (!file_exists(PRODUCTS_FILE)) {
        FILE *f = fopen(PRODUCTS_FILE, "w");
        if (!f) return -1;
        fprintf(f, "id,name,price\n");
        for (int i = 0; i < n_prod; i++) {
            fprintf(f, "%d,%s,%.2f\n", i + 1, product_names[i], 30.0 + i * 17.5);
        }
        fclose(f);
        LOG_I("Создан файл товаров: %s", PRODUCTS_FILE);
    }

    /* Покупатели. */
    if (!file_exists(CUSTOMERS_FILE)) {
        FILE *f = fopen(CUSTOMERS_FILE, "w");
        if (!f) return -1;
        fprintf(f, "id,name\n");
        for (int i = 0; i < n_cust; i++) {
            fprintf(f, "%d,%s\n", i + 1, customer_names[i]);
        }
        fclose(f);
        LOG_I("Создан файл покупателей: %s", CUSTOMERS_FILE);
    }

    /* Файл продаж (пустой, с заголовком). */
    if (!file_exists(SALES_FILE)) {
        FILE *f = fopen(SALES_FILE, "w");
        if (!f) return -1;
        fprintf(f, "id,timestamp,customer_id,product_id\n");
        fclose(f);
    }

    return 0;
}
