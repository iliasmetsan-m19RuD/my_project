from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.contrib import messages
from django.db import models
from .models import *


def get_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None


def login_view(request):
    if get_user(request):
        return redirect('home')
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if username and password:
            try:
                user = User.objects.get(username=username, password=password)
                request.session['user_id'] = user.id
                return redirect('home')
            except User.DoesNotExist:
                error = 'Неверный логин или пароль'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def home_view(request):
    user = get_user(request)
    if not user:
        return redirect('login')
    search = request.GET.get('search', '').strip()
    sklad_id = request.GET.get('sklad', '')
    group_id = request.GET.get('group', '')
    products = Product.objects.all()
    if search:
        products = products.filter(Q(name__icontains=search) | Q(articul__icontains=search))
    if group_id:
        products = products.filter(group_id=group_id)

    sklads_to_check = [Sklad.objects.get(id=sklad_id)] if sklad_id else Sklad.objects.all()
    products_with_stock = []
    for product in products:
        for sklad in sklads_to_check:
            plus = LineOfPlus.objects.filter(
                product=product, plusProduct__sklad=sklad, plusProduct__is_using=True
            ).aggregate(total=Sum('count'))['total'] or 0
            minus = LineOfMinus.objects.filter(
                product=product, minusProduct__sklad=sklad, minusProduct__is_using=True
            ).aggregate(total=Sum('count'))['total'] or 0
            remove_out = LineOfRemove.objects.filter(
                product=product, removeToSklad__sklad_sender=sklad, removeToSklad__is_using=True
            ).aggregate(total=Sum('count'))['total'] or 0
            remove_in = LineOfRemove.objects.filter(
                product=product, removeToSklad__sklad_getter=sklad, removeToSklad__is_using=True
            ).aggregate(total=Sum('count'))['total'] or 0
            sell = LineOfSell.objects.filter(
                product=product, sellProduct__sklad=sklad, sellProduct__is_using=True
            ).aggregate(total=Sum('count'))['total'] or 0
            stock = plus - minus - remove_out + remove_in - sell
            if sklad_id or stock != 0:
                products_with_stock.append({'product': product, 'sklad': sklad, 'stock': stock})
    return render(request, 'home.html', {
        'user': user,
        'products_with_stock': products_with_stock,
        'sklads': Sklad.objects.all(),
        'groups': GroupOfProduct.objects.all(),
        'search': search,
        'sklad_id': sklad_id,
        'group_id': group_id,
    })


# ===== СПРАВОЧНИКИ =====
def directories_view(request):
    user = get_user(request)
    if not user:
        return redirect('login')
    return render(request, 'directories.html', {'user': user})


def directory_detail_view(request, directory_name):
    user = get_user(request)
    if not user:
        return redirect('login')

    directories = {
        'roles': {
            'title': 'Роли',
            'headers': ['ID', 'Название'],
            'items': Role.objects.all(),
            'get_values': lambda o: [o.id, o.name]
        },
        'users': {
            'title': 'Сотрудники',
            'headers': ['ID', 'Логин', 'ФИО', 'Роль'],
            'items': User.objects.all(),
            'get_values': lambda o: [o.id, o.username, f"{o.second_name} {o.first_name}", o.role.name]
        },
        'sklads': {
            'title': 'Склады',
            'headers': ['ID', 'Название', 'Адрес', 'Ответственный'],
            'items': Sklad.objects.all(),
            'get_values': lambda o: [o.id, o.name, o.address, o.main.username]
        },
        'counteragents': {
            'title': 'Контрагенты',
            'headers': ['ID', 'Название', 'ИНН', 'Тип'],
            'items': CounterAgent.objects.all(),
            'get_values': lambda o: [o.id, o.name, o.inn or '—', ', '.join([t for t, v in [('Производитель', o.is_producer), ('Поставщик', o.is_importer), ('Покупатель', o.is_client)] if v]) or '—']
        },
        'groups': {
            'title': 'Группы товаров',
            'headers': ['ID', 'Название'],
            'items': GroupOfProduct.objects.all(),
            'get_values': lambda o: [o.id, o.name]
        },
        'products': {
            'title': 'Товары',
            'headers': ['ID', 'Артикул', 'Название', 'Группа', 'Производитель'],
            'items': Product.objects.all(),
            'get_values': lambda o: [o.id, o.articul, o.name, o.group.name, o.producer.name]
        },
        'reasons': {
            'title': 'Причины списания',
            'headers': ['ID', 'Название'],
            'items': ReasonOfMinus.objects.all(),
            'get_values': lambda o: [o.id, o.name]
        },
    }
    if directory_name not in directories:
        return redirect('directories')
    dir_info = directories[directory_name]
    rows = [dir_info['get_values'](item) for item in dir_info['items']]

    return render(request, 'directory_detail.html', {
        'user': user,
        'title': dir_info['title'],
        'headers': dir_info['headers'],
        'rows': rows,
        'directory_name': directory_name,
    })


