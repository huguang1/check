/**
 * Created by Owner on 2019/1/24.
 */

    //渲染
    var pagesize = 10;
    var page = 1;
    function showtype (page){
        $.ajax({
            url:'/transfertype?p=' + page +'&size=' + pagesize,
            dataType:'json',
            cache:false,
            type:'get',
            success:function (data) {
                if(data.count != 0){
                    var html_str = '<tr><th>ID</th><th>名字</th><th>类型</th><th>操作</th></tr>';
                    $.each(data.data, function (i, award) {
                        //
                        html_str += '<tr><td>'+ award.id +'</td><td>'+ award.name + '</td><td>' + award.type +'</td><td><a class="btn_edit" editpk="' + award.id + '">编辑</a><a class="btn_delete" delpk="'+ award.id +'">删除</a></td></tr>'
                    });
                    var sPage = Paging(page, pagesize, data.count, 2, "showtype", 'cur', '', '上一页', '下一页');
                    sPage +="<input type='text' name='lname'   id='text_data' />";
                    sPage += "<input type='button' value='跳转' id='tiaozhuan' onclick='tiaozhuan(" + data.num_pages+ ","+"showtype" +")' />";
                    sPage += "<span>总共" + data.num_pages +"页<span>";
                    $("#page").html(sPage);
                    $("#type-list").html(html_str);
                }
            }
        })
    }
    showtype(1);

    function Trim(str)
    { var result;
        result = str.replace(/\s/g,"");
        return result;
    }

    // 添加类型
     $(document).on("click", "#addtype", function () {
        var name = $('#typename').val();
        var transfertype = $('#add-type').val();
        if(name==''){
            layer.msg("类型名不能为空", {time:1000, icon:2});
            return false
        }
        name = Trim(name);
        $.ajax({
            url:"/transfertype",
            type:"post",
            dataType:"json",
            data:{
                name:name,
                transfertype:transfertype
            },
            success:function (data) {
                if(data.stat==0){
                    layer.msg(data.msg, {time:800, icon:1},function () {
                    location.href = '/static/addtype.html';
                });

                }else if(data.stat==1){
                    layer.msg(data.msg, {time:1000, icon:2});
                    return false
                }
            }
        })

    });

   //删除类型
    $(document).on("click",".btn_delete",function (){
        var delpk = $(this).attr('delpk');
        layer.confirm('确定删除该类型?', {
        btn: ['确定', '取消'] //按钮
        }, function () {
            $.ajax({
                url:"/deltype",
                cache:false,
                type:"get",
                dataType:"json",
                data:{
                    delpk:delpk
                },
                success:function (data) {
                    if(data.stat==0){
                        layer.msg(data.msg, {time:800, icon:1},function () {
                        location.href = '/static/addtype.html';
                        });

                    }else if(data.stat==1){
                        layer.msg(data.msg, {time:1000, icon:2});
                    }
                }
        })

        })

        // if(confirm("确定删除类型?")){
        //     $.ajax({
        //         url:"/deltype",
        //         cache:false,
        //         type:"get",
        //         dataType:"json",
        //         data:{
        //             delpk:delpk
        //         },
        //         success:function (data) {
        //             if(data.stat==0){
        //                 alert(data.msg);
        //                 location.href='/static/addtype.html'
        //             }else if(data.stat==1){
        //                 alert(data.msg)
        //             }
        //         }
        // })
        // }
    });


// 编辑弹框
    $(document).on("click",".btn_edit", function () {
        var typeid = $(this).parents("tr").find("td").eq(0).text();
        var typename=$(this).parents("tr").find("td").eq(1).text();
        $("#name").val(typename);
        $('#name').attr('pk',typeid);
        layer.open({
          type: 1,
          title:'编辑',
          skin: 'layui-layer-demo', //样式类名
          closeBtn: 1, //显示关闭按钮
          anim: 2,
          area: ['540px', '330px'],
          shadeClose: true, //开启遮罩关闭
          content: $('#tanout')
        });
        var H = $('.layui-layer').height()-42;
        $('.layui-layer-content').height(H-42);
    });


//编辑修改转入类型
    $(document).on("click","#mdftype",function (){
    var editpk = $("#name").attr('pk');
    var name = $("#name").val();
    name = Trim(name);
        $.ajax({
            url:"/mdftype",
            cache:false,
            type:"post",
            dataType:"json",
            data:{
                editpk:editpk,
                name: name
            },
            success:function (data) {
                if(data.stat==0){
                    layer.msg(data.msg, {time:800, icon:1},function () {
                        location.href = '/static/addtype.html';
                    })
                }else if(data.stat==1){
                    layer.msg(data.msg, {time:1000, icon:2});
                }
            }
    })

});

