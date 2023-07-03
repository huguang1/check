# -*- coding: utf-8 -*-
# 18-12-27 20:35
# AUTHOR:xiaoli
import pytz
from django.core.serializers import json
from django.shortcuts import render
from django.views.generic import View
from PIL import Image, ImageDraw, ImageFont
from django.utils.six import BytesIO
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from account.models import *
from django.middleware.csrf import get_token
import time
import decimal
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
SECRET_KEY = 'ihkkeauf!%_&f2fq6c-=oqbspwy1-mm2a7no4n-sv!p-psln$('
import pickle, base64
import json
import datetime
from django.utils import timezone
import csv
import operator
# Create your views here.

"""
这个是django返回数据的统一格式。
0:成功
1:信息不完整
2:信息不正确
3:插入数据库不正确
4:查询数据库错误
"""


# 验证码
class VerifyCodeView(View):
    """
    这个验证码的功能是，后台生成随机数，保存在django的session中，同时将这个随机数做成图片，并增加一些噪点，
    传递给前端并展示出来。
    """
    def get(self, request):
        # 引入随机函数模块
        import random
        # 定义变量，用于画面的背景色、宽、高
        bgcolor = '#3D1769'
        width = 100
        height = 40
        # 创建画面对象
        im = Image.new('RGB', (width, height), bgcolor)
        # 创建画笔对象
        draw = ImageDraw.Draw(im)
        # 调用画笔的point()函数绘制噪点
        for i in range(0, 100):
            xy = (random.randrange(0, width), random.randrange(0, height))
            fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
            draw.point(xy, fill=fill)
        # 定义验证码的备选值
        str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
        # 随机选取4个值作为验证码
        rand_str = ''
        for i in range(0, 4):
            rand_str += str1[random.randrange(0, len(str1))]
        # 构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
        font = ImageFont.truetype('FreeMono.ttf', 33)  # linux
        # font = ImageFont.truetype('arial.ttf', 33)  # win7的
        # 构造字体颜色
        # 选取验证码的背景颜色
        fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
        # 绘制4个字
        draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
        draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
        draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
        draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
        # 释放画笔
        del draw
        # 存入session，用于做进一步验证
        request.session['verifycode'] = rand_str
        # 内存文件操作
        buf = BytesIO()
        # 将图片保存在内存中，文件类型为png
        im.save(buf, 'png')
        # 将内存中的图片数据返回给客户端，MIME类型为图片png
        return HttpResponse(buf.getvalue(), 'image/png')


# 登陆
class LoginView(View):
    """
    登陆主要是验证用户名和密码是否匹配，以及验证码是否输入正确，同时要实现记住用户名的功能。
    """
    def post(self, request):
        # 从请求体中获取到用户输入的信息
        username = request.POST['username']
        password = request.POST['password']
        yan_txt = request.POST['yan_txt']
        remember_num = request.POST['remember_num']
        # 如果用户名和密码和验证码没有同时获取到，则直接不通过
        if not (username and password and yan_txt):
            data = {'status': 1, 'msg': '数据不完整'}
            return JsonResponse(data)
        # 如果传入的验证码和session中存入的验证码不一致，则验证不通过
        if not yan_txt.lower() == request.session['verifycode'].lower():
            data = {'status': 2, 'msg': '验证码不正确'}
            return JsonResponse(data)
        # 使用django自带的函数来验证用户的用户名和密码
        user = authenticate(request, username=username, password=password)
        # 验证用户通过，再判断用户是否选择了记住用户名
        if user is not None:
            # 使用django自带的用户登陆函数，自带的记住用户名
            login(request, user)
            # 创建django返回对象
            data = {'status': 0, 'msg': '用户登陆成功'}
            response = JsonResponse(data)
            # 使用cookie来记住用户是否需要记住用户名
            if remember_num == 'on':
                response.set_cookie('remember', 1)
            else:
                response.set_cookie('remember', 0)
            # 使用日志收集系统来收集信息
            loginfo(request, username, "登录")
            return response
        else:
            # 用户登陆不成功，则直接返回账号或密码不正确
            data = {'status': 2, 'msg': '账户或密码不正确'}
            return JsonResponse(data)


# 登出
class LogoutView(View):
    """
    使用django的登出系统，删除django中用户的登陆信息
    """
    def post(self, request):
        # 使用日志来收集用户的登出信息
        loginfo(request, request.user.username, "登出")
        # 使用django自带的用户登出系统
        logout(request)
        data = {'status': 0, 'msg': '数据不完整'}
        return JsonResponse(data)


# 获取页面上的用户名信息
class SetUserNameView(View):
    """
    判断浏览器中是否存有用户的登陆信息，用户的登陆信息存储再session中，
    """
    def get(self, request):
        try:
            sessionid = request.COOKIES.get('sessionid')
            session = Session.objects.get(session_key=sessionid)
            uid = session.get_decoded().get('_auth_user_id')
            user = MyUser.objects.get(pk=uid)
        except Exception as e:
            data = {'status': 1, 'msg': '登陆失败，请重试！'}
            return JsonResponse(data)
        else:
            data = {'status': 0, 'username': user.username}
            response = JsonResponse(data)
            from urllib import parse
            un2 = parse.quote(user.username)
            response.set_cookie('username', un2)
            return response


# 判断用户使用者，同时确定首页银行
class GetUserPermissionBankcardView(View):
    def get(self, request):
        username = request.GET.get('username')
        try:
            user = MyUser.objects.get(username=username)
        except Exception as e:
            data = {'status': 1, 'msg': '查询用户失败，请重试！'}
            return JsonResponse(data)
        else:
            groups = AdminGroup.objects.all()
            for group in groups:
                users = group.group_user.all()
                for i in users:
                    if user.id == i.id:
                        if group.name == '出款管理员':
                            try:
                                bankcard = BankCard.objects.filter(editor_id=user.id).filter(Q(account_type=1) | Q(account_type=3)).filter(is_disable=False).first()
                                if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                                    bankcardtype = '入款银行'
                                else:
                                    bankcardtype = '出款银行'
                                data = {'status': 0, 'group': '出款管理员', 'bankcard': bankcard.name, 'bankcardtype': bankcardtype}
                                return JsonResponse(data)
                            except Exception as e:
                                data = {'tat': 205, 'group': '出款管理员', 'msg': 'addBank.html'}
                                return JsonResponse(data)
                        elif group.name == '入款管理员':
                            try:
                                bankcard = BankCard.objects.filter(editor_id=user.id).filter(Q(account_type=0) | Q(account_type=2)).filter(is_disable=False).first()
                                if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                                    bankcardtype = '入款银行'
                                else:
                                    bankcardtype = '出款银行'
                                data = {'status': 0, 'group': '入款管理员', 'bankcard': bankcard.name, 'bankcardtype': bankcardtype}
                                return JsonResponse(data)
                            except Exception as e:
                                data = {'tat': 205, 'group': '入款管理员', 'msg': 'addBank.html'}
                                return JsonResponse(data)
                        elif group.name == '总管理员':
                            try:
                                bankcard = BankCard.objects.filter(editor_id=user.id).filter(is_disable=False).first()
                                if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                                    bankcardtype = '入款银行'
                                else:
                                    bankcardtype = '出款银行'
                                data = {'status': 0, 'group': '总管理员', 'bankcard': bankcard.name, 'bankcardtype': bankcardtype}
                                return JsonResponse(data)
                            except Exception as e:
                                data = {'tat': 205, 'group': '总管理员', 'msg': 'addBank.html'}
                                return JsonResponse(data)
                        elif user.is_superuser == 1:
                            try:
                                bankcard = BankCard.objects.filter(editor_id=user.id).filter(is_disable=False).first()
                                if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                                    bankcardtype = '入款银行'
                                else:
                                    bankcardtype = '出款银行'
                                data = {'status': 0, 'group': '总管理员', 'bankcard': bankcard.name, 'bankcardtype': bankcardtype}
                                return JsonResponse(data)
                            except Exception as e:
                                data = {'tat': 205, 'group': '总管理员', 'msg': 'addBank.html'}
                                return JsonResponse(data)
                        else:
                            data = {'tat': 205, 'group': '入款管理员', 'msg': 'addBank.html'}
                            return JsonResponse(data)
            data = {'status': 1, 'msg': '未查询到用户相应的信息'}
            return JsonResponse(data)


"""
1. 银行卡信息
2. 总的对账数
3. 某张银行卡的记录
4. 某张银行卡的对账数
"""


# 获取银行列表
class BanksInfoView(View):
    def get(self, request):
        banks = Banks.objects.all()
        bank_name = []

        for bank in banks:
            bank_name.append(bank.name)
        data = {'status': 0, 'bank_name': bank_name}
        return JsonResponse(data)


# 获取银行卡列表
class BankCardView(View):
    def post(self, request):
        bankname = request.POST.get('bankname')
        bank = Banks.objects.filter(name=bankname)
        if bank.first():
            bankcards = bank.first().bankcard_set.all()
            bankcard_list = []
            for bankcard in bankcards:
                bankcard_list.append(bankcard.name)
            data = {'status': 0, 'bankcard_list': bankcard_list}
            return JsonResponse(data)
        else:
            data = {'status': 1, 'msg': '银行卡输入有误'}
            return JsonResponse(data)


# 获取银行卡列表
class GetBankcardListView(View):
    def get(self, request):
        username = request.GET.get('username')
        try:
            user = MyUser.objects.get(username=username)
        except Exception as e:
            data = {'status': 1, 'msg': '这个用户不存在'}
            return JsonResponse(data)
        banks = Banks.objects.all()
        bank_list = []
        for bank in banks:
            if user.is_superuser == 1:
                bankcards = BankCard.objects.filter(bank_type=bank).filter(Q(account_type=0) | Q(account_type=2)).filter(is_disable=False)
            else:
                bankcards = BankCard.objects.filter(bank_type=bank).filter(Q(account_type=0) | Q(account_type=2)).filter(is_disable=False).filter(editor=user)
            bankcard_list = []
            for bankcard in bankcards:
                bankcard_dict = {
                    'bankcard_name': bankcard.name
                }
                bankcard_list.append(bankcard_dict)
            bank_dict = {
                'bank_name': bank.name,
                'bankcard_list': bankcard_list
            }
            bank_list.append(bank_dict)
        data = {'status': 0, 'bank_list': bank_list}
        return JsonResponse(data)


