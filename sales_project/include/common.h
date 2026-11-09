#ifndef COMMON_H
#define COMMON_H

#include <stdint.h>
#include <time.h>
#include <pthread.h>

/* Максимальные размеры */
#define MAX_PRODUCTS    200
#define MAX_CUSTOMERS   500
#define MAX_SALES       100000
#define MAX_NAME_LEN    64
#define MAX_PATH_LEN    256
#define MAX_LINE_LEN    512

/* Пути к файлам */
#define SALES_FILE      "data/sales.csv"
#define PRODUCTS_FILE   "data/products.csv"
#define CUSTOMERS_FILE  "data/customers.csv"
#define REPORTS_DIR     "reports"
#define LOGS_DIR        "logs"

/* Товар */
typedef struct {
    int    id;
    char   name[MAX_NAME_LEN];
    double price;
} Product;

/* Покупатель */
typedef struct {
    int  id;
    char name[MAX_NAME_LEN];
} Customer;

/* Продажа */
typedef struct {
    int64_t id;
    time_t  timestamp;
    int     customer_id;
    int     product_id;
} Sale;

/* Список товаров (простой массив, поиск — линейный). */
typedef struct {
    Product items[MAX_PRODUCTS];
    int     count;
} ProductList;

/* Список покупателей (простой массив, поиск — линейный). */
typedef struct {
    Customer items[MAX_CUSTOMERS];
    int      count;
} CustomerList;

/* Список продаж с мьютексом для потокобезопасной записи. */
typedef struct {
    Sale            items[MAX_SALES];
    int             count;
    pthread_mutex_t lock;
} SaleList;

/* Создание рабочих каталогов. */
void ensure_directory(const char *path);
int  create_directories(void);

#endif
