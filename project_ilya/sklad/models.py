from django.core.exceptions import ValidationError
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class User(models.Model):
    first_name = models.CharField(max_length=25, verbose_name='Имя')
    second_name = models.CharField(max_length=25, verbose_name='Фамилия')
    third_name = models.CharField(max_length=25, blank=True, verbose_name='Отчество')
    username = models.CharField(max_length=25, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=128, verbose_name='Пароль')
    email = models.EmailField(verbose_name='Почта')
    phone = models.CharField(max_length=15, verbose_name='Телефон')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')

    def __str__(self): return f"{self.second_name} {self.first_name} ({self.role.name})"
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def can_delete(self): return self.role.name == "Администратор"
    def can_use(self): return self.role.name in ["Администратор", "Ответственный"]

class Sklad(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    main = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Ответственный')
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

class CounterAgent(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    inn = models.CharField(max_length=12, blank=True, verbose_name='ИНН')
    is_producer = models.BooleanField(default=False, verbose_name='Производитель')
    is_client = models.BooleanField(default=False, verbose_name='Покупатель')
    is_importer = models.BooleanField(default=False, verbose_name='Поставщик')
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'

class GroupOfProduct(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Группа товаров'
        verbose_name_plural = 'Группы товаров'

class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    articul = models.CharField(max_length=20, unique=True, verbose_name='Артикул')
    producer = models.ForeignKey(CounterAgent, on_delete=models.CASCADE, verbose_name='Производитель')
    group = models.ForeignKey(GroupOfProduct, on_delete=models.CASCADE, verbose_name='Группа')
    def __str__(self): return f"{self.articul} — {self.name}"
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Document(models.Model):
    date = models.DateField(verbose_name='Дата')
    is_using = models.BooleanField(default=False, verbose_name='Проведён')
    class Meta:
        abstract = True
    def start_using(self):
        if self.is_using: raise ValidationError("Документ уже проведён")
        self.is_using = True; self.save()
    def stop_using(self):
        if not self.is_using: raise ValidationError("Документ не проведён")
        self.is_using = False; self.save()

class LineOfDocument(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    count = models.IntegerField(verbose_name='Количество')
    class Meta:
        abstract = True

class ReasonOfMinus(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    def __str__(self): return self.name
    class Meta:
        verbose_name = 'Причина списания'
        verbose_name_plural = 'Причины списания'

class MinusProduct(Document):
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE, verbose_name='Склад')
    reason = models.ForeignKey(ReasonOfMinus, on_delete=models.CASCADE, verbose_name='Причина')
    photo = models.ImageField(upload_to='documents/', blank=True, null=True, verbose_name='Фото документа')
    class Meta:
        verbose_name = 'Списание товаров'
        verbose_name_plural = 'Списания товаров'
    def __str__(self): return f"Списание №{self.id:08d} — {self.date}"

class RemoveToSklad(Document):
    sklad_sender = models.ForeignKey(Sklad, on_delete=models.CASCADE, related_name='sender_docs', verbose_name='Склад-отправитель')
    sklad_getter = models.ForeignKey(Sklad, on_delete=models.CASCADE, related_name='getter_docs', verbose_name='Склад-получатель')
    photo = models.ImageField(upload_to='documents/', blank=True, null=True, verbose_name='Фото документа')
    class Meta:
        verbose_name = 'Перемещение товаров'
        verbose_name_plural = 'Перемещения товаров'
    def __str__(self): return f"Перемещение №{self.id:08d} — {self.date}"

class PlusProduct(Document):
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE, verbose_name='Склад')
    importer = models.ForeignKey(CounterAgent, on_delete=models.CASCADE, verbose_name='Поставщик')
    photo = models.ImageField(upload_to='documents/', blank=True, null=True, verbose_name='Фото документа')
    class Meta:
        verbose_name = 'Поставка товаров'
        verbose_name_plural = 'Поставки товаров'
    def __str__(self): return f"Поставка №{self.id:08d} — {self.date}"

class SellProduct(Document):
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE, verbose_name='Склад')
    client = models.ForeignKey(CounterAgent, on_delete=models.CASCADE, verbose_name='Клиент')
    photo = models.ImageField(upload_to='documents/', blank=True, null=True, verbose_name='Фото документа')
    class Meta:
        verbose_name = 'Реализация товаров'
        verbose_name_plural = 'Реализации товаров'
    def __str__(self): return f"Реализация №{self.id:08d} — {self.date}"

class LineOfPlus(LineOfDocument):
    plusProduct = models.ForeignKey(PlusProduct, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Строка поставки'
        verbose_name_plural = 'Строки поставки'

class LineOfMinus(LineOfDocument):
    minusProduct = models.ForeignKey(MinusProduct, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Строка списания'
        verbose_name_plural = 'Строки списания'

class LineOfRemove(LineOfDocument):
    removeToSklad = models.ForeignKey(RemoveToSklad, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Строка перемещения'
        verbose_name_plural = 'Строки перемещения'

class LineOfSell(LineOfDocument):
    sellProduct = models.ForeignKey(SellProduct, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Строка реализации'
        verbose_name_plural = 'Строки реализации'