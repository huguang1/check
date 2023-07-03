/**
 * Created by python on 19-1-13.
 */
$(function(){
	$(document).on('click','.childnav>li>a',function() {
			$(this).siblings().slideToggle('500');
			$(this).parent().siblings().find('a').children().removeClass('caret').end().siblings().slideUp('500');
			if($(this).siblings().length>0){
				$(this).children().toggleClass('caret');
			}
	});
});

// ********************************************************************************************


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
				$('#setusername').html(data.username);
                // 首页展示
                $.ajax({
                    url:'/getuserpermissionbankcard',
                    type:'get',
                    dataType:'json',
                    data:{'username': data.username},
                    success:function (data) {
                        if(data.status){
                            console.log('获取用户信息错误')
                        }else {
                            var group = data.group;
                            var bankcard = data.bankcard;

                            // 5获取时间
                            get_time();

                            // 6获取银行卡的展示
							console.log('年多少了发生对方了收到浪费的')
							console.log(group)
                            if(group=='总管理员'){
                                get_bankcard_list();
                                get_bankcard_list_out();
                            }else if(group=='出款管理员'){
                                get_bankcard_list_out();
                                $('#in_manage').css("display","none");
								$('#systom_manage').css("display","none");
                            }else {
                                get_bankcard_list();
                                $('#out_manage').css("display","none");
                                $('#systom_manage').css("display","none");
                            }
                        }
                    },
                    error:function () {
                        console.log('服务器错误，请重试！')
                    }
                });
			}
        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	})
}
get_user_cookie();



// ************************************************************************


// 5获取时间
function get_time() {
	var html = '';
	$.ajax({
		url:"/indexinfo",
		type:"get",
		dataType:"json",
		data:{},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				var ti = data.date_list;
				html += '<span class="preT"><b class="date_sub"></b></span><span class="addT"><b class="date_add"></b></span>' +
					'<p class="nav_date"><span id="da_date_day">' + ti[2] + '</span><span id="xiao_date_day">' + ti[3] + '</span></p>'+
					'<p class="date_month"><span id="da_date_mon">'+ ti[0] +'</span><span id="xiao_date_mon">'+ ti[1] +'</span><span>月</span></p>'+
					'<p class="date_hour"><span>'+ ti[4] +'</span><span>'+ ti[5] +'</span></p>'+
					'<p class="date_minute"><span>'+ ti[6] +'</span><span>'+ ti[7] +'</span></p>';
				$('.navtimes').html(html);
			}
		},
		error:function () {
			console.log('服务器错误，请重试！')
		}
	});
}

// 时间增加，减少
$(function () {
	// 时间增加，减少
	$('.navtimes').on('click','.addT b',function () {
		var date_day = $('#da_date_day').html() + $('#xiao_date_day').html();
		var date_mon = $('#da_date_mon').html() + $('#xiao_date_mon').html();
		var html = '';
		$.ajax({
			url:'/dateadd',
			type:'POST',
			dataType:'json',
			data:{'date_play': date_day, 'date_mon': date_mon},
			success:function (data) {
				if(data.status){
					console.log('服务器错误，请重试！')
				}else {
					$('#da_date_day').html(data.day_list[0]);
					$('#xiao_date_day').html(data.day_list[1]);
					$('#da_date_mon').html(data.mon_list[0]);
					$('#xiao_date_mon').html(data.mon_list[1]);
				}
            },
			error:function () {
				console.log('服务器错误，请重试')
            }
		})
    });


	$('.navtimes').on('click', '.preT b', function () {
		var date_day = $('#da_date_day').html() + $('#xiao_date_day').html();
		var date_mon = $('#da_date_mon').html() + $('#xiao_date_mon').html();
		$.ajax({
			url:'/datesub',
			type:'POST',
			dataType:'json',
			data:{'date_play': date_day, 'date_mon': date_mon},
			success:function (data) {
				if(data.status){
					console.log('服务器错误，请重试！')
				}else {
					$('#da_date_day').html(data.day_list[0]);
					$('#xiao_date_day').html(data.day_list[1]);
					$('#da_date_mon').html(data.mon_list[0]);
					$('#xiao_date_mon').html(data.mon_list[1]);
				}
            },
			error:function () {
				console.log('服务器错误，请重试！')
            }
		})
    })
});


// 6入款银行卡的展示
function get_bankcard_list() {
	var username = $('#setusername').html();
	if (username){
		$.ajax({
		url:'/getbankcardlist',
		type:'get',
		dataType:'json',
		data:{'username': username},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				var html = '';
				html += '<ul class="nav childnav" id="rukuan">';
				$.each(data.bank_list, function(i, bank_dict){
					html += '<li><a href="javascript:;">'+ bank_dict.bank_name +'<b class="rightico"></b></a><ol class="third-nav">';
					$.each(bank_dict.bankcard_list, function (i, bankcard_dict) {
						html += '<li><a class="setck" href="index.html" >'+ bankcard_dict.bankcard_name +'</a></li>'
                    });
					html += '</ol></li>'
				});
				html += '</ul>';
				$('#ui-inmanage').html(html);
			}
        },
		error:function () {
			console.log('服务器超时，请重试！')
        }
	})
	}else {
		console.log('没有获取到用户信息')
	}
}


// 6出款银行卡展示
function get_bankcard_list_out() {
	var username = $('#setusername').html();
	if (username){
		$.ajax({
		url:'/getbankcardlistout',
		type:'get',
		dataType:'json',
		data:{'username': username},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				var html = '';
				html += '<ul class="nav childnav">';
				$.each(data.bank_list, function (i, bank_dict) {
					html += '<li><a href="javascript:;">'+ bank_dict.bank_name +'<b class="rightico"></b></a><ol class="third-nav">';
					$.each(bank_dict.bankcard_list, function (i, bankcard_dict) {
						html += '<li><a class="setckout" href="indexout.html">'+ bankcard_dict.bankcard_name +'</a></li>'
                    });
					html += '</ol></li>'
                });
				html += '</ul>';
				$('#ui-chuk').html(html)
			}
        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	})
	}else {
		console.log('没有获取到用户信息')
	}
}


// 登出
$(function () {
	// 登出
	$('#logout_out').click(function () {
		$.ajax({
            url:'/logout',
            type:'post',
            dataType:'json',
            success:function (data) {
                if(data.status){
                    console.log('退出失败，请重试！')
                }else {
                    location.href = "/static/login.html";
                }
            },
            error:function () {
                console.log('服务器超时，请重试！')
            }
        });
    })
});