# 获取出款银行卡列表
class GetBankcardListOutView(View):
    def get(self, request):
        username = request.GET.get('username')
        try:
            user = MyUser.objects.get(username=username)
        except Exception as e:
            data = {'status': 1, 'msg': '这个用户不存在'}
            return JsonResponse(data)
        banks = Banks.objects.all()
        bank_list = []
        for bank in banks:
            if user.is_superuser == 1:
                bankcards = BankCard.objects.filter(bank_type=bank).filter(Q(account_type=1) | Q(account_type=3)).filter(is_disable=False)
            else:
                bankcards = BankCard.objects.filter(bank_type=bank).filter(Q(account_type=1) | Q(account_type=3)).filter(is_disable=False).filter(editor=user)
            bankcard_list = []
            for bankcard in bankcards:
                bankcard_dict = {
                    'bankcard_name': bankcard.name
                }
                bankcard_list.append(bankcard_dict)
            bank_dict = {
                'bank_name': bank.name,
                'bankcard_list': bankcard_list
            }
            bank_list.append(bank_dict)
        data = {'status': 0, 'bank_list': bank_list}
        return JsonResponse(data)


# 获取银行卡的具体信息
class BankRecordView(View):
    """转账记录以及转账记录的统计"""
    def get(self, request):
        pIndex = request.GET.get('p')
        size = request.GET.get('size')
        bankcard = request.GET.get('bankcard')
        shuaixuan = request.GET.get('shuaixuan')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        show_time = request.COOKIES.get('show_time')
        try:
            year_int = 2019
            mon_int = int(show_time[0]+show_time[1])
            day_int = int(show_time[2]+show_time[3])
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        if(end_date):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date += datetime.timedelta(days=1)
            except Exception as e:
                data = {'status': 0, 'count': 0}
                return JsonResponse(data)
        if shuaixuan or start_date or end_date:
            if shuaixuan and start_date and end_date:
                records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
            elif shuaixuan:
                records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan)))
            elif start_date and end_date:
                records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
            else:
                data = {'status': 0, 'count': 0}
                return JsonResponse(data)
        else:
            try:
                records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int)).order_by('-sort', '-id')
            except Exception as e:
                records = None

        if records is None:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        count = records.count()
        if pIndex == '':
            pIndex = '1'
        try:
            pIndex = int(pIndex)
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        try:
            size = int(size)
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        p = Paginator(records, size)
        records = p.page(pIndex)
        num_pages = p.num_pages
        record_list = []
        for record in records:
            kk = {
                'id': record.id,
                'amount': record.amount,
                'type': record.type,
                'fees': record.fees,
                'remark': record.remark,
                'balance': record.balance,
                'sort': record.sort
            }
            record_list.append(kk)
        data = {'status': 0, 'count': count, 'record_list': record_list, 'num_pages': num_pages}
        return JsonResponse(data)


# 查询银行卡的具体信息
class SearchBankRecordView(View):
    """查询转账记录以及转账记录的统计"""
    def get(self, request):
        pIndex = request.GET.get('p')
        size = request.GET.get('size')
        bankcard = request.GET.get('bankcard')
        shuaixuan = request.GET.get('shuaixuan')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        show_time = request.COOKIES.get('show_time')
        yinhang = request.GET.get('yinhang')
        intype = request.GET.get('intype')
        try:
            year_int = 2019
            mon_int = int(show_time[0]+show_time[1])
            day_int = int(show_time[2]+show_time[3])
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        if(end_date):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date += datetime.timedelta(days=1)
            except Exception as e:
                data = {'status': 0, 'count': 0}
                return JsonResponse(data)
        if yinhang == '所有银行':
            bankcard_account_type = BankCard.objects.filter(name=bankcard).first().account_type
            bankcards = BankCard.objects.filter(account_type=bankcard_account_type)
            bankcard_id_list = []
            for bankcard in bankcards:
                bankcard_id_list.append(bankcard.id)
            if intype == '所有':
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan)))
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int)).order_by('-id')
            else:
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark__startswith=intype)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(remark__startswith=intype)
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark__startswith=intype)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int)).filter(remark__startswith=intype).order_by('-id')
        else:
            if intype == '所有':
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark__startswith=intype)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(remark__startswith=intype)
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark__startswith=intype)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int)).filter(remark__startswith=intype).order_by('-id')
            else:
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan)))
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int)).order_by('-id')

        if records is None:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        count = records.count()
        if pIndex == '':
            pIndex = '1'
        try:
            pIndex = int(pIndex)
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        try:
            size = int(size)
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        p = Paginator(records, size)
        records = p.page(pIndex)
        num_pages = p.num_pages
        record_list = []
        for record in records:
            kk = {
                'id': record.id,
                'amount': record.amount,
                'type': record.type,
                'fees': record.fees,
                'remark': record.remark,
                'balance': record.balance
            }
            record_list.append(kk)
        data = {'status': 0, 'count': count, 'record_list': record_list, 'num_pages': num_pages}
        return JsonResponse(data)


