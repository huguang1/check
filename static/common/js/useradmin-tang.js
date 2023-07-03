/**
 * Created by Owner on 2019/1/7.
 */

    // 渲染
var pagesize = 10;
var page = 1;
function showsysadm(page) {
    $.ajax({
        url: "/manage?p=" + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: "get",
        success: function (data) {
            if (data.count != 0) {
                var html_str = "<tr><th>ID</th><th>用户名</th><th>昵称</th><th>所属角色</th><th>拥有权限</th><th>操作</th></tr>";
                var x = "";
                $.each(data.data, function (i, award) {
                    html_str += '<tr><td>' + award.id + '</td><td>' + award.name + '</td><td>' + award.nickname + '</td><td>' + award.roles + '</td><td>' + award.pms + '</td><td><a class="btn_edit">编辑</a><a class="btn_delete" pk="' + award.id + '">删除</a></td></tr>'
                });
                var sPage = Paging(page, pagesize, data.count, 2, "showsysadm", 'cur', '', '上一页', '下一页');
                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showsysadm" + ")' />";
                sPage += "<span>总共" + data.num_pages + "页<span>";
                $("#page").html(sPage);
                $("#user_list").html(html_str);
            }
            // 下拉选择
            var select_list = "";
            for (var i = 0; i < data.roles.length; i++) {
                select_list += "<option value='" + data.roles[i].id + "'>" + data.roles[i].name + "</option>"
            }
            $('.selectpicker').html(select_list);

            $(".selectpicker").selectpicker({
                noneSelectedText: '请选择'
            });
            $(".selectpicker").selectpicker("refresh");
            //下拉
        }
    })
}
showsysadm(1);

// 渲染弹框
$(function () {
    /*编辑*/
    $(document).on('click', '.btn_edit', function () {
        var usrid = $(this).parents("tr").find("td").eq(0).text();  // 用户id
        var usr = $(this).parents("tr").find("td").eq(1).text();
        var name = $(this).parents("tr").find("td").eq(2).text();
        var usercode = $("#uu1").val(usr);
        var realname = $("#nc1").val(name);
        var pwdval = $('#pwd1').val();
        var realuserid = $('#uu1').attr("userid", usrid);
        var roles = $(this).parents("tr").find("td").eq(3).text();
        var rolelist = roles.split(",");
        $('.filter-option').html('');
        $('.dropdown-menu li').removeClass('selected');
        var optval = [];
        for (var i = 0; i < rolelist.length; i++) {
            $("#tankuang option").each(function (k) {
                var myrole = $(this).text();
                if (rolelist[i] == myrole) {
                    optval.push($(this).attr('value'));
                }
            });
            $('#tankuang').selectpicker('val', optval).trigger("change")
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
            area: ['540px', '660px'],
            shadeClose: true, //开启遮罩关闭
            content: $('#tanout')
        });

        var H = $('.layui-layer').height() - 42;
        $('.layui-layer-content').height(H - 42);

    });
    /*删除*/
    $(document).on('click', '.btn_delete', function () {
        var thisobj = $(this).closest('tr')
        var pk = $(this).attr('pk');
        layer.confirm('确定要删除吗？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
            $.ajax({
                url: '/deluser?pk=' + pk,
                dataType: 'json',
                type: 'get',
                cache: false,
                success: function (data) {
                    if (data.stat == 0) {
                        layer.msg(data.msg, {time: 800, icon: 1}, function () {
                            thisobj.remove()
                        });
                    } else {
                        layer.msg(data.msg, {time: 800, icon: 2})
                    }

                }
            })
        })

    });

});

function Trim(str)
{ var result;
    result = str.replace(/\s/g,"");
    return result;
}

// 添加管理员
$(document).on("click", "#btn_adduser", function () {
    var selete_data = $('#adduserselect').val();
    var username = $("#myusr").val();
    var nickname = $("#nicheng").val();
    var mypwd = $("#mypwd").val();
    if (username == '') {
        layer.msg("用户名不能为空", {time: 800, icon: 2});
        return false
    }
    if (mypwd == '') {
        layer.msg("密码不能为空", {time: 800, icon: 2});
        return false
    }
    if (selete_data == '') {
        layer.msg("请选择角色", {time: 800, icon: 2});
        return false
    }
    username = Trim(username);
    $.ajax({
        url: "/addmanage",
        type: "post",
        dataType: "json",
        cache: "false",
        data: {
            username: username,
            nickname: nickname,
            mypwd: mypwd,
            role: JSON.stringify(selete_data)
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1}, function () {
                    window.location.href = "/static/sysadm.html";
                });
            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon: 2});
            }
        }
    })
});

// 修改用户
$(document).on("click", "#mdfuser", function () {
    var selete_data = $('#tankuang').val();
    var userid = $("#uu1").attr("userid");
    var username = $("#uu1").val();
    var password = $("#pwd1").val();
    var nikname = $("#nc1").val();
    if (username == '') {
        layer.msg("用户名不能修改为空", {time: 800, icon: 2});
        return false
    } else if (userid == '') {
        layer.msg("获取不到id无法修改", {time: 800, icon: 2});
        return false
    } else if (selete_data == '') {
        layer.msg("未选择角色", {time: 800, icon: 2});
        return false
    }
    username = Trim(username);
    $.ajax({
        url: "/mdfuser",
        dataType: "json",
        type: "post",
        data: {
            userid: userid,
            username: username,
            selete_data: JSON.stringify(selete_data),
            password: password,
            nikname: nikname
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon: 1}, function () {
                    window.location.href = "/static/sysadm.html";
                });
            } else {
                layer.msg(data.msg, {time: 800, icon: 2});
            }
        }
    })
});