def directory_add_view(request, directory_name):
    user = get_user(request)
    if not user or not user.can_delete():
        return redirect('directories')
    models_map = {
        'roles': Role, 'users': User, 'sklads': Sklad,
        'counteragents': CounterAgent, 'groups': GroupOfProduct,
        'products': Product, 'reasons': ReasonOfMinus
    }
    if directory_name not in models_map:
        return redirect('directories')
    model = models_map[directory_name]

    if request.method == 'POST':
        item = model()
        for field in model._meta.fields:
            if field.name == 'id':
                continue
            val = request.POST.get(field.name)
            if val is not None:
                if isinstance(field, models.BooleanField):
                    setattr(item, field.name, val == 'on')
                elif isinstance(field, models.ForeignKey):
                    setattr(item, field.name + '_id', val if val else None)
                else:
                    setattr(item, field.name, val)
        item.save()
        messages.success(request, 'Запись добавлена')
        return redirect('directory_detail', directory_name=directory_name)

    fields_data = []
    for field in model._meta.fields:
        if field.name == 'id':
            continue
        info = {
            'name': field.name,
            'verbose_name': field.verbose_name,
            'type': type(field).__name__
        }
        if isinstance(field, models.ForeignKey):
            info['related_model'] = field.related_model
            info['related_name'] = field.related_model._meta.verbose_name_plural
            info['choices'] = field.related_model.objects.all()
        fields_data.append(info)
    return render(request, 'directory_add.html', {
        'user': user,
        'title': f'Добавление: {model._meta.verbose_name}',
        'fields_data': fields_data,
        'directory_name': directory_name
    })


def directory_edit_view(request, directory_name, item_id):
    user = get_user(request)
    if not user or not user.can_delete():
        return redirect('directories')
    models_map = {
        'roles': Role, 'users': User, 'sklads': Sklad,
        'counteragents': CounterAgent, 'groups': GroupOfProduct,
        'products': Product, 'reasons': ReasonOfMinus
    }
    if directory_name not in models_map:
        return redirect('directories')
    model = models_map[directory_name]
    item = get_object_or_404(model, id=item_id)

    if request.method == 'POST':
        for field in model._meta.fields:
            if field.name == 'id':
                continue
            val = request.POST.get(field.name)
            # Исправление Бага 2: BooleanField обрабатывается всегда
            if isinstance(field, models.BooleanField):
                setattr(item, field.name, val == 'on')
            elif isinstance(field, models.ForeignKey):
                setattr(item, field.name + '_id', val if val else None)
            elif val is not None:
                setattr(item, field.name, val)
        item.save()
        messages.success(request, 'Запись обновлена')
        return redirect('directory_detail', directory_name=directory_name)

    fields_data = []
    for field in model._meta.fields:
        if field.name == 'id':
            continue
        info = {
            'name': field.name,
            'verbose_name': field.verbose_name,
            'value': getattr(item, field.name),
            'type': type(field).__name__
        }
        if isinstance(field, models.ForeignKey):
            info['related_model'] = field.related_model
            info['related_name'] = field.related_model._meta.verbose_name_plural
            info['current_id'] = getattr(item, field.name + '_id')
            # Исправление: добавлен choices для выпадающего списка
            info['choices'] = field.related_model.objects.all()
        fields_data.append(info)
    return render(request, 'directory_edit.html', {
        'user': user,
        'title': f'Редактирование: {model._meta.verbose_name}',
        'fields_data': fields_data,
        'directory_name': directory_name
    })


