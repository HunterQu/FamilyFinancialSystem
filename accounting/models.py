from django.db import models
from django.utils import timezone


class NormalUser(models.Model): #用户名称
    name = models.CharField(max_length=100)

class Currency(models.Model): #货币种类
    name = models.CharField("货币名称", max_length=100)
    icon = models.CharField("货币图标", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class Account(models.Model): #账户类型，如支付宝余额、余额宝余额、银行卡余额等
    name = models.CharField("账户类型名", max_length=100)
    amount = models.DecimalField("账户余额" ,max_digits=8, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, default=1)
    icon = models.CharField(max_length=100, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_date']


class Category(models.Model): #记录大类
    CATEGORY_TYPES = (
       ("income", "收入"),
       ("expense", "支出")
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    category_type = models.CharField(choices=CATEGORY_TYPES, default=CATEGORY_TYPES[0][1], max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class SubCategory(models.Model): #子类，用于记录细分
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    parent = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class HistoryRecord(models.Model): #记录表
    username = models.ForeignKey(NormalUser, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, default=1)
    time_of_occurrence = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, default=1)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.CharField(max_length=500, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-time_of_occurrence']