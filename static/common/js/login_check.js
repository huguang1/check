/**
 * Created by Owner on 2019/1/9.
 */
// 1获取到用户的登陆信息
function get_user_cookie() {
	$.ajax({
		url:'/setusername',
		type:'get',
		dataType:'json',
		data:{},
		success:function (data) {
			if(data.status){
				location.href = "/static/login.html"
			}else {
				$('#setusername').html(data.username)
			}
        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	})
}
get_user_cookie();