def directory_delete_view(request, directory_name, item_id):
    user = get_user(request)
    if not user or not user.can_delete():
        return redirect('directories')
    models_map = {
        'roles': Role, 'users': User, 'sklads': Sklad,
        'counteragents': CounterAgent, 'groups': GroupOfProduct,
        'products': Product, 'reasons': ReasonOfMinus
    }
    if directory_name not in models_map:
        return redirect('directories')
    get_object_or_404(models_map[directory_name], id=item_id).delete()
    messages.success(request, 'Запись удалена')
    return redirect('directory_detail', directory_name=directory_name)


def documents_view(request):
    user = get_user(request)
    if not user:
        return redirect('login')
    
    sklad_id = request.GET.get('sklad', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    doc_type_filter = request.GET.get('doc_type', '')  # ← НОВОЕ: фильтр по типу
    
    plus_docs = PlusProduct.objects.all().order_by('-date')
    minus_docs = MinusProduct.objects.all().order_by('-date')
    remove_docs = RemoveToSklad.objects.all().order_by('-date')
    sell_docs = SellProduct.objects.all().order_by('-date')
    
    # ← НОВОЕ: фильтрация по типу документа
    if doc_type_filter == 'plus':
        minus_docs = minus_docs.none()
        remove_docs = remove_docs.none()
        sell_docs = sell_docs.none()
    elif doc_type_filter == 'minus':
        plus_docs = plus_docs.none()
        remove_docs = remove_docs.none()
        sell_docs = sell_docs.none()
    elif doc_type_filter == 'remove':
        plus_docs = plus_docs.none()
        minus_docs = minus_docs.none()
        sell_docs = sell_docs.none()
    elif doc_type_filter == 'sell':
        plus_docs = plus_docs.none()
        minus_docs = minus_docs.none()
        remove_docs = remove_docs.none()
    
    if sklad_id:
        plus_docs = plus_docs.filter(sklad_id=sklad_id)
        minus_docs = minus_docs.filter(sklad_id=sklad_id)
        remove_docs = remove_docs.filter(Q(sklad_sender_id=sklad_id) | Q(sklad_getter_id=sklad_id))
        sell_docs = sell_docs.filter(sklad_id=sklad_id)
    
    if date_from:
        plus_docs = plus_docs.filter(date__gte=date_from)
        minus_docs = minus_docs.filter(date__gte=date_from)
        remove_docs = remove_docs.filter(date__gte=date_from)
        sell_docs = sell_docs.filter(date__gte=date_from)
    
    if date_to:
        plus_docs = plus_docs.filter(date__lte=date_to)
        minus_docs = minus_docs.filter(date__lte=date_to)
        remove_docs = remove_docs.filter(date__lte=date_to)
        sell_docs = sell_docs.filter(date__lte=date_to)

    all_docs = []
    for doc in plus_docs:
        all_docs.append({'doc': doc, 'type': 'Поставка товара', 'sklad': doc.sklad, 'doc_type': 'plus'})
    for doc in minus_docs:
        all_docs.append({'doc': doc, 'type': 'Списание товара', 'sklad': doc.sklad, 'doc_type': 'minus'})
    for doc in remove_docs:
        all_docs.append({'doc': doc, 'type': 'Перемещение товара', 'sklad': doc.sklad_getter, 'doc_type': 'remove'})
    for doc in sell_docs:
        all_docs.append({'doc': doc, 'type': 'Реализация товара', 'sklad': doc.sklad, 'doc_type': 'sell'})
    all_docs.sort(key=lambda x: x['doc'].date, reverse=True)
    
    return render(request, 'documents.html', {
        'user': user,
        'documents': all_docs,
        'sklads': Sklad.objects.all(),
        'sklad_id': sklad_id,
        'date_from': date_from,
        'date_to': date_to,
        'doc_type_filter': doc_type_filter  # ← НОВОЕ: передаём в шаблон
    })


def document_detail_view(request, doc_type, doc_id):
    user = get_user(request)
    if not user:
        return redirect('login')
    if doc_type == 'plus':
        doc = get_object_or_404(PlusProduct, id=doc_id)
        lines = LineOfPlus.objects.filter(plusProduct=doc)
    elif doc_type == 'minus':
        doc = get_object_or_404(MinusProduct, id=doc_id)
        lines = LineOfMinus.objects.filter(minusProduct=doc)
    elif doc_type == 'remove':
        doc = get_object_or_404(RemoveToSklad, id=doc_id)
        lines = LineOfRemove.objects.filter(removeToSklad=doc)
    elif doc_type == 'sell':
        doc = get_object_or_404(SellProduct, id=doc_id)
        lines = LineOfSell.objects.filter(sellProduct=doc)
    else:
        return redirect('documents')
    return render(request, 'document_detail.html', {
        'user': user,
        'doc': doc,
        'doc_type': doc_type,
        'lines': lines
    })


def add_document_view(request, doc_type):
    user = get_user(request)
    if not user:
        return redirect('login')
    if not user.can_use():
        messages.error(request, 'У вас нет прав для создания документов')
        return redirect('documents')
    sklads = Sklad.objects.all()
    products = Product.objects.all()
    extra_context = {}
    if doc_type == 'plus':
        extra_context = {'importers': CounterAgent.objects.filter(is_importer=True)}
    elif doc_type == 'minus':
        extra_context = {'reasons': ReasonOfMinus.objects.all()}
    elif doc_type == 'sell':
        extra_context = {'clients': CounterAgent.objects.filter(is_client=True)}

    if request.method == 'POST':
        sklad_id = request.POST.get('sklad')
        date_val = request.POST.get('date')
        products_list = request.POST.getlist('product')
        counts_list = request.POST.getlist('count')
        if not sklad_id or not date_val:
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'add_document.html', {
                'user': user, 'doc_type': doc_type,
                'sklads': sklads, 'products': products, **extra_context
            })
        try:
            sklad = Sklad.objects.get(id=sklad_id)
        except Sklad.DoesNotExist:
            return redirect('documents')

        if doc_type == 'plus':
            importer = get_object_or_404(CounterAgent, id=request.POST.get('importer'))
            doc = PlusProduct.objects.create(sklad=sklad, importer=importer, date=date_val, is_using=True)
        elif doc_type == 'minus':
            reason = get_object_or_404(ReasonOfMinus, id=request.POST.get('reason'))
            doc = MinusProduct.objects.create(sklad=sklad, reason=reason, date=date_val, is_using=True)
        elif doc_type == 'remove':
            sender = get_object_or_404(Sklad, id=request.POST.get('sklad_sender'))
            getter = get_object_or_404(Sklad, id=request.POST.get('sklad_getter'))
            doc = RemoveToSklad.objects.create(sklad_sender=sender, sklad_getter=getter, date=date_val, is_using=True)
        elif doc_type == 'sell':
            client = get_object_or_404(CounterAgent, id=request.POST.get('client'))
            doc = SellProduct.objects.create(sklad=sklad, client=client, date=date_val, is_using=True)

        photo = request.FILES.get('photo')
        if photo:
            doc.photo = photo
            doc.save()

        for i in range(len(products_list)):
            if products_list[i] and counts_list[i]:
                try:
                    product = Product.objects.get(id=products_list[i])
                    count = int(counts_list[i])
                    if count > 0:
                        if doc_type == 'plus':
                            LineOfPlus.objects.create(plusProduct=doc, product=product, count=count)
                        elif doc_type == 'minus':
                            LineOfMinus.objects.create(minusProduct=doc, product=product, count=count)
                        elif doc_type == 'remove':
                            LineOfRemove.objects.create(removeToSklad=doc, product=product, count=count)
                        elif doc_type == 'sell':
                            LineOfSell.objects.create(sellProduct=doc, product=product, count=count)
                except (Product.DoesNotExist, ValueError):
                    pass
        messages.success(request, f'Документ №{doc.id:08d} создан и проведён')
        return redirect('documents')
    return render(request, 'add_document.html', {
        'user': user, 'doc_type': doc_type,
        'sklads': sklads, 'products': products, **extra_context
    })