# 导出银行卡的记录
class SearchBankRecordDaochuView(View):
    def get(self, request):
        bankcard = request.GET.get('bankcard')
        shuaixuan = request.GET.get('shuaixuan')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        show_time = request.COOKIES.get('show_time')
        yinhang = request.GET.get('yinhang')
        intype = request.GET.get('intype')
        try:
            year_int = 2019
            mon_int = int(show_time[0] + show_time[1])
            day_int = int(show_time[2] + show_time[3])
        except Exception as e:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        if (end_date):
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                end_date += datetime.timedelta(days=1)
            except Exception as e:
                data = {'status': 0, 'count': 0}
                return JsonResponse(data)
        if yinhang == '所有银行':
            bankcard_account_type = BankCard.objects.filter(name=bankcard).first().account_type
            bankcards = BankCard.objects.filter(account_type=bankcard_account_type)
            bankcard_id_list = []
            for bankcard in bankcards:
                bankcard_id_list.append(bankcard.id)
            if intype == '所有':
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan)))
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                            create_time__gte=start_date).filter(create_time__lte=end_date)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                        create_time__startswith=datetime.date(year_int, mon_int, day_int)).order_by('-id')
            else:
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(
                            create_time__lte=end_date).filter(remark=intype)
                    elif shuaixuan:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(remark=intype)
                    elif start_date and end_date:
                        records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                            create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark=intype)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(bankcard_id__in=bankcard_id_list).filter(
                        create_time__startswith=datetime.date(year_int, mon_int, day_int)).filter(
                        remark=intype).order_by('-id')
        else:
            if intype == '所有':
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(
                            create_time__lte=end_date).filter(remark=intype)
                    elif shuaixuan:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(remark=intype)
                    elif start_date and end_date:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                            create_time__gte=start_date).filter(create_time__lte=end_date).filter(remark=intype)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(
                        bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                        create_time__startswith=datetime.date(year_int, mon_int, day_int)).filter(
                        remark=intype).order_by('-id')
            else:
                if shuaixuan or start_date or end_date:
                    if shuaixuan and start_date and end_date:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                            Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan))).filter(create_time__gte=start_date).filter(create_time__lte=end_date)
                    elif shuaixuan:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(Q(remark=shuaixuan) | Q(amount=decimal.Decimal(shuaixuan)))
                    elif start_date and end_date:
                        records = Record.objects.filter(
                            bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                            create_time__gte=start_date).filter(create_time__lte=end_date)
                    else:
                        data = {'status': 0, 'count': 0}
                        return JsonResponse(data)
                else:
                    records = Record.objects.filter(
                        bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(
                        create_time__startswith=datetime.date(year_int, mon_int, day_int)).order_by('-id')
        if records is None:
            data = {'status': 0, 'count': 0}
            return JsonResponse(data)
        response = HttpResponse(content_type='text/csv; charset=gbk')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % request.user.username
        writer = csv.writer(response)
        writer.writerow([bankcard, 'id', '转入', '转出', '手续费', '余额', '备注', '记录时间', '创建时间'])
        for record in records:
            if record.type == 0:
                writer.writerow(['', record.id, record.amount, 0, record.fees, record.balance, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
            else:
                writer.writerow(['', record.id, 0, record.amount, record.fees, record.remark, record.balance, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
        return response


# 获取银行卡的最新余额
def get_balance(*args):
    try:
        bankcard = BankCard.objects.get(name=args[0])
    except Exception as e:
        return '错误'
    else:
        try:
            if len(args)>1:
                end_time = timezone.datetime(args[1], args[2], args[3], 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=24)
                balance = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__lt=end_time).latest('id').balance
            else:
                balance = Record.objects.filter(bankcard_id=bankcard.id).latest('id').balance
        except Exception as e:
            balance = bankcard.initial_amount
            return balance, bankcard
        else:
            return balance, bankcard


# 添加银行卡记录
class AddBankRecordView(View):
    def post(self, request):
        amount = request.POST.get('amount')
        fees = request.POST.get('fees')
        remark = request.POST.get('remark')
        type = request.POST.get('type')
        bankcard = request.POST.get('bankcard')
        now_time = request.POST.get('now_time')
        if not fees:
            fees = 0
        if not remark:
            remark = ''
        try:
            year_int = 2019
            mon_int = int(now_time[0] + now_time[1])
            day_int = int(now_time[2] + now_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        balance, bankcard = get_balance(bankcard, year_int, mon_int, day_int)

        if balance == '错误':
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)

        if type == 'in':
            try:
                time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
                time = datetime.datetime.strptime(time, '%Y-%m-%d') + datetime.timedelta(hours=16)
                new_record = Record()
                new_record.amount = decimal.Decimal(amount)
                new_record.type = 0
                new_record.fees = decimal.Decimal(fees)
                new_record.remark = remark
                new_record.bankcard = bankcard
                new_record.create_time = time
                new_record.balance = balance + decimal.Decimal(amount) - decimal.Decimal(fees)
                new_record.save()
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__gt=time)
                for record in records:
                    record.balance += (decimal.Decimal(amount) - decimal.Decimal(fees))
                    record.save()
            except Exception as e:
                data = {'status': 1, 'msg': '保存数据失败，请重试！'}
                return JsonResponse(data)
            else:
                data = {'status': 0, 'msg': '数据保存成功！'}
                return JsonResponse(data)
        elif type == 'out':
            try:
                time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
                time = datetime.datetime.strptime(time, '%Y-%m-%d') + datetime.timedelta(hours=16)
                new_record = Record()
                new_record.amount = decimal.Decimal(amount)
                new_record.type = 1
                new_record.fees = decimal.Decimal(fees)
                new_record.remark = remark
                new_record.bankcard = bankcard
                new_record.create_time = time
                new_record.balance = balance - decimal.Decimal(amount) - decimal.Decimal(fees)
                new_record.save()
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__gt=time)
                for record in records:
                    record.balance += (- decimal.Decimal(amount) - decimal.Decimal(fees))
                    record.save()
            except Exception as e:
                data = {'status': 1, 'msg': '保存数据失败，请重试！'}
                return JsonResponse(data)
            else:
                data = {'status': 0, 'msg': '数据保存成功！'}
                return JsonResponse(data)
        else:
            data = {'status': 1, 'msg': '转账类型不对，请检查！'}
            return JsonResponse(data)


class GetTime(object):
    def __init__(self):
        self.date_list = []

    def get_list(self, str):
        if len(str) == 2:
            self.date_list.append(str[0:1])
            self.date_list.append(str[1:2])
        else:
            self.date_list.append('0')
            self.date_list.append(str)


# 获取首页的相关信息
class IndexInfoView(View):
    """时间信息以及总的信息以及登陆者的信息"""
    def get(self, request):
        a = time.localtime(time.time() - 12*60*60)
        mon_str = str(a.tm_mon)
        day_str = str(a.tm_mday)
        hour_str = str(a.tm_hour)
        min_str = str(a.tm_min)
        sec_str = str(a.tm_sec)
        nowdate = GetTime()
        nowdate.get_list(mon_str)
        nowdate.get_list(day_str)
        nowdate.get_list(hour_str)
        nowdate.get_list(min_str)
        nowdate.get_list(sec_str)
        data = {'status': 0, 'date_list': nowdate.date_list}
        response = JsonResponse(data)
        response.set_cookie('show_time', nowdate.date_list[0]+nowdate.date_list[1]+nowdate.date_list[2]+nowdate.date_list[3])
        return response


# 获取每月的天数
def monday():
    y = time.localtime(time.time()).tm_year
    mon_day = {1: '31',
               3: '31',
               4: '30',
               5: '31',
               6: '30',
               7: '31',
               8: '31',
               9: '30',
               10: '31',
               11: '30',
               12: '31'}
    if (y % 4) == 0 and (y % 400) != 0:
        mon_day[2] = '29'
    else:
        mon_day[2] = '28'
    return mon_day


# 增加时间视图
class DateAddView(View):
    """增加时间的视图"""
    def post(self, request):
        try:
            date_day = int(request.POST.get('date_play'))
            date_mon = int(request.POST.get('date_mon'))
        except Exception as e:
            data = {'status': 2, 'msg': '时间获取的不对，请重试！'}
            return JsonResponse(data)
        mon_day = monday()
        if date_mon != 12:
            if date_day < int(mon_day[date_mon]):
                date_day += 1
            else:
                date_day = 1
                date_mon += 1
        else:
            if date_day < int(mon_day[date_mon]):
                date_day += 1
            else:
                date_day = 1
                date_mon = 1
        day_new = GetTime()
        day_new.get_list(str(date_day))
        mon_new = GetTime()
        mon_new.get_list(str(date_mon))
        data = {'status': 0, 'day_list': day_new.date_list, 'mon_list':mon_new.date_list}
        response = JsonResponse(data)
        response.set_cookie('show_time', mon_new.date_list[0]+mon_new.date_list[1]+day_new.date_list[0]+day_new.date_list[1])
        return response


# 减少时间视图
class DateSubView(View):
    """减少时间的视图"""
    def post(self, request):
        try:
            date_day = int(request.POST.get('date_play'))
            date_mon = int(request.POST.get('date_mon'))
        except Exception as e:
            data = {'status': 2, 'msg': '时间获取的不对，请重试！'}
            return JsonResponse(data)
        mon_day = monday()
        if date_mon != 1:
            if date_day != 1:
                date_day -= 1
            else:
                date_mon -= 1
                date_day = int(mon_day[date_mon])
        else:
            if date_day != 1:
                date_day -= 1
            else:
                date_mon = 12
                date_day = 31
        day_new = GetTime()
        day_new.get_list(str(date_day))
        mon_new = GetTime()
        mon_new.get_list(str(date_mon))
        data = {'status': 0, 'day_list': day_new.date_list, 'mon_list':mon_new.date_list}
        response = JsonResponse(data)
        response.set_cookie('show_time', mon_new.date_list[0]+mon_new.date_list[1]+day_new.date_list[0]+day_new.date_list[1])
        return response


# 外转入记录
class TransferInView(View):
    """外转入记录"""
    def post(self, request):
        transfer_type = request.POST.get('transfer_type')
        transfer_amount = request.POST.get('transfer_amount')
        transfer_remark = request.POST.get('transfer_remark')
        bankcard = request.POST.get('bankcard')
        now_time = request.POST.get('now_time')
        try:
            year_int = 2019
            mon_int = int(now_time[0] + now_time[1])
            day_int = int(now_time[2] + now_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        balance, bankcard = get_balance(bankcard, year_int, mon_int, day_int)
        if balance == '错误':
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)
        try:
            time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
            time = datetime.datetime.strptime(time, '%Y-%m-%d') + datetime.timedelta(hours=16)
            new_record = Record()
            if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                new_record.amount = - decimal.Decimal(transfer_amount)
                new_record.type = 1
            else:
                new_record.amount = decimal.Decimal(transfer_amount)
                new_record.type = 0
            new_record.fees = 0
            new_record.remark += transfer_type + "@"
            if transfer_remark:
                new_record.remark += transfer_remark
            new_record.bankcard = bankcard
            new_record.create_time = time
            new_record.balance = balance + decimal.Decimal(transfer_amount)
            new_record.save()
            records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__gt=time)
            for record in records:
                record.balance += decimal.Decimal(transfer_amount)
                record.save()
        except Exception as e:
            data = {'status': 3, 'msg': '插入数据库不正确'}
            return JsonResponse(data)
        else:
            data = {'status': 0, 'msg': '插入数据成功'}
            return JsonResponse(data)


# 外转出记录
class TransferOutMoneyView(View):
    """外转出记录"""
    def post(self, request):
        transfer_type = request.POST.get('transfer_type')
        transfer_amount = request.POST.get('transfer_amount')
        waizhuanchu_fees = request.POST.get('waizhuanchu_fees')
        transfer_remark = request.POST.get('transfer_remark')
        bankcard = request.POST.get('bankcard')
        now_time = request.POST.get('now_time')
        try:
            year_int = 2019
            mon_int = int(now_time[0] + now_time[1])
            day_int = int(now_time[2] + now_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        balance, bankcard = get_balance(bankcard, year_int, mon_int, day_int)
        if balance == '错误':
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)
        if not waizhuanchu_fees:
            waizhuanchu_fees = 0
        try:
            time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
            time = datetime.datetime.strptime(time, '%Y-%m-%d') + datetime.timedelta(hours=16)
            new_record = Record()
            if (bankcard.account_type == 1) or (bankcard.account_type == 3):
                new_record.amount = - decimal.Decimal(transfer_amount)
                new_record.type = 0
            else:
                new_record.amount = decimal.Decimal(transfer_amount)
                new_record.type = 1
            new_record.balance = balance - decimal.Decimal(transfer_amount) - decimal.Decimal(waizhuanchu_fees)
            new_record.fees = decimal.Decimal(waizhuanchu_fees)
            new_record.remark += transfer_type + "@"
            if transfer_remark:
                new_record.remark += transfer_remark
            new_record.bankcard = bankcard
            new_record.create_time = time
            new_record.save()
            records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__gt=time)
            for record in records:
                record.balance -= (decimal.Decimal(transfer_amount) + decimal.Decimal(waizhuanchu_fees))
                record.save()
        except Exception as e:
            data = {'status': 3, 'msg': '插入数据库不正确'}
            return JsonResponse(data)
        else:
            data = {'status': 0, 'msg': '插入数据成功'}
            return JsonResponse(data)


# 获取银行卡里的余额
class GetBalanceView(View):
    """获取银行卡里的余额"""
    def post(self, request):
        bankcard = request.POST.get('bankcard')
        show_time = request.COOKIES.get('show_time')
        try:
            year_int = 2019
            mon_int = int(show_time[0] + show_time[1])
            day_int = int(show_time[2] + show_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        balance, bankcard = get_balance(bankcard, year_int, mon_int, day_int)
        if balance == '错误':
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)

        data = {'status': 0, 'balance': balance, 'msg': '查询数据成功'}
        return JsonResponse(data)


# 获取外转出的种类
class WaiBankcardView(View):
    """获取外转出的种类"""
    def get(self, request):
        bank_type = request.GET.get('bank_type')
        banks_type_dict = {
            '入款': 0,
            '出款': 1,
            '入款中转': 2,
            '出款中转': 3,
        }
        try:
            bankcards = BankCard.objects.filter(account_type=banks_type_dict[bank_type])
        except Exception as e:
            data = {'status': 4, 'msg': '查询数据库失败！'}
            return JsonResponse(data)
        bankcard_list = []
        for bankcard in bankcards:
            bankcard_list.append(bankcard.name)
        data = {'status': 0, 'bankcard_list': bankcard_list}
        return JsonResponse(data)


# 外转出给其他银行的视图
class TransferOutView(View):
    def post(self, request):
        wai_bankcard = request.POST.get('wai_bankcard')
        chu_amount = request.POST.get('chu_amount')
        wai_bankcard_type = request.POST.get('wai_bankcard_type')
        bankcard = request.POST.get('bankcard')
        chu_fees = request.POST.get('chu_fees')
        now_time = request.POST.get('now_time')
        try:
            year_int = 2019
            mon_int = int(now_time[0] + now_time[1])
            day_int = int(now_time[2] + now_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        wai_balance, wai_bankcard = get_balance(wai_bankcard, year_int, mon_int, day_int)
        balance, bankcard = get_balance(bankcard, year_int, mon_int, day_int)
        if not chu_fees:
            chu_fees = 0
        if (balance == '错误') or (wai_bankcard == '错误') or (wai_bankcard == bankcard):
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)
        try:
            now_time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d') + datetime.timedelta(hours=16)
            out_record = Record()
            out_record.remark = wai_bankcard.name
            out_record.bankcard = bankcard
            out_record.create_time = now_time
            out_record.fees = decimal.Decimal(chu_fees)
            # 出款银行转出款银行，一个标记为入款负数，一个标记为入款正数

            a = bankcard.account_type
            print(bankcard.account_type)
            if bankcard.account_type == 1 or bankcard.account_type == 3:
                out_record.amount = - decimal.Decimal(chu_amount)
                out_record.type = 0
                out_record.balance = balance - decimal.Decimal(chu_amount) - decimal.Decimal(chu_fees)
            else:
                out_record.amount = decimal.Decimal(chu_amount)
                out_record.type = 1
                out_record.balance = balance - decimal.Decimal(chu_amount) - decimal.Decimal(chu_fees)
            out_record.save()
            records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__gt=now_time)
            for record in records:
                record.balance -= (decimal.Decimal(chu_amount) + decimal.Decimal(chu_fees))
                record.save()
        except Exception as e:
            data = {'status': 3, 'msg': '插入数据库不正确'}
            return JsonResponse(data)
        try:
            new_record = Record()
            new_record.remark += bankcard.name
            new_record.remark += '@'
            new_record.remark += str(out_record.id)
            new_record.bankcard = wai_bankcard
            new_record.create_time = now_time
            new_record.fees = 0
            # 入款银行转给入款银行，一个记为转出正数，一个记为转出负数
            if wai_bankcard.account_type == 2 or wai_bankcard.account_type == 0:
                new_record.amount = -decimal.Decimal(chu_amount)
                new_record.type = 1
                new_record.balance = wai_balance + decimal.Decimal(chu_amount)
            else:
                new_record.amount = decimal.Decimal(chu_amount)
                new_record.type = 0
                new_record.balance = wai_balance + decimal.Decimal(chu_amount)
            new_record.save()
            records = Record.objects.filter(bankcard_id=wai_bankcard.id).filter(create_time__gt=now_time)
            for record in records:
                record.balance += decimal.Decimal(chu_amount)
                record.save()
        except Exception as e:
            data = {'status': 3, 'msg': '插入数据库不正确'}
            return JsonResponse(data)
        try:
            out_record.remark += '@'
            out_record.remark += str(new_record.id)
            a = out_record.remark
            out_record.save()
        except Exception as e:
            data = {'status': 3, 'msg': '插入数据库不正确'}
            return JsonResponse(data)
        data = {'status': 0, 'msg': '插入数据成功'}
        return JsonResponse(data)


