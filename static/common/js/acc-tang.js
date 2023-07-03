/**
 * Created by Owner on 2019/1/14.
 */
    //渲染
var pagesize = 10;
var page = 1;
function showacc(page) {
    $.ajax({
        url: '/showacc?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        success: function (data) {
            if (data.count != 0) {
                var html_str = '<tr><th>ID</th><th>账户名</th><th>所属银行</th><th>类型</th><th>初始余额</th><th>添加人</th><th>是否停用</th><th>操作</th></tr>';
                $.each(data.data, function (i, award) {
                    html_str += '<tr><td>' + award.id + '</td><td>' + award.name + '</td><td>' + award.bank + '</td><td>' + award.type + '</td><td>' + award.initial_amount + '</td><td>' + award.editor + '</td><td>' + award.is_disable + '</td><td><a class="btn_edit" bankpk="' + award.id + '">编辑</a><a class="btn_delete" pk="' + award.id + '">删除</a></td></tr>'
                });
                var sPage = Paging(page, pagesize, data.count, 2, "showacc", 'cur', '', '上一页', '下一页');
                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showacc" + ")' />";
                sPage += "<span>总共" + data.num_pages + "页<span>";
                $("#page").html(sPage);
                $("#bank-list").html(html_str);
            }
        }
    })
}
showacc(1);

//下拉选项数据获取
$.ajax({
    url: "/showbk",
    type: "get",
    dataType: "json",
    cache: false,
    success: function (data) {
        var bankstr = '';
        var typestr = '';
        $.each(data.bklist, function (i, award) {
            bankstr += '<option>' + award.name + '</option>'
        });
        $.each(data.type_list, function (i, award) {
            typestr += '<option pk=' + award.ind + '>' + award.name + '</option>';
        });
        $("#banktype").html(typestr);
        $("#bank").html(bankstr);
        $("#box-type").html(typestr);
        $("#box-bank").html(bankstr);
    }
});

function Trim(str)
{ var result;
    result = str.replace(/\s/g,"");
    return result;
}

//添加账户
$(document).on("click", ".btn-submit", function () {
    var banktype = $("#banktype").val();
    var bank = $("#bank").val();
    var balance = $("#balance").val();
    var accountname = $("#bankname").val();
    if (bank == '') {
        layer.msg("请选择银行，如没有银行请先添加银行", {time: 800, icon: 0});
        return false
    }
    else if (accountname == '') {
        layer.msg("账户名不能为空", {time: 800, icon: 0});
        return false
    } else if (balance == '') {
        layer.msg("余额不能为空", {time: 800, icon: 0});
        return false
    }
    accountname = Trim(accountname);
    $.ajax({
        url: "/addaccount",
        type: "post",
        dataType: "json",
        cache: false,
        data: {
            accountname: accountname,
            accounttype: banktype,
            balance: balance,
            bankname: bank
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1}, function () {
                    window.location.href = '/static/addAccount.html'
                })
            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 1000, icon: 5})
            }
        }
    })
});

//删除账户
$(document).on("click", ".btn_delete", function () {
    thisobj = $(this).closest('tr')
    var accid = $(this).attr('pk')
    layer.confirm('确定删除账户?', {
        btn: ['确定', '取消'] //按钮
    }, function () {
        $.ajax({
            url: "/delacc",
            cache: false,
            type: "get",
            dataType: "json",
            data: {
                accid: accid
            },
            success: function (data) {
                if (data.stat == 0) {
                    layer.msg(data.msg, {time: 800, icon: 1}, function () {
                        thisobj.remove()
                    })
                } else if (data.stat == 1) {
                    layer.msg(data.msg, {time: 800, icon: 2})
                }
            }
        })
    })
})

// 编辑弹框
$(document).on("click", ".btn_edit", function () {
    var accid = $(this).parents("tr").find("td").eq(0).text();
    var accname = $(this).parents("tr").find("td").eq(1).text();
    var accbank = $(this).parents("tr").find("td").eq(2).text();
    var acctype = $(this).parents("tr").find("td").eq(3).text();
    var is_use = $(this).parents("tr").find("td").eq(6).text();
    var balance = $(this).parents("tr").find("td").eq(4).text();
    $("#username").val(accname);
    for (var i = 0; i < $("#box-type option").length; i++) {
        if (acctype == $("#box-type option").eq(i).val()) {
            $("#box-type option").eq(i).attr("selected", "selected").siblings().removeAttr('selected');
        }
    }
    for (var i = 0; i < $("#box-bank option").length; i++) {
        if (accbank == $("#box-bank option").eq(i).val()) {
            $("#box-bank option").eq(i).attr("selected", "selected").siblings().removeAttr('selected');
        }
    }
    $("#username").attr("pk", accid);
    $("#box-is-use").val(is_use);
    $('#bal').val(balance);
    layer.open({
        type: 1,
        title: '编辑',
        skin: 'layui-layer-demo', //样式类名
        closeBtn: 1, //显示关闭按钮
        anim: 2,
        area: ['540px', '450px'],
        shadeClose: true, //开启遮罩关闭
        content: $('#tanout')
    });
    var H = $('.layui-layer').height() - 42;
    $('.layui-layer-content').height(H - 42);
});


//编辑
$(document).on("click", "#mdfbank", function () {
    var accid = $("#username").attr("pk");
    var accname = $("#username").val();
    var acctype = $("#box-type").val();
    var accbank = $("#box-bank").val();
    var is_disable = $("#box-is-use").val();
    var balance = $("#bal").val();
    accname = Trim(accname);
    $.ajax({
        url: "/mdfacc",
        dataType: "json",
        type: "post",
        cache: false,
        data: {
            accname: accname,
            accid: accid,
            acctype: acctype,
            accbank: accbank,
            is_disable:is_disable,
            balance: balance
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1}, function () {
                    window.location.href = "/static/addAccount.html"
                })

            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon: 3})
            }

        }
    })
});

