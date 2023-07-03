/**
 * Created by Owner on 2019/1/14.
 */
//渲染
var pagesize = 10;
var page = 1;
function showbank(page) {
    $.ajax({
        url: '/showbank?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        success: function (data) {
            if (data.count != 0) {
                var html_str = '<tr><th>ID</th><th>银行名</th><th>操作</th></tr>';
                $.each(data.data, function (i, award) {
                    html_str += '<tr><td>' + award.id + '</td><td>' + award.name + '</td><td><a class="btn_edit" bankpk="' + award.id + '">编辑</a><a class="btn_delete" pk="' + award.id + '">删除</a></td></tr>'
                });

                var sPage = Paging(page, pagesize, data.count, 2, "showbank", 'cur', '', '上一页', '下一页');

                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showbank" + ")' />";

                sPage += "<span>总共" + data.num_pages + "页<span>";
                //   sPage +="<input type='text' name='lname' id='text_data' class='jump_select_val' placeholder='页数'/>";
                $("#page").html(sPage);
                $("#bank-list").html(html_str);
            }
        }
    })
}
showbank(1);


function Trim(str)
{ var result;
    result = str.replace(/\s/g,"");
    return result;
}

//添加银行
$(document).on("click", ".add_bank_btn", function () {
    var bkname = $(".bank_input_wrap").val();
    if (bkname == '') {
        layer.msg("请输入银行名字", {time: 800, icon: 0});
        return false
    }
    bkname = Trim(bkname);
    $.ajax({
        url: "/addbank",
        type: "post",
        dataType: "json",
        data: {
            bkname: bkname
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1},function () {
                    window.location.href = '/static/addBank.html'
                })

            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon: 3})
            }
        }
    })

});

// 编辑弹框
$(document).on("click", ".btn_edit", function () {
    var bankname = $(this).parents("tr").find("td").eq(1).text();
    var bankid = $(this).parents("tr").find("td").eq(0).text();
    $("#uu1").val(bankname);
    $('#uu1').attr("pk", bankid);
    layer.open({
        type: 1,
        title: '编辑',
        skin: 'layui-layer-demo', //样式类名
        closeBtn: 1, //显示关闭按钮
        anim: 2,
        area: ['540px', '200px'],
        shadeClose: true, //开启遮罩关闭
        content: $('#tanout')
    });
    var H = $('.layui-layer').height() - 42;
    $('.layui-layer-content').height(H - 42);
});

//编辑
$(document).on("click", "#mdfbank", function () {
    var bankid = $("#uu1").attr("pk");
    var bankname = $("#uu1").val();
    bankname = Trim(bankname);
    $.ajax({
        url: "/mdfbankname",
        dataType: "json",
        type: "post",
        cache: false,
        data: {
            bankname: bankname,
            bankid: bankid
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1},function () {
                    window.location.href = "/static/addBank.html"
                })
            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon: 3})
            }
        }
    })
});

//删除银行
$(document).on("click", ".btn_delete", function () {
    var thisobj = $(this).closest('tr')
    var bankid =  $(this).attr('pk')
    layer.confirm('确定要删除吗？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
        $.ajax({
            url: "/delbank",
            cache: false,
            type: "get",
            dataType: "json",
            data: {
                bankid:bankid
            },
            success: function (data) {
                if (data.stat == 0) {
                    layer.msg(data.msg, {time: 800, icon: 1},function () {
                        thisobj.remove()
                    })
                } else if (data.stat == 1) {
                    layer.msg(data.msg, {time: 800, icon: 3})
                }
            }
        })

    })

});