def edit_document_view(request, doc_type, doc_id):
    user = get_user(request)
    if not user:
        return redirect('login')
    if not user.can_use():
        messages.error(request, 'У вас нет прав для редактирования документов')
        return redirect('documents')

    # Получаем существующий документ
    if doc_type == 'plus':
        doc = get_object_or_404(PlusProduct, id=doc_id)
    elif doc_type == 'minus':
        doc = get_object_or_404(MinusProduct, id=doc_id)
    elif doc_type == 'remove':
        doc = get_object_or_404(RemoveToSklad, id=doc_id)
    elif doc_type == 'sell':
        doc = get_object_or_404(SellProduct, id=doc_id)
    else:
        return redirect('documents')

    sklads = Sklad.objects.all()
    products = Product.objects.all()
    extra_context = {}

    if doc_type == 'plus':
        importers = CounterAgent.objects.filter(is_importer=True)
        extra_context = {'importers': importers, 'selected_importer': doc.importer.id}
    elif doc_type == 'minus':
        reasons = ReasonOfMinus.objects.all()
        extra_context = {'reasons': reasons, 'selected_reason': doc.reason.id}
    elif doc_type == 'remove':
        extra_context = {
            'selected_sender': doc.sklad_sender.id,
            'selected_getter': doc.sklad_getter.id
        }
    elif doc_type == 'sell':
        clients = CounterAgent.objects.filter(is_client=True)
        extra_context = {'clients': clients, 'selected_client': doc.client.id}

    if request.method == 'POST':
        sklad_id = request.POST.get('sklad')
        sklad_sender_id = request.POST.get('sklad_sender')
        sklad_getter_id = request.POST.get('sklad_getter')
        date_val = request.POST.get('date')
        products_list = request.POST.getlist('product')
        counts_list = request.POST.getlist('count')

        # Для перемещения проверяем sender и getter, для остальных — sklad
        if doc_type == 'remove':
            if not sklad_sender_id or not sklad_getter_id or not date_val:
                messages.error(request, 'Заполните все обязательные поля')
                return render(request, 'edit_document.html', {
                    'user': user, 'doc_type': doc_type, 'doc': doc,
                    'sklads': sklads, 'products': products, **extra_context
                })
        else:
            if not sklad_id or not date_val:
                messages.error(request, 'Заполните все обязательные поля')
                return render(request, 'edit_document.html', {
                    'user': user, 'doc_type': doc_type, 'doc': doc,
                    'sklads': sklads, 'products': products, **extra_context
                })

        # Обновляем основные поля документа
        doc.date = date_val

        if doc_type == 'plus':
            doc.sklad = get_object_or_404(Sklad, id=sklad_id)
            doc.importer = get_object_or_404(CounterAgent, id=request.POST.get('importer'))
        elif doc_type == 'minus':
            doc.sklad = get_object_or_404(Sklad, id=sklad_id)
            doc.reason = get_object_or_404(ReasonOfMinus, id=request.POST.get('reason'))
        elif doc_type == 'remove':
            doc.sklad_sender = get_object_or_404(Sklad, id=sklad_sender_id)
            doc.sklad_getter = get_object_or_404(Sklad, id=sklad_getter_id)
        elif doc_type == 'sell':
            doc.sklad = get_object_or_404(Sklad, id=sklad_id)
            doc.client = get_object_or_404(CounterAgent, id=request.POST.get('client'))

        # Обновляем фото если загружено новое
        photo = request.FILES.get('photo')
        if photo:
            doc.photo = photo

        doc.save()

        # Удаляем старые строки и создаём новые
        if doc_type == 'plus':
            LineOfPlus.objects.filter(plusProduct=doc).delete()
        elif doc_type == 'minus':
            LineOfMinus.objects.filter(minusProduct=doc).delete()
        elif doc_type == 'remove':
            LineOfRemove.objects.filter(removeToSklad=doc).delete()
        elif doc_type == 'sell':
            LineOfSell.objects.filter(sellProduct=doc).delete()

        for i in range(len(products_list)):
            if products_list[i] and counts_list[i]:
                try:
                    product = Product.objects.get(id=products_list[i])
                    count = int(counts_list[i])
                    if count > 0:
                        if doc_type == 'plus':
                            LineOfPlus.objects.create(plusProduct=doc, product=product, count=count)
                        elif doc_type == 'minus':
                            LineOfMinus.objects.create(minusProduct=doc, product=product, count=count)
                        elif doc_type == 'remove':
                            LineOfRemove.objects.create(removeToSklad=doc, product=product, count=count)
                        elif doc_type == 'sell':
                            LineOfSell.objects.create(sellProduct=doc, product=product, count=count)
                except (Product.DoesNotExist, ValueError):
                    pass

        messages.success(request, f'Документ №{doc.id:08d} обновлён')
        return redirect('documents')

    # Получаем существующие строки для предзаполнения формы
    if doc_type == 'plus':
        existing_lines = LineOfPlus.objects.filter(plusProduct=doc)
    elif doc_type == 'minus':
        existing_lines = LineOfMinus.objects.filter(minusProduct=doc)
    elif doc_type == 'remove':
        existing_lines = LineOfRemove.objects.filter(removeToSklad=doc)
    elif doc_type == 'sell':
        existing_lines = LineOfSell.objects.filter(sellProduct=doc)

    extra_context['existing_lines'] = existing_lines
    extra_context['selected_sklad'] = doc.sklad.id if doc_type != 'remove' else None

    return render(request, 'edit_document.html', {
        'user': user, 'doc_type': doc_type, 'doc': doc,
        'sklads': sklads, 'products': products, **extra_context
    })


def delete_document_view(request, doc_type, doc_id):
    user = get_user(request)
    if not user or not user.can_delete():
        return redirect('documents')
    if doc_type == 'plus':
        doc = get_object_or_404(PlusProduct, id=doc_id)
        LineOfPlus.objects.filter(plusProduct=doc).delete()
    elif doc_type == 'minus':
        doc = get_object_or_404(MinusProduct, id=doc_id)
        LineOfMinus.objects.filter(minusProduct=doc).delete()
    elif doc_type == 'remove':
        doc = get_object_or_404(RemoveToSklad, id=doc_id)
        LineOfRemove.objects.filter(removeToSklad=doc).delete()
    elif doc_type == 'sell':
        doc = get_object_or_404(SellProduct, id=doc_id)
        LineOfSell.objects.filter(sellProduct=doc).delete()
    else:
        return redirect('documents')
    doc.delete()
    messages.success(request, 'Документ удалён')
    return redirect('documents')