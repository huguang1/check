/**
 * Created by Owner on 2019/1/14.
 */
var pagesize = 10;
var page = 1;
function showlog(page) {
    $.ajax({
        url: '/log?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        success: function (data) {
            if (data.count != 0) {
                var html_str = "<tr><th>ID</th><th>操作人</th><th>操作内容</th><th>时间</th><th>IP</th><th>操作</th></tr>";
                $.each(data.data, function (i, award) {
                    //html_str += '<tr><td><input type="checkbox" id="'+ award.id +'"/>' + award.id + '</td><td>'+award.username+'</td><td>'+award.content+'</td><td>'+award.time+'</td><td><!--<a class="btn_edit" >修改</a>--><a class="btn_delete" pk="'+award.id+'" >删除</a></td></tr>'
                    html_str += '<tr><td><input type="checkbox" id="' + award.id + '"/>' + award.id + '</td><td>' + award.username + '</td><td>' + award.content + '</td><td>' + award.time + '</td><td>' + award.ip + '</td><td><a class="btn_delete" pk="' + award.id + '" >删除</a></td></tr>'
                });
                var sPage = Paging(page, pagesize, data.count, 2, "showlog", 'cur', '', '上一页', '下一页');
                sPage += "<input type='text' name='lname'   id='text_data' />";
                sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "showlog" + ")' />";
                sPage += "<span>总共" + data.num_pages + "页<span>";
                $("#page").html(sPage);
                $("#log-list").html(html_str);
            }
        }
    })
}
showlog(1);

// 删除单个日志
$(document).on("click", ".btn_delete", function () {
    var thisobj = $(this).closest('tr')
    var pk = $(this).attr('pk')
    layer.confirm('确定要删除吗？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
          $.ajax({
            url: "/dellog",
            dataType: "json",
            type: "get",
            cache: false,
            data: {
                pk: pk
            },
            success: function (data) {
                if (data.stat == 0) {
                     layer.msg(data.msg, {time: 800, icon: 1}, function () {
                         thisobj.remove()
                        });
                }else {
                    layer.msg(data.msg, {time: 800, icon: 2})
                }
            }
        })

})
});

// 删除选中日志
$(document).on("click", ".delete_some", function () {
    layer.confirm('确定要删除吗？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
        var data_info = [];
        $.each($('.table-exit :checkbox'), function () {
            if (this.checked) {
                data_info.push($(this).attr("id"));
            }
        });
        if (data_info.length == 0) {
            layer.msg("请选择删除内容", {time: 800, icon: 2})
            return false
        }
        $.ajax({
            url: "/dellog",
            type: "post",
            dataType: "json",
            data: {
                log_list: JSON.stringify(data_info)
            },
            success: function (data) {
                if (data.stat == 0) {
                    layer.msg(data.msg, {time: 800, icon: 1},function () {
                        $.each($('.table-exit :checkbox'), function () {
                            if (this.checked){
                                $(this).closest('tr').remove()
                            }
                            });
                    })
                } else {
                    layer.msg(data.msg, {time: 800, icon: 2})
                }
            }
        })
})
});

//搜索日志
function serchlog(page) {
    var mytime = $("#start_time").val();
    var username = $("#username").val();
    if(mytime==''&&username==''){
        layer.msg('请输入搜索内容', {time: 800, icon: 0})
        return false
    }
    $.ajax({
        url: '/sclog?p=' + page + '&size=' + pagesize,
        dataType: 'json',
        cache: false,
        type: 'get',
        data: {
            sctime: mytime,
            username: username
        },
        success: function (data) {
            if (data.stat == 0) {
                if (data.count != 0) {
                    var html_str = "<tr><th>ID</th><th>操作人</th><th>操作内容</th><th>时间</th> <!--<th>IP</th>--><th>操作</th></tr>";
                    $.each(data.data, function (i, award) {
                        html_str += '<tr><td><input type="checkbox" id="' + award.id + '"/>' + award.id + '</td><td>' + award.username + '</td><td>' + award.content + '</td><td>' + award.time + '</td><td><!--<a class="btn_edit" >修改</a>--><a class="btn_delete" pk="' + award.id + '" >删除</a></td></tr>'
                    });
                    var sPage = Paging(page, pagesize, data.count, 2, "serchlog", 'cur', '', '上一页', '下一页');
                    sPage += "<input type='text' name='lname'   id='text_data' />";
                    sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages + "," + "serchlog" + ")' />";
                    sPage += "<span>总共" + data.num_pages + "页<span>";
                    $("#page").html(sPage);
                    $("#log-list").html(html_str);
                }
            } else if (data.stat == 1) {
                layer.msg(data.msg, {time: 800, icon: 2});
                return false
            }
        }
    })
}
// 搜索
$(document).on("click", "#search", function () {
    serchlog(1)
});

$(document).on("click", ".remove_empty", function () {
    layer.confirm('确定要清除日志吗？', {
            btn: ['确定', '取消'] //按钮
        }, function () {
        $.ajax({
            url: "/delalllog",
            type: "get",
            dataType: "json",
            cache: false,
            success: function (data) {
                if(data.stat==0){
                    layer.msg(data.msg, {time: 800, icon: 1}, function () {
                        window.location.href = '/static/logInfo.html'
                    });
                }
            }
        })
    })
});