# 删除银行卡记录
class DeleteRecordView(View):
    # 删除银行卡记录
    def post(self, request):
        id = request.POST.get('id')
        try:
            delete_record = Record.objects.get(id=id)
        except Exception as e:
            data = {'status': 2, 'msg': '传递的金额不正确'}
            return JsonResponse(data)
        change_records = Record.objects.filter(bankcard=delete_record.bankcard).filter(Q(create_time__gt=delete_record.create_time)|Q(create_time__exact=delete_record.create_time, id__gt=id))

        if delete_record.type == 0:
            change_amount = delete_record.amount - delete_record.fees
            for change_record in change_records:
                change_record.balance -= change_amount
                change_record.save()
            try:
                other_record = Record.objects.get(id=delete_record.remark.split('@')[1])
            except Exception as e:
                pass
            else:
                other_change_records = Record.objects.filter(bankcard=other_record.bankcard).filter(Q(create_time__gt=other_record.create_time)|Q(create_time__exact=other_record.create_time, id__gt=other_record.id))
                for other_change_record in other_change_records:
                    if other_record.type == 0:
                        other_change_record.balance -= other_record.amount
                        other_change_record.balance += other_record.fees
                    else:
                        other_change_record.balance += (other_record.amount + other_record.fees)
                    other_change_record.save()
                other_record.delete()
            delete_record.delete()
            data = {'status': 0, 'msg': '删除成功'}
            return JsonResponse(data)
        else:
            change_amount = delete_record.amount + delete_record.fees
            for change_record in change_records:
                change_record.balance += change_amount
                change_record.save()
            try:
                other_record = Record.objects.get(id=delete_record.remark.split('@')[1])
            except Exception as e:
                pass
            else:
                other_change_records = Record.objects.filter(bankcard=other_record.bankcard).filter(Q(create_time__gt=other_record.create_time)|Q(create_time__exact=other_record.create_time, id__gt=other_record.id))
                change_amount = other_record.amount
                for other_change_record in other_change_records:
                    if other_record.type == 1:
                        other_change_record.balance += change_amount + other_record.fees
                    else:
                        other_change_record.balance -= change_amount
                    other_change_record.save()
                other_record.delete()
            delete_record.delete()
            data = {'status': 0, 'msg': '删除成功'}
            return JsonResponse(data)


# 对一张银行卡的数据统计
class GetCheckBankcardView(View):
    def post(self, request):
        bankcard = request.POST.get('bankcard')
        try:
            bankcard = BankCard.objects.get(name=bankcard)
        except Exception as e:
            data = {'status': 4, 'msg': '查询银行卡失败'}
            return JsonResponse(data)
        data = {'status': 0}
        return JsonResponse(data)


# 获取银行卡当天的对账额
class CheckNowBankcardView(View):
    def get(self, request):
        bankcard = request.GET.get('bankcard')
        show_time = request.COOKIES.get('show_time')
        try:
            year_int = 2019
            mon_int = int(show_time[0]+show_time[1])
            day_int = int(show_time[2]+show_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        try:
            end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
            record = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__lt=end_time).latest('id')
        except Exception as e:
            past_balance = 0
        else:
            past_balance = record.balance
        try:
            records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
        except Exception as e:
            # data = {'status': 1, 'msg': '查看当前银行卡失败'}
            # return JsonResponse(data)
            msg = {
                'past_balance': past_balance,
                'now_balance': past_balance,
                'in_amount': 0,
                'fees': 0,
                'total_in_amount': 0
            }
            data = {'status': 0, 'msg': msg}
            return JsonResponse(data)

        if not records:
            msg = {
                'past_balance': past_balance,
                'now_balance': past_balance,
                'in_amount': 0,
                'fees': 0,
                'total_in_amount': 0
            }
            data = {'status': 0, 'msg': msg}
            return JsonResponse(data)
        now_balance = 0

        if records:
            now_balance += records.latest('id').balance
        in_amount = 0
        fees = 0
        total_in_amount = 0
        types = [tf_type.name for tf_type in TransferType.objects.filter(transfer_type=0)]
        for record in records:
            fees += record.fees
            if record.type == 0 and record.remark not in types:
                in_amount += record.amount
        total_in_amount += in_amount - fees
        """
        past_balance: 昨日原余额
        now_balance: 余额
        in_amount: 入款
        total_in_amount: 实入款
        fees: 手续费
        """
        msg = {
            'past_balance': past_balance,
            'now_balance': now_balance,
            'in_amount': in_amount,
            'fees': fees,
            'total_in_amount': total_in_amount
        }
        data = {'status': 0, 'msg': msg}
        return JsonResponse(data)


# 获取银行卡当天的对账额
class CheckNowBankcardOutView(View):
    def get(self, request):
            bankcard = request.GET.get('bankcard')
            show_time = request.COOKIES.get('show_time')
            try:
                year_int = 2019
                mon_int = int(show_time[0] + show_time[1])
                day_int = int(show_time[2] + show_time[3])
            except Exception as e:
                data = {'status': 1, 'msg': '没有获取到时间的信息'}
                return JsonResponse(data)
            try:
                end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
                record = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__lt=end_time).latest('id')
            except Exception as e:
                past_balance = 0
            else:
                past_balance = record.balance
            try:
                records = Record.objects.filter(bankcard_id=BankCard.objects.filter(name=bankcard).first().id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
            except Exception as e:
                data = {'status': 1, 'msg': '查看当前银行卡失败'}
                return JsonResponse(data)
            if not records:
                msg = {
                    'past_balance': past_balance,
                    'now_balance': past_balance,
                    'out_amount': 0,
                    'fees': 0,
                    'total_out_amount': 0
                }
                data = {'status': 0, 'msg': msg}
                return JsonResponse(data)
            now_balance = 0
            if records:
                now_balance += records.latest('id').balance
            out_amount = 0
            fees = 0
            total_out_amount = 0
            for record in records:
                fees += record.fees
                if record.type == 1:
                    out_amount += record.amount
            total_out_amount += out_amount - fees
            """
            past_balance: 昨日原余额
            now_balance: 余额
            in_amount: 入款
            total_in_amount: 实入款
            fees: 手续费
            """
            msg = {
                'past_balance': past_balance,
                'now_balance': now_balance,
                'out_amount': out_amount,
                'fees': fees,
                'total_out_amount': total_out_amount
            }
            data = {'status': 0, 'msg': msg}
            return JsonResponse(data)


# 获取总的银行卡的对账额度
class CheckAllBankcardView(View):
    def get(self, request):
        show_time = request.COOKIES.get('show_time')
        try:
            year_int = 2019
            mon_int = int(show_time[0] + show_time[1])
            day_int = int(show_time[2] + show_time[3])
        except Exception as e:
            data = {'status': 1, 'msg': '没有获取到时间的信息'}
            return JsonResponse(data)
        past_balance = 0
        now_balance = 0
        in_amount = 0
        fees = 0
        total_in_amount = 0
        bankcards = BankCard.objects.filter(account_type=0)
        for bankcard in bankcards:  # 获取到所有的银行卡
            try:
                end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
                record = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__lt=end_time).latest('id')   # 获取到这张银行卡之前的最大记录
            except Exception as e:
                if bankcard.initial_amount != 0:
                    past_balance += bankcard.initial_amount
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                if records:
                    now_balance += records.latest('id').balance
                for record in records:
                    fees += record.fees
                    if record.type == 0:
                        in_amount += record.amount
            else:
                past_balance += record.balance
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                if records:
                    now_balance += records.latest('id').balance
                else:
                    now_balance += record.balance
                for record in records:
                    fees += record.fees
                    if record.type == 0:
                        in_amount += record.amount
        total_in_amount += in_amount - fees

        zhong_past_balance = 0
        zhong_now_balance = 0
        zhong_in_amount = 0
        zhong_fees = 0
        zhong_total_in_amount = 0
        zhong_bankcards = BankCard.objects.filter(account_type=2)
        for bankcard in zhong_bankcards:
            try:
                end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
                record = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__lt=end_time).latest('id')
            except Exception as e:
                if bankcard.initial_amount != 0:
                    zhong_past_balance += bankcard.initial_amount
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                if records:
                    zhong_now_balance += records.latest('id').balance
                for record in records:
                    zhong_fees += record.fees
                    if record.type == 0:
                        zhong_in_amount += record.amount
            else:
                zhong_past_balance += record.balance
                records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                if records:
                    zhong_now_balance += records.latest('id').balance
                else:
                    zhong_now_balance += record.balance
                for record in records:
                    zhong_fees += record.fees
                    if record.type == 0:
                        zhong_in_amount += record.amount
        zhong_total_in_amount += zhong_in_amount - zhong_fees
        msg = {
            'past_balance': past_balance, # 昨天总余额  入款
            'now_balance': now_balance,
            'in_amount': in_amount,
            'fees': fees,
            'total_in_amount': total_in_amount,
            'zhong_past_balance': zhong_past_balance, # 昨天总余额 中转
            'zhong_now_balance': zhong_now_balance,
            'zhong_in_amount': zhong_in_amount,
            'zhong_fees': zhong_fees,
            'zhong_total_in_amount': zhong_total_in_amount
        }
        data = {'status': 0, 'msg': msg}
        return JsonResponse(data)


