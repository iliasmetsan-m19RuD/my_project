from django.contrib import admin
from .models import *

class LineOfPlusInline(admin.TabularInline):
    model = LineOfPlus
    extra = 1

class LineOfMinusInline(admin.TabularInline):
    model = LineOfMinus
    extra = 1

class LineOfRemoveInline(admin.TabularInline):
    model = LineOfRemove
    extra = 1

class LineOfSellInline(admin.TabularInline):
    model = LineOfSell
    extra = 1

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'second_name', 'first_name', 'role')
    list_filter = ('role',)

@admin.register(Sklad)
class SkladAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'main')

@admin.register(CounterAgent)
class CounterAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inn', 'is_producer', 'is_client', 'is_importer')

@admin.register(GroupOfProduct)
class GroupOfProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'articul', 'name', 'group', 'producer')
    list_filter = ('group', 'producer')

@admin.register(ReasonOfMinus)
class ReasonOfMinusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(PlusProduct)
class PlusProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'sklad', 'importer', 'is_using')
    inlines = [LineOfPlusInline]

@admin.register(MinusProduct)
class MinusProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'sklad', 'reason', 'is_using')
    inlines = [LineOfMinusInline]

@admin.register(RemoveToSklad)
class RemoveToSkladAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'sklad_sender', 'sklad_getter', 'is_using')
    inlines = [LineOfRemoveInline]

@admin.register(SellProduct)
class SellProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'sklad', 'client', 'is_using')
    inlines = [LineOfSellInline]