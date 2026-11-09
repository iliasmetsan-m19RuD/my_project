#ifndef DATA_LOADER_H
#define DATA_LOADER_H

#include "common.h"

int load_products(const char *path, ProductList *out);
int load_customers(const char *path, CustomerList *out);
int load_sales(const char *path, SaleList *out);
int append_sale(const char *path, const Sale *sale, pthread_mutex_t *lock);
int generate_test_data(void);

#endif
