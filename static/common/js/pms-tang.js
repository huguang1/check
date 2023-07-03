/**
 * Created by Owner on 2019/1/7.
 */

    // 渲染页面
var pagesize = 10;
var page = 1;
function showquxianadm(page) {
    $.ajax({
        url: '/getpms?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        success: function (data) {
            if (data.count != 0) {
                var html_str = "<tr><th>ID</th> <th>权限名称</th> <th>描述</th> <th>操作</th> </tr>";
                var x = "";
                $.each(data.data, function (i, award) {
                    html_str += '<tr><td>' + award.id + '</td><td>' + award.name + '</td><td>' + award.des + '</td><td><a class="btn_edit">编辑</a><a class="btn_delete" pk="' + award.id + '">删除</a></td></tr>'
                });
                var sPage = Paging(page, pagesize, data.count, 2, "showquxianadm", 'cur', '', '上一页', '下一页');
                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showquxianadm" + ")' />";
                sPage += "<span>总共" + data.num_pages + "页<span>";
                $("#page").html(sPage);
                $("#pms_list").html(html_str);
            }
        }
    })
}
showquxianadm(1);

//删除权限
$(document).on("click", ".btn_delete", function () {
    var thisobj = $(this).closest('tr')
    var pk = $(this).attr('pk')
        layer.confirm('确定要删除吗？', {
        btn: ['确定', '取消'] //按钮
    }, function () {
        $.ajax({
            url: '/delpms?pk=' + pk,
            dataType: 'json',
            type: 'get',
            cache: false,
            success: function (data) {
                if (data.stat == 0) {
                    layer.msg(data.msg, {icon: 1, time:500}, function () {
                        thisobj.remove()
                    });
                }else {
                    layer.msg(data.msg, {icon: 1});
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

// 添加权限
$(document).on("click",".btn_adadm",function () {
    var mypms = $('#mypms').val();
    if(mypms == ''){
        layer.msg("权限名不能为空", {time:1000, icon:2});
        return false
    }
    mypms = Trim(mypms);
    $.ajax({
        url:"/addpms",
        type:"post",
        dataType:"json",
        cache:"false",
        data:{
            pmsname:mypms,
            des:$('#des').val()
        },
        success:function (obj) {
            if(obj.stat==0){
                layer.msg(obj.msg,{time: 1000, icon:1},function () {
                    window.location.href = "/static/quxianadm.html";
                });
            }else if(obj.stat==1){
                layer.msg(obj.msg, {time:800, icon:2 });
            }
        }
    })
});

// 修改弹框
$(document).on("click", ".btn_edit", function () {
    var pmsid = $(this).parents("tr").find("td").eq(0).text();
    var pmsname = $(this).parents("tr").find("td").eq(1).text();
    var pmsdec = $(this).parents("tr").find("td").eq(2).text();
    $("#pmsname").val(pmsname);
    $("#decname").val(pmsdec);
    $("#pmsname").attr("pk", pmsid);

    layer.open({
        type: 1,
        title: '编辑',
        skin: 'layui-layer-demo', //样式类名
        closeBtn: 1, //显示关闭按钮
        anim: 2,
        area: ['540px', '330px'],
        shadeClose: true, //开启遮罩关闭
        content: $('#tanout')
    });
    var H = $('.layui-layer').height() - 42;
    $('.layui-layer-content').height(H - 42);
});

//编辑
$(document).on("click", "#mdfpms", function () {
    var pmsid = $("#pmsname").attr("pk");
    var pmsname = $("#pmsname").val();
    var decname = $("#decname").val();
    pmsname = Trim(pmsname);
    $.ajax({
        url: "/mdfpms",
        dataType: "json",
        type: "post",
        cache: false,
        data: {
            pmsid: pmsid,
            pmsname: pmsname,
            decname: decname
        },
        success: function (data) {
            if (data.stat == 0) {
                layer.msg(data.msg, {time: 800, icon:1}, function () {
                    window.location.href = "/static/quxianadm.html"
                });
            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon:2});
            }
        }
    })
});