# 获取总的银行卡的对账额度
class CheckAllBankcardOutView(View):
    def get(self, request):
            show_time = request.COOKIES.get('show_time')
            try:
                year_int = 2019
                mon_int = int(show_time[0] + show_time[1])
                day_int = int(show_time[2] + show_time[3])
            except Exception as e:
                data = {'status': 1, 'msg': '没有获取到时间的信息'}
                return JsonResponse(data)
            past_balance = 0
            now_balance = 0
            out_amount = 0
            fees = 0
            total_out_amount = 0
            bankcards = BankCard.objects.filter(account_type=1)
            types = [tf_type.name for tf_type in TransferType.objects.filter(transfer_type=0)]
            for bankcard in bankcards:
                try:
                    end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
                    record = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__lt=end_time).latest('id')
                except Exception as e:
                    if bankcard.initial_amount != 0:
                        past_balance += bankcard.initial_amount
                    records = Record.objects.filter(bankcard_id=bankcard.id).filter(
                        create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if records:
                        now_balance += records.latest('id').balance
                    for record in records:
                        fees += record.fees
                        if record.type == 1 and record.remark not in types:
                            out_amount += record.amount
                else:
                    past_balance += record.balance
                    records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if records:
                        now_balance += records.latest('id').balance
                    else:
                        now_balance += record.balance
                    for record in records:
                        fees += record.fees
                        if record.type == 1 and record.remark not in types:
                            out_amount += record.amount
            total_out_amount += (out_amount - fees)
            zhong_past_balance = 0
            zhong_now_balance = 0
            zhong_out_amount = 0
            zhong_fees = 0
            zhong_total_out_amount = 0
            zhong_bankcards = BankCard.objects.filter(account_type=3)
            for bankcard in zhong_bankcards:
                try:
                    end_time = timezone.datetime(year_int, mon_int, day_int, 0, tzinfo=pytz.UTC) + datetime.timedelta(hours=4)
                    record = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__lt=end_time).latest('id')
                except Exception as e:
                    if bankcard.initial_amount != 0:
                        zhong_past_balance += bankcard.initial_amount
                    records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if records:
                        zhong_now_balance += records.latest('id').balance
                    for record in records:
                        zhong_fees += record.fees
                        if record.type == 1 and record.remark not in types:
                            zhong_out_amount += record.amount
                else:
                    zhong_past_balance += record.balance
                    records = Record.objects.filter(bankcard_id=bankcard.id).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if records:
                        zhong_now_balance += records.latest('id').balance
                    else:
                        zhong_now_balance += record.balance
                    for record in records:
                        zhong_fees += record.fees
                        if record.type == 1 and record.remark not in types:
                            zhong_out_amount += record.amount
            zhong_total_out_amount += (zhong_out_amount - zhong_fees)
            msg = {
                'past_balance': past_balance,
                'now_balance': now_balance,
                'out_amount': out_amount,
                'fees': fees,
                'total_out_amount': total_out_amount,
                'zhong_past_balance': zhong_past_balance,
                'zhong_now_balance': zhong_now_balance,
                'zhong_out_amount': zhong_out_amount,
                'zhong_fees': zhong_fees,
                'zhong_total_out_amount': zhong_total_out_amount
            }
            data = {'status': 0, 'msg': msg}
            return JsonResponse(data)


# 最后的对账图的入款对账部分
class CheckAccountView(View):
    def post(self, request):
        date_list = request.POST.get('date_list')
        try:
            year_int = 2019
            mon_int = int(date_list[0:2])
            day_int = int(date_list[2:4])
        except Exception as e:
            data = {'status': 1, 'msg': '时间解析错误'}
            return JsonResponse(data)
        users = MyUser.objects.all()
        user_balance = []
        all_in_amount = 0
        all_fees = 0
        all_now_balance = 0
        all_out_amount = 0
        all_new_amount = 0
        all_remove = 0
        all_transit = 0
        for user in users:
            # 根据每个用户查询出每个用户相对应的银行卡
            bankcards = BankCard.objects.filter(editor=user).filter(Q(account_type=0) | Q(account_type=2))
            in_amount = 0
            fees = 0
            now_balance = 0
            out_amount = 0
            new_amount = 0
            remove = 0
            transit = 0
            if bankcards:
                for bankcard in bankcards:
                    # 查询银行卡今天是否有记录，记录银行卡最后一条记录的余额
                    records = Record.objects.filter(bankcard=bankcard).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if records:
                        now_balance += records.latest('id').balance
                    else:
                        # 如果银行卡今天没有记录，则必须查找银行卡今天之前的所有记录，来查看银行卡最后的余额
                        allrecords = Record.objects.filter(bankcard=bankcard).filter(create_time__lt=datetime.date(year_int, mon_int, day_int))
                        if allrecords:
                            now_balance += allrecords.latest('id').balance
                        else:
                            # 如果银行卡之前也没有余额，那么查看银行卡最初的余额
                            if bankcard.initial_amount != 0:
                                # 如果银行卡的初始余额不为零
                                now_balance += bankcard.initial_amount
                    # 1.所有的转入都是实际用户转入的
                    for record in records.filter(type=0).filter(bankcard__account_type=0):
                        in_amount += record.amount
                        fees += record.fees
                    # 4.获取外转入的钱
                    q2 = Q()
                    q2.connector = 'OR'
                    if TransferType.objects.filter(transfer_type=0):
                        for i in TransferType.objects.filter(transfer_type=0):
                            q2.children.append(('remark__startswith', i.name+'@'))
                        for record in records.filter(q2).filter(type=1):
                            new_amount += record.amount
                    # 3.获取外转出的钱
                    q1 = Q()
                    q1.connector = 'OR'
                    if TransferType.objects.filter(transfer_type=1):
                        for i in TransferType.objects.filter(transfer_type=1):
                            q1.children.append(('remark__startswith', i.name+'@'))
                        for record in records.filter(type=1).filter(q1):
                            out_amount += record.amount + record.fees
                    # 2.获取到中转的手续费
                    for record in records.filter(type=1).exclude(q2).exclude(q1).exclude(remark__startswith='移除@'):
                        if record.fees:
                            transit += record.fees
                    # 5.获取到移除的钱
                    for record in records.filter(type=1).filter(remark__startswith='移除@'):
                        remove += record.amount
                all_in_amount += in_amount
                all_fees += fees
                all_now_balance += now_balance
                all_out_amount += out_amount
                all_new_amount += new_amount
                all_remove += remove
                all_transit += transit
                """
                in_amount:转入
                real_in_amount:实际转入
                fees:手续费
                now_balance:现余额
                out_amount:外转出
                new_amount:外转入
                remove:移除
                transit: 中转，实际就是中转的手续费
                """
                userinfo = {
                    'in_amount': in_amount,
                    'real_in_amount': in_amount -fees,
                    'fees': fees,
                    'now_balance': now_balance,
                    'user': user.username,
                    'out_amount': out_amount,
                    'new_amount': new_amount,
                    'remove': remove,
                    'transit': transit
                }
                user_balance.append(userinfo)
        userinfo = {
            'in_amount': all_in_amount,
            'real_in_amount': all_in_amount - all_fees,
            'fees': all_fees,
            'now_balance': all_now_balance,
            'user': 'total',
            'out_amount': all_out_amount,
            'new_amount': all_new_amount,
            'remove': all_remove,
            'transit': all_transit
        }
        user_balance.append(userinfo)
        data = {'status': 0, 'user_balance': user_balance}
        return JsonResponse(data)


# 对账数据渲染视图之出款
class CheckOutView(View):
    def post(self, request):
        date_list = request.POST.get('date_list')
        try:
            year_int = 2019
            mon_int = int(date_list[0:2])
            day_int = int(date_list[2:4])
        except Exception as e:
            data = {'status': 1, 'msg': '时间解析错误'}
            return JsonResponse(data)
        # outward_group = AdminGroup.objects.get(name='出款管理员')
        # outward_users = outward_group.group_user.all()
        outward_users = MyUser.objects.all()
        userdata = []
        ba = 0  # 余额
        am = 0  # 出款
        fe = 0  # 手续费
        ne = 0  # 新增
        ou = 0  # 支出
        re = 0  # 移出
        tr = 0  # 中转
        for outward_user in outward_users:
            balance = 0  # 余额
            amount = 0  # 出款
            fees = 0  # 手续费
            new = 0  # 新增
            out = 0  # 支出
            remove = 0  # 移出
            transit = 0  #　中转
            # 查询出每个用户的所有银行卡的信息
            outward_cards = BankCard.objects.filter(editor=outward_user).filter(Q(account_type=1) | Q(account_type=3))
            if outward_cards:
                for outward_card in outward_cards:
                    # 查看每张银行卡，对账天里面的转账记录
                    records = Record.objects.filter(bankcard=outward_card).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
                    if not records.exists():
                        # 如果银行卡今天没有记录，则必须查找银行卡今天之前的所有记录，来查看银行卡最后的余额
                        allrecords = Record.objects.filter(bankcard=outward_card).filter(create_time__lt=datetime.date(year_int, mon_int, day_int))
                        if allrecords:
                            balance += allrecords.latest('id').balance
                        else:
                            # 如果银行卡之前也没有余额，那么查看银行卡最初的余额
                            if outward_card.initial_amount != 0:
                                # 如果银行卡的初始余额不为零
                                balance += outward_card.initial_amount
                        continue
                    balance += records.last().balance
                    # 1.统计新增金额
                    q1 = Q()
                    q1.connector = 'OR'
                    if TransferType.objects.filter(transfer_type=0):
                        for i in TransferType.objects.filter(transfer_type=0):
                            q1.children.append(('remark__startswith', i.name+'@'))
                        in_records = records.filter(type=0).filter(q1)
                        for in_record in in_records:
                            new += in_record.amount
                    # 2.统计出款金额
                    normal_records = records.filter(type=1).filter(bankcard__account_type=1)
                    for normal_record in normal_records:
                        amount += normal_record.amount
                        fees += normal_record.fees
                    # 3.统计费用
                    q2 = Q()
                    q2.connector = 'OR'
                    if TransferType.objects.filter(transfer_type=1):
                        for i in TransferType.objects.filter(transfer_type=1):
                            q2.children.append(('remark__startswith', i.name+'@'))
                        out_records = records.filter(type=0).filter(q2)
                        for out_record in out_records:
                            if out_record.fees:
                                out += (out_record.amount - out_record.fees)
                            else:
                                out += out_record.amount
                    # 5.统计中转,只统计中转的手续费
                    for record in records.filter(type=0).exclude(q1).exclude(q2).exclude(remark__startswith='移除@'):
                        if record.fees:
                            transit += record.fees
                    # 4.统计移除金额
                    remove_records = records.filter(type=0).filter(remark__startswith='移除@')
                    for remove_record in remove_records:
                        remove += remove_record.amount
                user_obj = {
                    "name": outward_user.username,
                    "real": amount + fees,
                    "amount": amount,
                    "balance": balance,
                    "fees": fees,
                    "out": out,
                    "new": new,
                    "remove": remove,
                    "transit": transit
                }
                userdata.append(user_obj)
                ba += balance  # 余额
                am += amount  # 出款
                fe += fees  # 手续费
                ne += new  # 新增
                ou += out  # 支出
                re += remove  # 移出
                tr += transit  # 中转
        userdata.append({
            "name": 'total',
            "real": am + fe,
            "amount": am,
            "balance": ba,
            "fees": fe,
            "out": ou,
            "new": ne,
            "remove": re,
            "transit": tr
        })
        context = {
            "status": 0,
            "inf": userdata
        }
        return JsonResponse(context)


