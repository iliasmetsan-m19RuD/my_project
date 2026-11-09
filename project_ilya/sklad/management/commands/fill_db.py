from django.core.management.base import BaseCommand
from sklad.models import *
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('🔄 Начинаю заполнение базы...')

        # ===== 1. РОЛИ =====
        role_admin, _ = Role.objects.get_or_create(name='Администратор')
        role_resp, _ = Role.objects.get_or_create(name='Ответственный')
        role_worker, _ = Role.objects.get_or_create(name='Сотрудник')
        self.stdout.write(self.style.SUCCESS('✅ Роли созданы'))

        # ===== 2. СОТРУДНИКИ =====
        user_admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Илья',
                'second_name': 'Иванов',
                'third_name': 'Петрович',
                'password': 'admin123',
                'email': 'admin@sklad.ru',
                'phone': '+79001112233',
                'date_of_birth': '1990-01-15',
                'role': role_admin,
            }
        )
        user_resp, _ = User.objects.get_or_create(
            username='manager',
            defaults={
                'first_name': 'Анна',
                'second_name': 'Петрова',
                'third_name': 'Сергеевна',
                'password': '12345',
                'email': 'manager@sklad.ru',
                'phone': '+79002223344',
                'date_of_birth': '1985-05-20',
                'role': role_resp,
            }
        )
        user_worker, _ = User.objects.get_or_create(
            username='worker',
            defaults={
                'first_name': 'Сергей',
                'second_name': 'Сидоров',
                'third_name': '',
                'password': '12345',
                'email': 'worker@sklad.ru',
                'phone': '+79003334455',
                'date_of_birth': '1995-10-10',
                'role': role_worker,
            }
        )
        self.stdout.write(self.style.SUCCESS('✅ Сотрудники созданы'))
        self.stdout.write(f'   Логин/пароль админа: admin / admin123')
        self.stdout.write(f'   Логин/пароль менеджера: manager / 12345')
        self.stdout.write(f'   Логин/пароль сотрудника: worker / 12345')

        # ===== 3. СКЛАДЫ =====
        sklad_a, _ = Sklad.objects.get_or_create(
            name='Склад А',
            defaults={'address': 'г. Москва, ул. Ленина, 1', 'main': user_admin}
        )
        sklad_b, _ = Sklad.objects.get_or_create(
            name='Склад Б',
            defaults={'address': 'г. Москва, ул. Пушкина, 10', 'main': user_resp}
        )
        sklad_c, _ = Sklad.objects.get_or_create(
            name='Склад В',
            defaults={'address': 'г. Москва, ул. Гагарина, 5', 'main': user_admin}
        )
        self.stdout.write(self.style.SUCCESS('✅ Склады созданы'))

        # ===== 4. КОНТРАГЕНТЫ =====
        producer1, _ = CounterAgent.objects.get_or_create(
            name='ООО "Производитель 1"',
            defaults={'inn': '7712345678', 'is_producer': True}
        )
        producer2, _ = CounterAgent.objects.get_or_create(
            name='ЗАО "Фабрика"',
            defaults={'inn': '7787654321', 'is_producer': True}
        )
        importer1, _ = CounterAgent.objects.get_or_create(
            name='ООО "Поставщик"',
            defaults={'inn': '7711111111', 'is_importer': True}
        )
        importer2, _ = CounterAgent.objects.get_or_create(
            name='ИП Смирнов',
            defaults={'inn': '7722222222', 'is_importer': True}
        )
        client1, _ = CounterAgent.objects.get_or_create(
            name='ООО "Покупатель"',
            defaults={'inn': '7733333333', 'is_client': True}
        )
        client2, _ = CounterAgent.objects.get_or_create(
            name='Магазин "Ромашка"',
            defaults={'inn': '7744444444', 'is_client': True}
        )
        self.stdout.write(self.style.SUCCESS('✅ Контрагенты созданы'))

        # ===== 5. ГРУППЫ ТОВАРОВ =====
        group1, _ = GroupOfProduct.objects.get_or_create(name='Электроника')
        group2, _ = GroupOfProduct.objects.get_or_create(name='Одежда')
        group3, _ = GroupOfProduct.objects.get_or_create(name='Продукты')
        group4, _ = GroupOfProduct.objects.get_or_create(name='Стройматериалы')
        self.stdout.write(self.style.SUCCESS('✅ Группы товаров созданы'))

        # ===== 6. ТОВАРЫ (без unit - всё в шт) =====
        product1, _ = Product.objects.get_or_create(
            articul='EL-001',
            defaults={'name': 'Ноутбук ASUS', 'producer': producer1, 'group': group1}
        )
        product2, _ = Product.objects.get_or_create(
            articul='EL-002',
            defaults={'name': 'Мышь беспроводная', 'producer': producer1, 'group': group1}
        )
        product3, _ = Product.objects.get_or_create(
            articul='EL-003',
            defaults={'name': 'Клавиатура механическая', 'producer': producer2, 'group': group1}
        )
        product4, _ = Product.objects.get_or_create(
            articul='CL-001',
            defaults={'name': 'Футболка белая', 'producer': producer2, 'group': group2}
        )
        product5, _ = Product.objects.get_or_create(
            articul='CL-002',
            defaults={'name': 'Джинсы синие', 'producer': producer2, 'group': group2}
        )
        product6, _ = Product.objects.get_or_create(
            articul='FD-001',
            defaults={'name': 'Кофе в зёрнах 1кг', 'producer': producer1, 'group': group3}
        )
        product7, _ = Product.objects.get_or_create(
            articul='FD-002',
            defaults={'name': 'Чай чёрный 500г', 'producer': producer1, 'group': group3}
        )
        product8, _ = Product.objects.get_or_create(
            articul='SM-001',
            defaults={'name': 'Цемент М500 50кг', 'producer': producer2, 'group': group4}
        )
        self.stdout.write(self.style.SUCCESS('✅ Товары созданы'))

        # ===== 7. ПРИЧИНЫ СПИСАНИЯ =====
        reason1, _ = ReasonOfMinus.objects.get_or_create(name='Брак')
        reason2, _ = ReasonOfMinus.objects.get_or_create(name='Утрата')
        reason3, _ = ReasonOfMinus.objects.get_or_create(name='Истёк срок годности')
        reason4, _ = ReasonOfMinus.objects.get_or_create(name='Нужды производства')
        self.stdout.write(self.style.SUCCESS('✅ Причины списания созданы'))

        # ===== 8. ТЕСТОВЫЕ ДОКУМЕНТЫ =====
        today = date.today()

        # Поставка на склад А
        doc_plus1, created = PlusProduct.objects.get_or_create(
            sklad=sklad_a,
            importer=importer1,
            date=today - timedelta(days=10),
            defaults={'is_using': True}
        )
        if created:
            LineOfPlus.objects.create(plusProduct=doc_plus1, product=product1, count=50)
            LineOfPlus.objects.create(plusProduct=doc_plus1, product=product2, count=200)
            LineOfPlus.objects.create(plusProduct=doc_plus1, product=product3, count=100)
            self.stdout.write(self.style.SUCCESS(f'✅ Поставка №{doc_plus1.id:08d} создана'))

        # Поставка на склад Б
        doc_plus2, created = PlusProduct.objects.get_or_create(
            sklad=sklad_b,
            importer=importer2,
            date=today - timedelta(days=5),
            defaults={'is_using': True}
        )
        if created:
            LineOfPlus.objects.create(plusProduct=doc_plus2, product=product4, count=300)
            LineOfPlus.objects.create(plusProduct=doc_plus2, product=product5, count=150)
            LineOfPlus.objects.create(plusProduct=doc_plus2, product=product6, count=50)
            self.stdout.write(self.style.SUCCESS(f'✅ Поставка №{doc_plus2.id:08d} создана'))

        # Поставка на склад В
        doc_plus3, created = PlusProduct.objects.get_or_create(
            sklad=sklad_c,
            importer=importer1,
            date=today - timedelta(days=3),
            defaults={'is_using': True}
        )
        if created:
            LineOfPlus.objects.create(plusProduct=doc_plus3, product=product7, count=100)
            LineOfPlus.objects.create(plusProduct=doc_plus3, product=product8, count=200)
            self.stdout.write(self.style.SUCCESS(f'✅ Поставка №{doc_plus3.id:08d} создана'))

        # Реализация со склада А
        doc_sell1, created = SellProduct.objects.get_or_create(
            sklad=sklad_a,
            client=client1,
            date=today - timedelta(days=2),
            defaults={'is_using': True}
        )
        if created:
            LineOfSell.objects.create(sellProduct=doc_sell1, product=product1, count=10)
            LineOfSell.objects.create(sellProduct=doc_sell1, product=product2, count=50)
            self.stdout.write(self.style.SUCCESS(f'✅ Реализация №{doc_sell1.id:08d} создана'))

        # Списание со склада Б
        doc_minus1, created = MinusProduct.objects.get_or_create(
            sklad=sklad_b,
            reason=reason1,
            date=today - timedelta(days=1),
            defaults={'is_using': True}
        )
        if created:
            LineOfMinus.objects.create(minusProduct=doc_minus1, product=product4, count=5)
            self.stdout.write(self.style.SUCCESS(f'✅ Списание №{doc_minus1.id:08d} создано'))

        # Перемещение со склада А на склад В
        doc_remove1, created = RemoveToSklad.objects.get_or_create(
            sklad_sender=sklad_a,
            sklad_getter=sklad_c,
            date=today - timedelta(days=1),
            defaults={'is_using': True}
        )
        if created:
            LineOfRemove.objects.create(removeToSklad=doc_remove1, product=product3, count=30)
            self.stdout.write(self.style.SUCCESS(f'✅ Перемещение №{doc_remove1.id:08d} создано'))

        self.stdout.write(self.style.SUCCESS('\n🎉 База данных успешно заполнена!'))
        self.stdout.write(self.style.WARNING('\n📋 Данные для входа:'))
        self.stdout.write('   Администратор: admin / admin123')
        self.stdout.write('   Менеджер: manager / 12345')
        self.stdout.write('   Сотрудник: worker / 12345')
        self.stdout.write('\n🌐 Запусти сервер: python manage.py runserver')
        self.stdout.write('   Затем открой: http://127.0.0.1:8000/login/')