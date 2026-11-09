#ifndef REPORT_H
#define REPORT_H

#include "common.h"

typedef struct {
    double total_sum;
    int    total_sales;
} TotalResult;

typedef struct {
    int    product_id;
    char   product_name[MAX_NAME_LEN];
    int    sold_count;
    double revenue;
} PopularityItem;

typedef struct {
    PopularityItem top[5];
    PopularityItem bottom[5];
    int top_count;
    int bottom_count;
} PopularityResult;

typedef struct {
    int    customer_id;
    char   customer_name[MAX_NAME_LEN];
    double spent;
} HighValueCustomer;

typedef struct {
    HighValueCustomer *items;
    int    count;
    double threshold;
} HighValueResult;

typedef struct {
    time_t day;
    int    sales_count;
    double revenue;
} TrendPoint;

typedef struct {
    TrendPoint *points;
    int count;
} TrendResult;

int report_generate(const char *path,
                    const TotalResult *total,
                    const PopularityResult *pop,
                    const HighValueResult *hv,
                    const TrendResult *trend);

#endif