# 银行卡中的移除
class RemoveAmountView(View):
    def post(self, request):
        amount = request.POST.get('chu_amount')
        remark = request.POST.get('chu_remark')
        bankcard = request.POST.get('bankcard')
        now_time = request.POST.get('now_time')
        balance, bankcard = get_balance(bankcard)
        if balance == '错误':
            data = {'status': 2, 'msg': '传递的参数错误，请重试！'}
            return JsonResponse(data)
        try:
            now_time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d') + datetime.timedelta(hours=16)
            new_record = Record()
            if (bankcard.account_type == 0) or (bankcard.account_type == 2):
                new_record.amount = decimal.Decimal(amount)
                new_record.type = 1
            else:
                new_record.amount = - decimal.Decimal(amount)
                new_record.type = 0
            new_record.fees = 0
            new_record.remark = '移除@'
            if remark:
                new_record.remark += remark
            new_record.bankcard = bankcard
            new_record.create_time = now_time
            new_record.balance = balance - decimal.Decimal(amount)
            new_record.save()
        except Exception as e:
            data = {'status': 1, 'msg': '保存数据失败，请重试！'}
            return JsonResponse(data)
        else:
            data = {'status': 0, 'msg': '数据保存成功！'}
            return JsonResponse(data)


# 一键对账功能
class ReconciliaView(View):
    def post(self, request):
        depositbalance = request.POST.get('depositbalance')  # 入款线内余额
        nowbalance = request.POST.get('nowbalance')  # 现余额
        outamount = request.POST.get('outamount')  # 外转出
        realinamount = request.POST.get('realinamount')  # 实入款
        remove = request.POST.get('remove')  # 移除
        newamount = request.POST.get('newamount')  # 外转入，新增
        transit = request.POST.get('transit')  # 中转手续费
        # 转出银行卡相关的
        re = request.POST.get('re')  # 实出款
        ba = request.POST.get('ba')  # 现余额
        out = request.POST.get('out')  # 费用，包含转出给小金库，大金库，各种费用
        inamount = request.POST.get('inamount')  # 新增，包含在线
        rm = request.POST.get('rm')  # 移除
        tr = request.POST.get('tr')  # 中转手续费
        if not depositbalance:
            depositbalance = 0
        try:
            depositbalance = decimal.Decimal(depositbalance)
            nowbalance = decimal.Decimal(nowbalance)
            outamount = decimal.Decimal(outamount)
            realinamount = decimal.Decimal(realinamount)
            remove = decimal.Decimal(remove)
            newamount = decimal.Decimal(newamount)
            transit = decimal.Decimal(transit)
            re = decimal.Decimal(re)
            ba = decimal.Decimal(ba)
            out = decimal.Decimal(out)
            inamount = decimal.Decimal(inamount)
            rm = decimal.Decimal(rm)
            tr = decimal.Decimal(tr)
        except Exception as e:
            data = {'status': 1, 'msg': '数据转换错误，请重试'}
            return JsonResponse(data)
        total_balance = depositbalance-nowbalance-outamount+realinamount-transit-remove-newamount-re-ba+out+inamount+rm-tr
        data = {'status': 0, 'total_balance': total_balance}
        return JsonResponse(data)


# 获取昨天的银行卡总余额
class GetYesterdayBalanceView(View):
    def get(self, request):
        date_list = request.GET.get('date_list')
        try:
            year_int = 2019
            mon_int = int(date_list[0:2])
            day_int = int(date_list[2:4])
        except Exception as e:
            data = {'status': 1, 'msg': '时间解析错误'}
            return JsonResponse(data)
        balances = YesterdayBalance.objects.filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
        if balances:
            balance = balances.latest('id').balance
        else:
            balance = 0
        data = {'status': 0, 'balance': balance}
        return JsonResponse(data)


# 更改昨天银行卡的总余额
class ChangeYesterDayBalanceView(View):
    def post(self, request):
        try:
            sessionid = request.COOKIES.get('sessionid')
            session = Session.objects.get(session_key=sessionid)
            uid = session.get_decoded().get('_auth_user_id')
            user = MyUser.objects.get(pk=uid)
        except Exception as e:
            data = {'status': 1, 'msg': '登陆失败，请重试！'}
            return JsonResponse(data)
        else:
            if user.is_superuser == 1:
                money = request.POST.get('money')
                now_time = request.POST.get('now_time')
                try:
                    money = decimal.Decimal(money)
                except Exception as e:
                    data = {'status': 2, 'msg': '获取的金额数据不对，请重试！'}
                    return JsonResponse(data)
                try:
                    time = '2019-' + now_time[0:2] + '-' + now_time[2:4]
                    time = datetime.datetime.strptime(time, '%Y-%m-%d') + datetime.timedelta(hours=16)
                    yesterdaybalance = YesterdayBalance()
                    yesterdaybalance.balance = money
                    yesterdaybalance.create_time = time
                    yesterdaybalance.save()
                    data = {'status': 0, 'msg': '修改金额正确'}
                    return JsonResponse(data)
                except Exception as e:
                    data = {'status': 2, 'msg': '插入数据不对，请重试！'}
                    return JsonResponse(data)
            else:
                data = {'status': 2, 'msg': '不是超级用户，不能够修改！'}
                return JsonResponse(data)


