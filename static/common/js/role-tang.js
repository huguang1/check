// 渲染页面
var pagesize = 10;
var page = 1;
function showroleadm(page) {
    $.ajax({
        url: '/getrole?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        success: function (data) {
            if (data.count != 0) {
                var html_str = "<tr><th>ID</th> <th>角色名称</th> <th>拥有权限</th> <th>操作</th> </tr>";
                var x = "";
                $.each(data.data, function (i, award) {
                    html_str += '<tr><td>' + award.id + '</td><td>' + award.name + '</td><td>' + award.pms + '</td><td><a class="btn_edit">编辑</a><a class="btn_delete" pk="' + award.id + '">删除</a></td></tr>'
                });
                var sPage = Paging(page, pagesize, data.count, 2, "showroleadm", 'cur', '', '上一页', '下一页');
                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showroleadm" + ")' />";
                sPage += "<span>总共" + data.num_pages + "页<span>";
                $("#page").html(sPage);
                $("#role_list").html(html_str);
            }
            // 下拉选择
            var select_list = "";
            for (var i = 0; i < data.pms.length; i++) {
                select_list += "<option value='" + data.pms[i].id + "'>" + data.pms[i].name + "</option>"
            }
            $('#sele').html(select_list);
            $('#tansele').html(select_list);
            $(".selectpicker").selectpicker({
                noneSelectedText: '请选择'
            });
            $(".selectpicker").selectpicker("refresh");
        }
    })
}
showroleadm(1);

// 删除角色
$(document).on("click", ".btn_delete", function () {
    var thisobj = $(this).closest('tr')
    var pk = $(this).attr('pk')
    layer.confirm('确定删除该角色?', {
        btn: ['确定', '取消'] //按钮
    }, function () {
        $.ajax({
            url: '/delrole?pk=' + pk,
            dataType: 'json',
            type: 'get',
            cache: false,
            success: function (data) {
                if (data.stat == 0) {
                    layer.msg(data.msg, {icon: 1, time: 500}, function () {
                        thisobj.remove()
                    });
                }
            }
        })
    }, function () {
        layer.msg('操作取消', {
            time: 500 //2s后自动关闭
        });
        return;
    });
});

function Trim(str)
{ var result;
    result = str.replace(/\s/g,"");
    return result;
}

//添加角色
$(document).on("click", ".btn_adadm", function () {
    var myrole = $('#myrole').val();
    var select_data = $('.selectpicker').val();
    if (myrole == '') {
        layer.msg("角色名不能为空", {time:1000, icon:2});
        return false
    }
    if (select_data == '') {
        layer.msg("请选择角色", {time:1000, icon:3});
        return false
    }
    myrole = Trim(myrole);
    $.ajax({
        url: "/addrole",
        type: "post",
        dataType: "json",
        cache: "false",
        data: {
            pmsname: myrole,
            pms: JSON.stringify(select_data)
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time:1000, icon:1},function () {
                    window.location.href = "/static/roleadm.html";
                });

            } else if (data.stat == 1) {
                layer.msg(data.msg, {time:1000, icon:2})
            }

        }
    })
});

// 编辑弹框
$(document).on("click", ".btn_edit", function () {
    var roleid = $(this).parents("tr").find("td").eq(0).text();
    var rolename = $(this).parents("tr").find("td").eq(1).text();
    var pms = $(this).parents("tr").find("td").eq(2).text();
    $("#rolename").val(rolename);
    $("#rolename").attr("pk", roleid);
    var pmslist = pms.split(",");


    // 渲染多选
    $('.filter-option').html('');
    $('.dropdown-menu li').removeClass('selected');
    var optval = [];
    for (var i = 0; i < pmslist.length; i++) {
        $("#tansele option").each(function (k) {
            var mypms = $(this).text();
            if (pmslist[i] == mypms) {
                optval.push($(this).attr('value'));
            }
        });
        $('#tansele').selectpicker('val', optval).trigger("change");
    }

    $('.dropdown-menu li').each(function () {
        $(this).click(function () {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                $(this).find('a').attr('aria-selected', false);
            } else {
                $(this).addClass('selected');
                $(this).find('a').attr('aria-selected', true);
            }
        })
    });


    layer.open({
        type: 1,
        title: '编辑',
        skin: 'layui-layer-demo', //样式类名
        closeBtn: 1, //显示关闭按钮
        anim: 2,
        area: ['540px', '400px'],
        shadeClose: true, //开启遮罩关闭
        content: $('#tanout')
    });
    var H = $('.layui-layer').height() - 42;
    $('.layui-layer-content').height(H - 42);
});

//修改角色名和所有权限
$(document).on("click", "#mdfpms", function () {
    var roleid = $("#rolename").attr("pk");  // 角色id
    var rolename = $("#rolename").val();  // 角色名字
    var select_data = $('#tansele').val(); // 选中的值
    if (rolename == '') {
        layer.msg("角色名不能为空", {time:1000, icon:2});
        return false
    }
    if (select_data == '') {
        layer.msg("请为角色选择权限", {time:1000, icon:2});
        return false
    }
    rolename = Trim(rolename);
    $.ajax({
        url: "/mdfrole",
        type: "post",
        dataType: "json",
        cache: "false",
        data: {
            roleid: roleid,
            rolename: rolename,
            pmslist: JSON.stringify(select_data)
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time:800, icon:1},function () {
                    window.location.href = "/static/roleadm.html";
                });
            } else if (dara.stat == 1) {
                 layer.msg(data.msg, {time:1000, icon:2})
            }

        }
    })
});