# -*- coding: utf-8 -*-
# 18-12-27 20:35
# AUTHOR:xiaoli

from django.conf.urls import url
from account.views import *

app_name = 'account'
urlpatterns = [
    url(r"addmanage$", AddManageView.as_view(), name='addmanage'),  # 添加管理员
    url(r'^verifycode$', VerifyCodeView.as_view(), name='verifycode'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^setusername$', SetUserNameView.as_view(), name='setusername'),
    url(r'^banksinfo$', BanksInfoView.as_view(), name='banksinfo'),
    url(r'^bankcard$', BankCardView.as_view(), name='bankcard'),
    url(r'^bankrecord$', BankRecordView.as_view(), name='bankrecord'),
    url(r'^searchbankrecord$', SearchBankRecordView.as_view(), name='searchbankrecord'),
    url(r'^searchbankrecorddaochu$', SearchBankRecordDaochuView.as_view(), name='searchbankrecorddaochu'),
    url(r'^indexinfo$', IndexInfoView.as_view(), name='indexinfo'),
    url(r'^dateadd$', DateAddView.as_view(), name='dateadd'),
    url(r'^datesub$', DateSubView.as_view(), name='datesub'),
    url(r'^addbankrecord$', AddBankRecordView.as_view(), name='addbankrecord'),
    url(r'^transferin$', TransferInView.as_view(), name='transferin'),
    url(r'^transferoutmoney$', TransferOutMoneyView.as_view(), name='transferoutmoney'),
    url(r'^getbalance$', GetBalanceView.as_view(), name='getbalance'),
    url(r'^waibankcard$', WaiBankcardView.as_view(), name='waibankcard'),
    url(r'^transferout$', TransferOutView.as_view(), name='transforout'),
    url(r'^deleterecord$', DeleteRecordView.as_view(), name='deleterecord'),
    url(r'^get_checkbankcard$', GetCheckBankcardView.as_view(), name='get_checkbankcard'),
    url(r'^getbankcardlist$', GetBankcardListView.as_view(), name='getbankcardlist'),
    url(r'^getbankcardlistout$', GetBankcardListOutView.as_view(), name='getbankcardlistout'),
    url(r'^getuserpermissionbankcard$', GetUserPermissionBankcardView.as_view(), name='getuserpermissionbankcard'),
    url(r'^checknowbankcard$', CheckNowBankcardView.as_view(), name='checknowbankcard'),
    url(r'^checknowbankcardout$', CheckNowBankcardOutView.as_view(), name='checknowbankcardout'),
    url(r'^checkallbankcard$', CheckAllBankcardView.as_view(), name='checkallbankcard'),
    url(r'^checkallbankcardout$', CheckAllBankcardOutView.as_view(), name='checkallbankcardout'),
    url(r'^checkaccount$', CheckAccountView.as_view(), name='checkaccount'),
    url(r'^checkout$', CheckOutView.as_view(), name='checkout'),
    url(r'^removeamount$', RemoveAmountView.as_view(), name='removeamount'),
    url(r'^reconcilia$', ReconciliaView.as_view(), name='reconcilia'),
    url(r'^getyesterdaybalance$', GetYesterdayBalanceView.as_view(), name='getyesterdaybalance'),
    url(r'^changeyesterdaybalance$', ChangeYesterDayBalanceView.as_view(), name='changeyesterdaybalance'),
    url(r'^downloadcheck$', DownloadCheckView.as_view(), name='downloadcheck'),
    url(r'^changesort$', ChangeSortView.as_view(), name='changesort'),
    #url('^getcsrf$', CsrfView.as_view(), name='csrf'),
    #url('^menu$', MenuView.as_view(), name='cd'),  # 显示菜单
    url('^getpms$', PmsView.as_view(), name='getpms'),  # 显示权限管理页面
    url(r'^getrole$', RoleView.as_view(), name='role'),  # 显示角色管理页面
    url('^addpms$', AddPmsView.as_view(), name='addpms'),  # 添加权限
    url('^addrole$', AddRoleView.as_view(), name='addrole'),  # 添加角色
    url('^manage$', ManageView.as_view(), name='manage'),  # 显示用户管理页面
    url("^delpms$", DelPmsView.as_view(), name='delpms'),  # 删除权限
    url("^delrole$", DelRoleView.as_view(), name='delrole'),  # 删除角色
    url("^deluser$", DelUserView.as_view(), name='deluser'),  # 删除用户
    url("^mdfuser$", MdfUserView.as_view(), name='mdfuser'),  # 更新用户
    url("^log$", LogView.as_view(), name='log'),  # 显示日志
    url("^dellog$", DelLogView.as_view(), name='dellog'),  # 删除日志
    url("^sclog$", SearchLogView.as_view(), name='searchlog'),  # 搜索日志
    url("^delalllog$", DelAllLogView.as_view(), name='delalllog'),  # 清空日志
    url("^addbank$", AddBankView.as_view(), name='addbank'),  # 添加银行
    url("^showbank$", ShowBankView.as_view(), name="showbank"),  # 显示银行
    url("^delbank$", DelBankView.as_view(), name="delbank"),  # 删除银行
    url("^showbk$", ShowBkView.as_view(), name="showbk"),  # 显示添加账户页面的银行
    url("^addaccount$", AddAccountView.as_view(), name="addaccount"), # 添加账户
    url("^mdfbankname$", MdfBankNameView.as_view(), name="mdfbankname"),  # 修改银行名
    url("^showacc$", ShowAccView.as_view(), name="showacc"),  # 显示账户页面
    url("^delacc$", DelAccView.as_view(), name="delacc"),  # 删除账户
    url("^mdfacc$", MdfAccView.as_view(), name="mdfacc"),  # 修改账户
    url("^mdfpms$", MdfPmsView.as_view(), name="mdfpms"),  # 修改权限
    url("^mdfrole$", MdfRoleView.as_view(), name="mdfrole"),  # 修改角色
    url("^transfertype$", TransferTypeView.as_view(), name='addtype'),  # 添加类型
    url(r'^transferintype$', TransferInTypeView.as_view(), name='transferintype'),  # 获取转入类型
    url(r'^transferouttype$', TransferOutTypeView.as_view(), name='transferouttype'),  # 获取转出类型
    url(r'^transferalltype$', TransferAllTypeView.as_view(), name='transferalltype'),  # 获取所有类型
    url("^deltype$", DelTypeView.as_view(), name='deltype'),  # 删除类型
    url("^mdftype$", MdfTypeView.as_view(), name='mdftype'),  # 修改转入类型
]