# 实现一键下载对账报表
class DownloadCheckView(View):
    def get(self, request):
        try:
            year_int = 2019
            day_int = int(request.GET.get('date_day'))
            mon_int = int(request.GET.get('date_mon'))
        except Exception as e:
            data = {'status': 2, 'msg': '时间获取的不对，请重试！'}
            return JsonResponse(data)
        username = request.GET.get('username')
        try:
            user = MyUser.objects.get(username=username)
        except Exception as e:
            data = {'status': 1, 'msg': '这个用户不存在'}
            return JsonResponse(data)
        bankcards = BankCard.objects.filter(editor=user)
        response = HttpResponse(content_type='text/csv; charset=gbk')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % request.user.username
        writer = csv.writer(response)
        past_balance = 0
        realamount = 0
        alltotalamount = 0
        allfees = 0
        now_balance = 0
        for bankcard in bankcards:
            records = Record.objects.filter(bankcard=bankcard).filter(create_time__startswith=datetime.date(year_int, mon_int, day_int))
            if records:
                now_balance += records.latest('id').balance
                allrecords = Record.objects.filter(bankcard=bankcard).filter(create_time__lt=datetime.date(year_int, mon_int, day_int))
                if allrecords:
                    past_balance += allrecords.latest('id').balance
                else:
                    # 如果银行卡之前也没有余额，那么查看银行卡最初的余额
                    if bankcard.initial_amount != 0:
                        # 如果银行卡的初始余额不为零
                        past_balance += bankcard.initial_amount
            else:
                # 如果银行卡今天没有记录，则必须查找银行卡今天之前的所有记录，来查看银行卡最后的余额
                allrecords = Record.objects.filter(bankcard=bankcard).filter(create_time__lt=datetime.date(year_int, mon_int, day_int))
                if allrecords:
                    now_balance += allrecords.latest('id').balance
                    past_balance += allrecords.latest('id').balance
                else:
                    # 如果银行卡之前也没有余额，那么查看银行卡最初的余额
                    if bankcard.initial_amount != 0:
                        # 如果银行卡的初始余额不为零
                        now_balance += bankcard.initial_amount
                        past_balance += bankcard.initial_amount
            # 如果银行为入款银行
            if bankcard.account_type == 0:
                writer.writerow([bankcard, 'id', '入款', '转出', '手续费', '备注', '记录时间', '创建时间'])
                totalamount = 0
                fees = 0
                for record in records:
                    if record.type == 0:
                        writer.writerow(['', record.id, record.amount, '', record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                    else:
                        writer.writerow(['', record.id, '', record.amount, record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                for record in records.filter(type=0):
                    totalamount += record.amount
                    fees += record.fees
                alltotalamount += totalamount
                allfees += fees
                realamount += (totalamount - fees)

            # 如果银行为出款银行
            elif bankcard.account_type == 1:
                writer.writerow([bankcard, 'id', '入款' '转出', '手续费', '备注', '记录时间', '创建时间'])
                totalamount = 0
                fees = 0
                for record in records:
                    if record.type == 0:
                        writer.writerow(['', record.id, record.amount, '', record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                    else:
                        writer.writerow(['', record.id, '', record.amount, record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                for record in records.filter(type=1):
                    totalamount += (record.amount + record.fees)
                    fees += record.fees
                alltotalamount += totalamount
                allfees += fees
                realamount += (totalamount - fees)

            # 如果银行为入款中转银行
            elif bankcard.account_type == 2:
                writer.writerow([bankcard, 'id', '入款', '转出', '手续费', '备注', '记录时间', '创建时间'])
                totalamount = 0
                fees = 0
                for record in records:
                    if record.type == 0:
                        writer.writerow(['', record.id, record.amount, '', record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                    else:
                        writer.writerow(['', record.id, '', record.amount, record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                for record in records.filter(type=0):
                    totalamount += record.amount
                    fees += record.fees
                alltotalamount += totalamount
                allfees += fees
                realamount += (totalamount - fees)

            # 如果银行为出款中转银行
            else:
                writer.writerow([bankcard, 'id', '入款', '转出', '手续费', '备注', '记录时间', '创建时间'])
                totalamount = 0
                fees = 0
                for record in records:
                    if record.type == 0:
                        writer.writerow(['', record.id, record.amount, '', record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                    else:
                        writer.writerow(['', record.id, '', record.amount, record.fees, record.remark, record.create_time.strftime('%Y-%m-%d'), record.real_time.strftime('%Y-%m-%d %H:%M:%S %f')])
                for record in records.filter(type=1):
                    totalamount += (record.amount + record.fees)
                    fees += record.fees
                alltotalamount += totalamount
                allfees += fees
                realamount += (totalamount - fees)
        writer.writerow(['', '', '', '', '', '', ''])
        if (bankcards.latest('id').account_type == 0) or (bankcards.latest('id').account_type == 2):
            writer.writerow(['汇总表', '原余额', '实入款', '总入款', '现余额', '手续费'])
        else:
            writer.writerow(['汇总表', '原余额', '实出款', '总出款', '现余额', '手续费'])
        writer.writerow(['', past_balance, realamount, alltotalamount, now_balance, allfees])
        return response


# 锁定的功能
class ChangeSortView(View):
    def post(self, request):
        id = request.POST.get('id')
        sort = request.POST.get('sort')
        try:
            record = Record.objects.get(id=id)
        except Exception as e:
            data = {'status': 1, 'msg': '为查询到数据'}
            return JsonResponse(data)
        else:
            record.sort = sort
            record.save()
        data = {'status': 0, 'msg': '修改成功'}
        return JsonResponse(data)





# xiaotang
"""
class CsrfView(View):
    #获取csrf

    def get(self, request):
        token = get_token(request)
        return JsonResponse({'stat': 0, 'mytoken': token})
"""

# 权限管理
class PmsView(View):
    """显示权限管理页面"""

    def get(self, request):
        objs = AdminPermission.objects.all().order_by('id')
        (paginator, page_objs) = page_handle(request, objs)
        list_query = []
        for obj in page_objs:
            data_obj = {
                "id": obj.id,
                "name": obj.name,
                "des": obj.des
            }
            list_query.append(data_obj)
        data = {"count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)


# 添加权限
class AddPmsView(View):

    def post(self, request):
        pmsname = request.POST.get('pmsname')
        des = request.POST.get('des')
        if pmsname == '':
            return JsonResponse({"stat": 1, "msg": "权限名不能为空"})
        try:
            pmsobj = AdminPermission.objects.get(name=pmsname)
        except Exception as e:
            AdminPermission.objects.create(name=pmsname, des=des)
            loginfo(request, request.user.username, "添加权限：%s" %pmsname)
            return JsonResponse({"stat": 0, "msg": "成功权限：%s" %pmsname})
        else:
            return JsonResponse({"stat": 1, "msg": "该权限已存在"})


# 显示角色页
class RoleView(View):

    def get(self, request):
        objs = AdminGroup.objects.all().order_by('id')
        (paginator, page_objs) = page_handle(request, objs)
        list_query = []
        for obj in page_objs:
            data_obj = {
                "id": obj.id,
                "name": obj.name,
                "pms": [p.name for p in obj.permission.all()]
            }
            list_query.append(data_obj)

        pms_objs = AdminPermission.objects.all()
        pms_list = []
        for i in pms_objs:
            data = {
                "id": i.id,
                "name": i.name,
            }
            pms_list.append(data)

        data = {"count": paginator.count, "data": list_query, "num_pages": paginator.num_pages, "pms":pms_list}
        return JsonResponse(data, safe=False)


# 添加角色
class AddRoleView(View):

    def post(self, request):
        rolename = request.POST.get('pmsname')
        pmss = json.loads(request.POST.get('pms'))
        try:
            AdminGroup.objects.get(name=rolename)
        except Exception as e:
            role_list = []
            for i in pmss:
                pmsobj = AdminPermission.objects.get(id=i)
                role_list.append(pmsobj)
            role_obj = AdminGroup.objects.create(name=rolename)
            role_obj.permission.set(role_list)
            loginfo(request, request.user.username, "添加角色：%s" %rolename)
            return JsonResponse({"stat": 0, "msg": "添加角色成功"})
        else:
            return JsonResponse({"stat": 1, "msg": "该角色已存在"})


# 显示管理员页
class ManageView(View):

    def get(self, request):

        objs = MyUser.objects.all().order_by('id')
        (paginator, page_objs) = page_handle(request, objs)
        list_query = []
        for usr in page_objs:
            data = {
                "id": usr.id,
                "name": usr.username,
                "nickname": usr.nickname
            }
            roles = AdminGroup.objects.filter(group_user=usr)  # 用该用户的组
            role = []
            pmslist = []
            if roles.exists():
                for i in roles:
                    role.append(i.name)
                    for i in (i.permission.all()):
                        if i.name not in pmslist:
                            pmslist.append(i.name)
            data["roles"] = role
            data["pms"] = pmslist
            list_query.append(data)

        rolelist = []
        role_obj = AdminGroup.objects.all()
        for role in role_obj:
            data = {
                "id": role.id,
                "name": role.name,
            }
            rolelist.append(data)
        data = {"count": paginator.count, "data": list_query, "num_pages": paginator.num_pages, "roles": rolelist}

        return JsonResponse(data, safe=False)


# 添加管理员
class AddManageView(View):

    def post(self, request):
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        mypwd = request.POST.get('mypwd')
        role = json.loads(request.POST.get('role'))
        if username == '' or mypwd == '':
            return JsonResponse({'stat': 1, 'msg': "用户名或密码不能为空"})
        if role == "":
            return JsonResponse({'stat': 1, 'msg': "角色不能为空"})
        try:
            MyUser.objects.get(username=username)
        except Exception as e:
            user_obj = MyUser.objects.create_user(username=username, nickname=nickname, password=mypwd, is_staff=True)
            for i in role:
                role_obj = AdminGroup.objects.get(id=i)
                role_obj.group_user.add(user_obj)
            loginfo(request, request.user.username, "添加管理员：%s" % username)
            return JsonResponse({"stat": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"stat": 1, "msg": "该用户已经存在"})


# 删除权限
class DelPmsView(View):

    def get(self, request):
        pmsid = request.GET.get('pk')
        try:
            pms_obj = AdminPermission.objects.get(id=pmsid)
        except Exception as e:
            return JsonResponse({"stat":1, "msg": "权限不存在"})
        pms_obj.delete()
        loginfo(request, request.user.username, "删除权限：%s" % pms_obj.name)
        return JsonResponse({"stat":0, "msg": "删除成功"})


# 删除角色
class DelRoleView(View):

    def get(self, request):
        roleid = request.GET.get('pk')
        try:
            role_obj = AdminGroup.objects.get(id=roleid)
        except Exception as e:
            return JsonResponse({"stat":1, "msg": "角色不存在"})
        role_obj.delete()
        loginfo(request, request.user.username, "删除角色：%s" % role_obj.name)
        return JsonResponse({"stat":0, "msg": "删除角色成功"})


# 删除管理员
class DelUserView(View):

    def get(self, request):
        userid = request.GET.get('pk')
        try:
            user_obj = MyUser.objects.get(id=userid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "用户不存在"})
        if user_obj.is_superuser:
            return JsonResponse({"stat": 1, "msg": "不能删除超级管理员"})
        user_obj.delete()
        loginfo(request, request.user.username, "删除管理员：%s" % user_obj.username)
        return JsonResponse({"stat": 0, "msg": "删除用户成功"})


# 修改管理员
class MdfUserView(View):

    def post(self, request):
        userid = request.POST.get("userid")
        username = request.POST.get("username")
        selete_data = json.loads(request.POST.get("selete_data"))
        password = request.POST.get("password")
        nikname = request.POST.get("nikname")

        if username == '':
            return JsonResponse({"stat": 1, "msg": "用户名不能为空"})
        try:
            user_obj = MyUser.objects.get(id=userid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "用户不存在"})
        mdfag_username = user_obj.username  # 修改前的名字
        if selete_data == []:
            return JsonResponse({"stat": 1, "msg": "未选择权限"})
        usergroups = AdminGroup.objects.filter(group_user=user_obj)
        for i in usergroups:
            i.group_user.remove(user_obj)
        user_obj.username = username
        user_obj.nickname = nikname
        if password != '':
            user_obj.set_password(password)
        user_obj.save()
        for i in selete_data:
            AdminGroup.objects.get(id=i).group_user.add(user_obj)
        loginfo(request, request.user.username, "把%s修改为：%s" %(mdfag_username, username))
        return JsonResponse({"stat": 0, "msg": "修改成功"})


# 显示日志
class LogView(View):

    def get(self, request):
        objs = LogInfo.objects.all().filter(is_delete=False).order_by('-create_time')
        (paginator,page_objs) = page_handle(request, objs)
        list_query = []
        for i in page_objs:
            data = {
                "id": i.id,
                "time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "username": i.name,
                "content": i.action_data,
                "ip": i.ip
            }
            list_query.append(data)
        data = {"count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)


# 批量删除日志
class DelLogView(View):

    # 删除单个日志
    def get(self, request):
        pk = request.GET.get('pk')
        try:
            obj = LogInfo.objects.get(id=pk)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "未找到该日志"})
        obj.is_delete=True
        obj.save()
        return JsonResponse({"stat": 0, "msg": "成功"})

    # 批量删除日志
    def post(self, request):
        id_list = json.loads(request.POST.get("log_list"))
        LogInfo.objects.filter(id__in=id_list).update(is_delete=True)
        return JsonResponse({"stat": 0, "msg": "删除成功"})


# 搜索日志
class SearchLogView(View):

    def get(self, request):
        sc_date = request.GET.get("sctime")
        username = request.GET.get("username")
        logs = LogInfo.objects.all().filter(is_delete=False).order_by('-create_time')
        if username:
            try:
                userobj = MyUser.objects.get(username=username)
            except Exception as e:
                return JsonResponse({"stat": 1, "msg": "该操作人不存在"})
            logs = logs.filter(name=userobj.username)
            if not logs.exists():
                return JsonResponse({"stat": 1, "msg": "没有查到该用户的日志"})

        if sc_date:
            try:
                start_time = sc_date.split()[0]
                end_time = sc_date.split()[2]
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
                start_time += datetime.timedelta(hours=8)
                end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
                end_time += datetime.timedelta(hours=23+8, minutes=59, seconds=59)
            except Exception as e:
                return JsonResponse({"stat": 1, "msg": "时间格式错误"})
            logs = logs.filter(create_time__gte=start_time, create_time__lte=end_time)
            if not logs.exists():
                return JsonResponse({"stat": 1, "msg": "在该时间段没有查到相关信息"})
        (paginator, page_objs) = page_handle(request, logs)
        list_query = []
        for i in page_objs:
            data = {
                "id": i.id,
                "time": i.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "username": i.name,
                "content": i.action_data,
                "ip": i.ip
            }
            list_query.append(data)
        data = {"stat": 0, "count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)


# 删除全部日志
class DelAllLogView(View):

    def get(self, request):
        LogInfo.objects.filter(is_delete=False).update(is_delete=True)
        loginfo(request, request.user.username, '删除全部日志')
        return JsonResponse({"stat": 0, "msg": "清除成功"})


# 添加银行
class AddBankView(View):

    def post(self, request):
        bkname = request.POST.get("bkname")
        try:
            bkobj = Banks.objects.get(name=bkname)
        except Exception as e:
            Banks.objects.create(name=bkname)
            loginfo(request, request.user.username, "添加银行：%s" % bkname)
            return JsonResponse({"stat": 0, "msg": "添加成功"})
        return JsonResponse({"stat": 1, "msg": "该银行已存在"})


# 显示银行管理页面
class ShowBankView(View):

    def get(self, request):
        banks = Banks.objects.all().order_by('id')
        paginator, page_objs = page_handle(request, banks)
        list_query = []
        for i in page_objs:
            data = {
                "id": i.id,
                "name": i.name,
            }
            list_query.append(data)
        data = {"stat": 0, "count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)


# 删除银行
class DelBankView(View):

    def get(self, request):
        bkid = request.GET.get("bankid")
        try:
            bkobj = Banks.objects.get(id=bkid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该银行不存在"})
        bkobj.delete()
        loginfo(request, request.user.username, "删除银行：%s" % bkobj.name)
        return JsonResponse({"stat": 0, "msg": "删除成功"})


# 显示添加账户银行下拉（应该和显示账户合并）
class ShowBkView(View):

    def get(self, request):
        banks = Banks.objects.all()
        bklist = []
        for i in banks:
            data = {
                "id": i.id,
                "name": i.name
            }
            bklist.append(data)
        type_list = []
        for i in BankCard.choose_types:
            data = {
                "ind": i[0],
                "name": i[1],
            }
            type_list.append(data)
        return JsonResponse({"bklist": bklist, "type_list": type_list})


# 添加账户
class AddAccountView(View):

    def post(self, request):

        userobj = request.user
        bankname = request.POST.get('bankname')  # 银行
        balance = request.POST.get('balance')    # 初始额
        accounttype = request.POST.get('accounttype')  # 账户类型
        accountname = request.POST.get('accountname')  # 账户名字
        if bankname == '':
            return JsonResponse({"stat": 1, "msg": "银行不能为空"})
        elif balance == '':
            return JsonResponse({"stat": 1, "msg": "余额不能为空"})
        elif accounttype == '':
            return JsonResponse({"stat": 1, "msg": "账户类型不能为空"})
        elif accountname == '':
            return JsonResponse({"stat": 1, "msg": "账户名不能为空"})
        try:
            balance = decimal.Decimal(balance)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "输入的余额不正确"})
        try:
            bankobj = Banks.objects.get(name=bankname)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该银行不存在"})
        try:
            BankCard.objects.get(name=accountname)
        except Exception as e:
            typenum = 0
            for i in BankCard.choose_types:
                if accounttype == i[1]:
                    typenum = i[0]
                    break
            BankCard.objects.create(
                name=accountname,
                bank_type=bankobj,
                account_type=typenum,
                initial_amount=balance,
                editor=userobj
            )
            loginfo(request, request.user.username, "添加账户：%s" % accountname)
            return JsonResponse({"stat": 0, "msg": "添加账户成功"})
        return JsonResponse({"stat": 1, "msg": "该账户已存在"})


# 修改银行名字
class MdfBankNameView(View):

    def post(self, request):

        bankid = request.POST.get("bankid")
        bankname = request.POST.get("bankname")
        try:
            obj = Banks.objects.get(id=bankid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该银行不存在"})
        mdfagname = obj.name
        obj.name = bankname
        obj.save()
        loginfo(request, request.user.username, "银行%s修改为：%s" % (mdfagname, bankname))
        return JsonResponse({"stat": 0, "msg": "修改成功"})


# 显示管理页面
class ShowAccView(View):

    def get(self, request):
        accobj = BankCard.objects.all().order_by('id')
        paginator, page_objs = page_handle(request, accobj)
        list_query = []
        for i in page_objs:
            data = {
                "id": i.id,
                "name": i.name,
                "bank": i.bank_type.name,
                "editor": i.editor.username,
                "initial_amount": i.initial_amount,
                "type": BankCard.choose_types[i.account_type][1],
                "is_disable": "是" if i.is_disable else "否"
            }
            list_query.append(data)
        data = {"stat": 0, "count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)


# 删除账户
class DelAccView(View):

    def get(self, request):
        accid = request.GET.get('accid')
        try:
            bcobj = BankCard.objects.get(id=accid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "未找到该账户"})
        loginfo(request, request.user.username, "删除账户：%s" % (bcobj.name))
        bcobj.delete()
        return JsonResponse({"stat": 0, "msg": "删除成功"})


# 修改账户
class MdfAccView(View):

    def post(self, request):

        accname = request.POST.get("accname")
        accid = request.POST.get("accid")
        acctype = request.POST.get("acctype")
        accbank = request.POST.get("accbank")
        is_disable = request.POST.get("is_disable")
        balance = request.POST.get("balance")
        if not request.user.is_superuser:
            return JsonResponse({"stat": 1, "msg": "没有权限修改"})
        elif balance == '':
            return JsonResponse({"stat": 1, "msg": "余额不能为空"})
        try:
            balance = decimal.Decimal(balance)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "输入的余额不正确"})
        try:
            accobj = BankCard.objects.get(id=accid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "未找到该账户"})
        try:
            bkobj = Banks.objects.get(name=accbank)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该银行不存在"})
        typeid = ''
        for i in BankCard.choose_types:
            if i[1] == acctype:
                typeid = i[0]
                break
        mdfagname = accobj.name
        accobj.name = accname
        accobj.bank_type = bkobj
        accobj.account_type = typeid
        if is_disable == '是':
            is_disable = True
        elif is_disable == '否':
            is_disable = False
        accobj.is_disable = is_disable
        accobj.initial_amount = balance
        accobj.save()
        loginfo(request, request.user.username, "修改账户%s为：%s" % (mdfagname, accname))
        return JsonResponse({"stat": 0, "msg": "修改账户成功"})


# 修改权限
class MdfPmsView(View):

    def post(self, request):
        pmsid = request.POST.get("pmsid")
        pmsname = request.POST.get("pmsname")
        decname = request.POST.get("decname")
        if pmsname == '':
            return JsonResponse({"stat": 1, "msg": "权限名不能为空"})
        try:
            pmsobj = AdminPermission.objects.get(id=pmsid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该权限不存在"})
        if pmsobj.name == pmsname:
            pmsobj.des = decname
            pmsobj.save()
            return JsonResponse({"stat": 0, "msg": "修改成功"})
        try:
            pmsobj = AdminPermission.objects.get(name=pmsname)
        except Exception as e:
            pmsobj.name = pmsname
            pmsobj.decname = decname
            pmsobj.save()
            loginfo(request, request.user.username, "修改权限：%s" % (pmsobj))
            return JsonResponse({"stat": 0, "msg": "修改成功"})
        return JsonResponse({"stat": 1, "msg": "该权限已存在"})


# 修改角色
class MdfRoleView(View):

    def post(self, request):
        roleid = request.POST.get("roleid")
        rolename = request.POST.get("rolename")
        pmslist = json.loads(request.POST.get("pmslist"))

        if rolename == '':
            return JsonResponse({"stat": 1, "msg": "角色名不能为空"})

        try:
            roleobj = AdminGroup.objects.get(id=roleid)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该角色不存在"})

        role_list = []
        for i in pmslist:
            pmsobj = AdminPermission.objects.get(id=i)
            role_list.append(pmsobj)

        if roleobj.name == rolename:  # 如果是只改权限
            roleobj.permission.clear()  # 清空权限
            roleobj.permission.set(role_list)
            return JsonResponse({"stat": 0, "msg": "修改角色成功"})

        try:
            other_role = AdminGroup.objects.get(name=rolename)
        except Exception as e:
            roleobj.name = rolename
            roleobj.permission.clear()  # 清空权限
            roleobj.permission.set(role_list)
            roleobj.save()
            loginfo(request, request.user.username, "修改角色：%s" % (rolename))
            return JsonResponse({"stat": 0, "msg": "修改角色成功"})

        return JsonResponse({"stat": 1, "msg": "该角色已存在"})


# 转入类型
class TransferTypeView(View):

    def get(self, request):
        typeobj = TransferType.objects.all().order_by('id')
        paginator, page_objs = page_handle(request, typeobj)
        list_query = []
        for i in page_objs:
            data = {
                "id": i.id,
                "name": i.name,
                "type": "转出" if i.transfer_type else "转入",
            }
            list_query.append(data)
        data = {"stat": 0, "count": paginator.count, "data": list_query, "num_pages": paginator.num_pages}
        return JsonResponse(data, safe=False)

    def post(self, request):
        typename = request.POST.get('name')
        transfertype = request.POST.get('transfertype')
        if transfertype == '转入':
            transfertype = 0
        else:
            transfertype = 1
        if typename == '':
            return JsonResponse({"stat": 1, "msg": "类型名不能为空"})
        try:
            typeobj = TransferType.objects.get(name=typename)
        except Exception as e:
            TransferType.objects.create(name=typename, transfer_type=transfertype)
            loginfo(request, request.user.username, "添加转入类型：%s" % typename)
            return JsonResponse({"stat": 0, "msg": "添加成功"})
        return JsonResponse({"stat": 1, "msg": "转入类型已存在"})


# 转入类型
class TransferInTypeView(View):
    def get(self, request):
        typeobj = TransferType.objects.filter(transfer_type=0)
        list_query = []
        for i in typeobj:
            data = {
                "id": i.id,
                "name": i.name,
            }
            list_query.append(data)
        data = {"stat": 0, "data": list_query}
        return JsonResponse(data, safe=False)


# 转出类型
class TransferOutTypeView(View):
    def get(self, request):
        typeobj = TransferType.objects.filter(transfer_type=1)
        list_query = []
        for i in typeobj:
            data = {
                "id": i.id,
                "name": i.name,
            }
            list_query.append(data)
        data = {"stat": 0, "data": list_query}
        return JsonResponse(data, safe=False)


# 转入类型
class TransferAllTypeView(View):
    def get(self, request):
        typeobj = TransferType.objects.all()
        list_query = []
        for i in typeobj:
            data = {
                "id": i.id,
                "name": i.name,
            }
            list_query.append(data)
        data = {"stat": 0, "data": list_query}
        return JsonResponse(data, safe=False)


# 删除转入类型
class DelTypeView(View):

    def get(self, request):
        delpk = request.GET.get('delpk')
        try:
            typeobj = TransferType.objects.get(id=delpk)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该类型不存在"})
        typename = typeobj.name
        typeobj.delete()
        loginfo(request, request.user.username, "删除转入类型%s" %typename)

        return JsonResponse({"stat": 0, "msg": "删除成功"})


# 编辑类型
class MdfTypeView(View):

    def post(self, request):
        editpk = request.POST.get("editpk")
        name = request.POST.get("name")
        transfer_type = request.POST.get('transfer_type')
        if transfer_type == '转入':
            transfer_type = 0
        else:
            transfer_type = 1
        try:
            typeobj = TransferType.objects.get(id=editpk)
        except Exception as e:
            return JsonResponse({"stat": 1, "msg": "该类型不存在"})
        if typeobj.name != name:
            try:
                type_obj = TransferType.objects.get(name=name)
            except Exception as e:
                typeobj.name = name
                typeobj.transfer_type = transfer_type
                typeobj.save()
                return JsonResponse({"stat": 0, "msg": "修改成功"})
        else:
            typeobj.transfer_type = transfer_type
            typeobj.save()
            return JsonResponse({"stat": 0, "msg": "修改成功"})
        return JsonResponse({"stat": 1, "msg": "该类型已存在"})


# 页码校验函数
def page_handle(request, qurey_set):
    page = request.GET.get("p")
    size = request.GET.get("size")
    if page == '':
        page = 1
    try:
        page = int(page)
    except Exception as e:
        page = 1
    if size == '':
        size = 1
    try:
        size = int(size)
    except Exception as e:
        size = 5
    paginator = Paginator(qurey_set, size)
    page_objs = paginator.page(page)
    return (paginator,page_objs)


# 插入日志函数
def loginfo(request, username, logmsg):
    if 'HTTP_X_FORWARDED_FOR' in request.META.values():
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    LogInfo.objects.create(
        name=username,
        action_data=logmsg,
        ip=ip
    )