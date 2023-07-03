/**
 * Created by xiaoli on 19-1-1.　
 */
$(function () {
  // 验证码
    $("#validate_pc").attr('src','/verifycode?' + Math.random());});
    function change_validate(){
        $('.chkcodeimg img').attr('src','/verifycode?'+Math.random());
    }
    $(document).keyup(function (event) {
        if (event.keyCode == 13) {
            $(".btn-log").click();
        }
});

$('.form-group input').focus(function () {
    $('.tlip').hide()
});

$(function () {
    // 登陆视图请求
    $('.btn-log').click(function () {
        if ($("#remember_num").is(':checked')){
            var remember_num = "on";
        }else {
            var remember_num = "off";
        }
        $.ajax({
            url:'/login',
            type:'POST',
            dataType:'json',
            data:{
                'username':$('#username').val(),
                'password':$('#password').val(),
                'yan_txt':$('.yan_txt').val(),
                'remember_num': remember_num
            },
            success:function (data) {
                if(data.status){
                    $('.tlip').show()
                }else {
                    $.ajax({
                        url: '/getuserpermissionbankcard',
                        type: 'get',
                        dataType: 'json',
                        data: {'username': $('#username').val()},
                        success:function (data) {
                            if(data.status){
                                alert('获取用户信息失败')
                            }else {
                                var group = data.bankcardtype;
                                if(group=='出款银行'){
                                    location.href = "/static/indexout.html";
                                }else {
                                    location.href = "/static/index.html";
                                }
                            }
                        }
                    });
                }
            },
            error:function () {
                alert('服务器超时，请重试！')
            }

        });
    })
});

var ca = document.cookie.split(';');
for(var i=0; i<ca.length; i++){
    var c = ca[i].trim();
    listrem = c.split('=');
    if((listrem[0] == 'remember') && (listrem[1] == '1')){
        $('#remember_num').attr("checked",'false');
        for(var a=0; a<ca.length; a++){
            var d = ca[a].trim();
            listrem1 = d.split('=');
            if(listrem1[0] == 'username'){
                $('#username').val(listrem1[1])
            }
        }
    }
}
