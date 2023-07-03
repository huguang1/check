from django.db import models
from check.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your models here.


class MyUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=10)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AdminPermission(models.Model):
    name = models.CharField('权限', max_length=15)
    des = models.CharField('描述', max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = '用户权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class AdminGroup(models.Model):
    name = models.CharField('组名', max_length=15)
    permission = models.ManyToManyField(AdminPermission, verbose_name='权限')
    group_user = models.ManyToManyField(MyUser, '用户')

    class Meta:
        verbose_name = '用户组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Banks(models.Model):
    """银行"""
    name = models.CharField('银行名字', max_length=25)

    class Meta:
        verbose_name = '银行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BankCard(models.Model):
    """银行卡"""
    choose_types = (
        (0, '入款'),
        (1, '出款'),
        (2, '入款中转'),
        (3, '出款中转')
    )
    name = models.CharField('银行卡名字', max_length=25)
    bank_type = models.ForeignKey(Banks, verbose_name='所属银行', on_delete=models.CASCADE)
    account_type = models.IntegerField('银行卡的类型', choices=choose_types)
    editor = models.ForeignKey(AUTH_USER_MODEL, '管理员')
    initial_amount = models.DecimalField('初始金额', max_digits=15, decimal_places=2)
    is_disable = models.BooleanField('是否停用', default=False)

    class Meta:
        verbose_name = '银行卡'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Record(models.Model):
    """所有记录"""
    type_choices = (
        (0, '转入'),
        (1, '转出')
    )
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    type = models.IntegerField('操作类型', choices=type_choices)
    fees = models.DecimalField('手续费', max_digits=12, decimal_places=2)
    remark = models.CharField('备注', max_length=40)
    create_time = models.DateTimeField(verbose_name='创建时间')
    real_time = models.DateTimeField(auto_now_add=True, verbose_name='实际时间')
    bankcard = models.ForeignKey(BankCard, verbose_name='银行卡', on_delete=models.PROTECT)
    balance = models.DecimalField('余额', max_digits=15, decimal_places=2)
    sort = models.IntegerField('排序字段', default=0)

    class Meta:
        verbose_name = '转账记录'
        verbose_name_plural = verbose_name


@receiver(post_save, sender=Record)
def notify_handler(instance, created, **kwargs):
    if created:
        name_list = []
        for i in BankCard.objects.all():
            name_list.append(i.name)
        amount = instance.amount
        type = instance.type
        fees = instance.fees
        remark = instance.remark
        bankcard = instance.bankcard
        balance = instance.balance
        if (remark.split('@')[0] in name_list) and ((((bankcard.account_type == 0) or (bankcard.account_type == 2)) and (amount > 0) and (type == 1)) or (((bankcard.account_type == 1) or (bankcard.account_type == 3)) and (amount < 0) and (type == 0))):
            message = {
                'outbankcard': bankcard.name,
                'inbankcard': remark,
                'fees': float(fees),
                'balance': float(balance),
                'amount': float(amount)
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat_123', {"type": "chat.message", "message": message})


class LogInfo(models.Model):
    """日志"""

    name = models.CharField('操作人', max_length=20)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    action_data = models.CharField('操作内容', max_length=255)
    ip = models.GenericIPAddressField('IP地址')
    is_delete = models.BooleanField('是否删除', default=False)


class TransferType(models.Model):
    """转帐类型"""
    type_choices = (
        (0, '转入'),
        (1, '转出')
    )
    name = models.CharField('转入类型', max_length=20)
    transfer_type = models.IntegerField("类型", choices=type_choices, default=0)


class YesterdayBalance(models.Model):
    """实时记录需要填入的数据"""
    create_time = models.DateField(verbose_name='记录时间')
    real_time = models.DateTimeField(auto_now_add=True, verbose_name='实际时间')
    balance = models.DecimalField('余额', max_digits=15, decimal_places=2)
