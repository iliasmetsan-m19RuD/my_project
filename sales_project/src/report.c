#include "report.h"
#include "logger.h"
#include <stdio.h>
#include <time.h>

int report_generate(const char *path,
                    const TotalResult *total,
                    const PopularityResult *pop,
                    const HighValueResult *hv,
                    const TrendResult *trend) {
    FILE *f = fopen(path, "w");
    if (!f) { LOG_E("Не удалось создать отчёт: %s", path); return -1; }

    /* Заголовок отчёта. */
    time_t now = time(NULL);
    struct tm tm_info;
    localtime_r(&now, &tm_info);
    char time_buf[64];
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", &tm_info);

    fprintf(f, "========================================================\n");
    fprintf(f, "          ОТЧЁТ ПО ПРОДАЖАМ\n");
    fprintf(f, "          Сформирован: %s\n", time_buf);
    fprintf(f, "========================================================\n\n");

    /* Раздел 1: общая сумма. */
    fprintf(f, "1. ОБЩАЯ СУММА ПРОДАЖ\n");
    fprintf(f, "--------------------------------------------------------\n");
    fprintf(f, "   Количество продаж : %d\n", total->total_sales);
    fprintf(f, "   Общая выручка     : %.2f руб.\n\n", total->total_sum);

    /* Раздел 2: популярность. */
    fprintf(f, "2. ПОПУЛЯРНОСТЬ ТОВАРОВ\n");
    fprintf(f, "--------------------------------------------------------\n");
    fprintf(f, "   ТОП-%d самых популярных:\n", pop->top_count);
    for (int i = 0; i < pop->top_count; i++) {
        fprintf(f, "     %d. %-20s  продано: %4d  выручка: %10.2f руб.\n",
                i + 1, pop->top[i].product_name,
                pop->top[i].sold_count, pop->top[i].revenue);
    }
    fprintf(f, "\n   ТОП-%d наименее популярных:\n", pop->bottom_count);
    for (int i = 0; i < pop->bottom_count; i++) {
        fprintf(f, "     %d. %-20s  продано: %4d  выручка: %10.2f руб.\n",
                i + 1, pop->bottom[i].product_name,
                pop->bottom[i].sold_count, pop->bottom[i].revenue);
    }
    fprintf(f, "\n");

    /* Раздел 3: крупные покупатели. */
    fprintf(f, "3. ПОКУПАТЕЛИ С СУММОЙ ПОКУПОК СВЫШЕ %.2f руб.\n", hv->threshold);
    fprintf(f, "--------------------------------------------------------\n");
    if (hv->count == 0) {
        fprintf(f, "   Покупателей не найдено.\n");
    } else {
        for (int i = 0; i < hv->count; i++) {
            fprintf(f, "     %-25s  ID: %4d  сумма: %10.2f руб.\n",
                    hv->items[i].customer_name,
                    hv->items[i].customer_id,
                    hv->items[i].spent);
        }
    }
    fprintf(f, "\n");

    /* Раздел 4: тенденции. */
    fprintf(f, "4. ТЕНДЕНЦИИ ПРОДАЖ (по дням)\n");
    fprintf(f, "--------------------------------------------------------\n");
    if (trend->count == 0) {
        fprintf(f, "   Нет данных.\n");
    } else {
        fprintf(f, "   %-12s  %-10s  %-15s\n", "Дата", "Продаж", "Выручка");
        for (int i = 0; i < trend->count; i++) {
            struct tm tm_day;
            localtime_r(&trend->points[i].day, &tm_day);
            char day_buf[16];
            strftime(day_buf, sizeof(day_buf), "%Y-%m-%d", &tm_day);
            fprintf(f, "   %-12s  %-10d  %-15.2f\n",
                    day_buf, trend->points[i].sales_count,
                    trend->points[i].revenue);
        }

        /* Оценка тренда. */
        if (trend->count >= 2) {
            double first = trend->points[0].revenue;
            double last  = trend->points[trend->count - 1].revenue;
            fprintf(f, "\n   Оценка тренда: ");
            if (last > first * 1.1)
                fprintf(f, "РОСТ (%.2f -> %.2f)\n", first, last);
            else if (last < first * 0.9)
                fprintf(f, "ПАДЕНИЕ (%.2f -> %.2f)\n", first, last);
            else
                fprintf(f, "СТАБИЛЬНО (%.2f -> %.2f)\n", first, last);
        }
    }

    fprintf(f, "\n========================================================\n");
    fprintf(f, "                   КОНЕЦ ОТЧЁТА\n");
    fprintf(f, "========================================================\n");

    fclose(f);
    LOG_I("Отчёт сохранён: %s", path);
    return 0;
}
