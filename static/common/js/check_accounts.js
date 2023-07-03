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
				console.log(data.date_list);
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
	// 时间增加
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
					var a = '';
					for(var i=0; i<data.mon_list.length; i++) {
                        a += data.mon_list[i];
                    }
                    for(var i=0; i<data.day_list.length; i++) {
                        a += data.day_list[i];
                    }
                    console.log(a);
                    check_account(a);
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
					var a = '';
					for(var i=0; i<data.mon_list.length; i++) {
                        a += data.mon_list[i];
                    }
                    for(var i=0; i<data.day_list.length; i++) {
                        a += data.day_list[i];
                    }
                    console.log(a);
                    check_account(a);
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

// 获取到所有的记录的统计结果
// function check_account(date_list) {
//     $.ajax({
//         url: '/checkaccount',
//         type: 'post',
//         dataType: 'json',
//         data: {'date_list': date_list},
//         success:function (data) {
//             if(data.status){
//                 console.log(data.msg)
//             }else {
//                 console.log(data.user_balance);
//                 $.each(data.user_balance, function (i, item) {
//                     html ='';
//                     if(item.user == ''){
//                         $('#inamount').html(item.in_amount);
//                         $('#realinamount').html(item.real_in_amount);
//                         $('#nowbalance').html(item.now_balance);
//                         $('#fees').html(item.fees);
//                         $('#outamount').html(item.out_amount);
//                         $('#newamount').html(item.new_amount);
//                         $('#removezong').html(item.remove);
//                         $('#newamountall').html(item.new_amount);
//                         $('#remove').html(item.remove)
//                     }else {
//                         // in_amount:转入
//                         // real_in_amount:实际转入
//                         // fees:手续费
//                         // now_balance:现余额
//                         // out_amount:转出,就是中转
//                         // new_amount:外转入
//                         // remove:移除
//                         var name = '#usernames' + i;
//                         var amount = '#inamount' + i; // 总入款
//                         var realamount = '#realinamount' + i; //实入款
//                         var balance = '#nowbalance' + i; // 现余额
//                         var fees = '#fees' + i;   // 手续费
//                         var outamount = '#outamount' + i;  // 中转
//                         var newamount = '#newamount' + i;  // 外转入
//                         var remove = '#remove' + i;  //移除
//                         $(name).html(item.user);
//                         $(amount).html(item.in_amount);
//                         $(realamount).html(item.real_in_amount);
//                         $(balance).html(item.now_balance);
//                         $(fees).html(item.fees);
//                         $(outamount).html(item.out_amount);
//                         $(newamount).html(item.new_amount);
//                         $(remove).html(item.remove)
//                     }
//                 })
//             }
//         },
//         error:function () {
//             console.log('服务器错误，请重试！')
//         }
//     });
//     $.ajax({
//         url: '/checkout',
//         type: 'post',
//         dataType: 'json',
//         data: {'date_list': date_list},
//         success:function (data) {
//             if(data.status == 0){
//                 $.each(data.inf, function (i, item) {
//                     if(item.name == "total"){
//                         $('#am').html(item.amount);
//                         $('#re').html(item.real);
//                         $('#ba').html(item.balance);
//                         $('#fe').html(item.fees);
//                         $('#out').html(item.out);
//                         $('#in').html(item.new);
//                         $('#rm').html(item.remove);
//
//                     }else {
//                         var name = '#outname' + i;
//                         var amount = '#am' + i;
//                         var realamount = '#re' + i;
//                         var balance = '#ba' + i;
//                         var fees = '#fe' + i;
//                         var out = '#out' + i;
//                         var income = '#in' + i;
//                         var remove  ='#rm' + i;
//                         $(name).html(item.name);
//                         $(amount).html(item.amount);
//                         $(realamount).html(item.real);
//                         $(balance).html(item.balance);
//                         $(fees).html(item.fees);
//                         $(out).html(item.out);
//                         $(income).html(item.new);
//                         $(remove).html(item.remove)
//
//                     }
//                 })
//             }else {
//                 console.log(data.msg)
//             }
//         },
//         error:function () {
//             console.log('服务器错误，请重试！')
//         }
//     })
// }

// 获取到所有的记录的统计结果
function check_account(date_list) {
    $.ajax({
        url: '/checkaccount',
        type: 'post',
        dataType: 'json',
        data: {'date_list': date_list},
        success:function (data) {
            if(data.status){
                console.log(data.msg)
            }else {
                console.log(data.user_balance);
                var tableHtml = '<tr><th colspan="5">入款线内余额</th><th colspan="4">对账额度</th></tr>' +
                    '<tr><td colspan="5"><input type="text" class="input_wrap" id="depositbalance"/></td><td colspan="4" id="total_balance"></td></tr>' +
                    '<tr><td>用户</td><td>实入款</td><td>总入款</td><td>现余额</td><td>手续费</td><td>中转</td><td>外转入</td><td>外转出</td><td>移除</td></tr>';
                var totalhtml ='';
                $.each(data.user_balance, function (i, item) {
                    if(item.user=='total'){
                        totalhtml += '<tr><td>'+item.user+'</td><td id="realinamount">'+item.real_in_amount+'</td><td>'+item.in_amount+'</td><td id="nowbalance">'+item.now_balance+'</td><td>'+item.fees+'</td><td id="transit">'+item.transit+'</td><td id="newamount">'+item.new_amount+'</td><td id="outamount">'+item.out_amount+'</td><td id="remove">'+item.remove+'</td></tr>';
                    }else {
                        tableHtml += '<tr><td>'+item.user+'</td><td>'+item.real_in_amount+'</td><td>'+item.in_amount+'</td><td>'+item.now_balance+'</td><td>'+item.fees+'</td><td>'+item.transit+'</td><td>'+item.new_amount+'</td><td>'+item.out_amount+'</td><td>'+item.remove+'</td></tr>';
                    }
                });
                $('#incheck').html("");
                $('#incheck').append(tableHtml);
                $('#incheck').append(totalhtml);
                getyesterdaybalance(date_list)
            }
        },
        error:function () {
            console.log('服务器错误，请重试！')
        }
    });
    $.ajax({
        url: '/checkout',
        type: 'post',
        dataType: 'json',
        data: {'date_list': date_list},
        success:function (data) {
            if(data.status == 0){
                var outHtml = '<tr><td>用户</td><td>实出款</td><td>总出款</td><td>现余额</td><td>手续费</td><td>中转</td><td>费用</td><td>新增</td><td>移除</td></tr>';
                var totalhtml ='';
                $.each(data.inf, function (i, item) {
                    if(item.name=='total'){
                        totalhtml += '<tr><td>'+item.name+'</td><td id="re">'+item.real+'</td><td>'+item.amount+'</td><td id="ba">'+item.balance+'</td><td>'+item.fees+'</td><td id="tr">'+item.transit+'</td><td id="out">'+item.out+'</td><td id="in">'+item.new+'</td><td id="rm">'+item.remove+'</td></tr>';
                    }else {
                        outHtml += '<tr><td>'+item.name+'</td><td>'+item.real+'</td><td>'+item.amount+'</td><td>'+item.balance+'</td><td>'+item.fees+'</td><td>'+item.transit+'</td><td>'+item.out+'</td><td>'+item.new+'</td><td>'+item.remove+'</td></tr>';
                    }
                });
                $('#outcheck').html("");
                $('#outcheck').append(outHtml);
                $('#outcheck').append(totalhtml)
            }else {
                console.log(data.msg)
            }
        },
        error:function () {
            console.log('服务器错误，请重试！')
        }
    })
}

// 获取昨天银行卡的最后余额
function getyesterdaybalance(date_list) {
    $.ajax({
        url: '/getyesterdaybalance',
        type: 'get',
        dataType: 'json',
        data: {'date_list': date_list},
        success: function (data) {
            if(data.status){
                console.log(data.msg)
            }else {
                console.log(data.balance);
                $('#depositbalance').val(data.balance)
            }
        },
        error: function () {
            console.log('服务器错误，请重试！')
        }
    });
}

// 修改昨天银行卡内的余额
$(function () {
    $(document).on('blur','#depositbalance',function () {
        var money = $(this).val();
        var now_time = $('#da_date_mon').html()+$('#xiao_date_mon').html()+$('#da_date_day').html()+$('#xiao_date_day').html();
        if(money && now_time){
            $.ajax({
                url: '/changeyesterdaybalance',
                type: 'post',
                dataType: 'json',
                data: {'money': money, 'now_time': now_time},
                success: function (data) {
                    if(data.status){
                        console.log(data.msg);
                        getyesterdaybalance(now_time)
                    }else {
                        console.log(data.msg);
                        getyesterdaybalance(now_time)
                    }
                },
                error: function () {
                    console.log('服务器错误，请重试！')
                }
            })
        }else {
            console.log('没有获取到钱和时间的信息！')
        }
    });
});

// 获取到当前的时间
function check_now_account() {
    $.ajax({
        url: "/indexinfo",
        type: "get",
        dataType: "json",
        data: {},
        success: function (data) {
            if(data.status){
                console.log(data.msg)
            }else {
                console.log(data.date_list);
                var a = '';
                for(var i=0; i<data.date_list.length; i++) {
                    a += data.date_list[i];
                }
                check_account(a);
            }
        },
        error:function () {
            console.log('服务器错误，请重试！')
        }
    });
}
check_now_account();

// 实现一键对账功能
$('#yijianduizhang').click(function () {
    var depositbalance = $('#depositbalance').val();  // 入款线内余额
    var nowbalance = $('#nowbalance').html();  // 现余额
    var outamount = $('#outamount').html();  // 外转出
    var realinamount = $('#realinamount').html();  // 实入款
    var remove = $('#remove').html();  // 移除
    var newamount = $('#newamount').html();  // 外转入，新增
    var transit = $('#transit').html();   // 中转手续费
    // 转出卡的相关数据
    var re = $('#re').html();  // 实出款
    var ba = $('#ba').html();  // 现余额
    var out = $('#out').html(); // 费用，包含转出给小金库，大金库，各种费用
    var inamount = $('#in').html(); // 新增，包含在线
    var rm = $('#rm').html();  // 移除
    var tr = $('#tr').html();  // 中转手续费
    $.ajax({
        url:'/reconcilia',
        dataType:'json',
        type: 'post',
        data: {'depositbalance': depositbalance, 'nowbalance': nowbalance, 'outamount': outamount,
        'realinamount': realinamount, 'remove': remove, 'newamount': newamount, 'transit': transit, 're': re, 'ba': ba,
        'out': out, 'inamount': inamount, 'rm': rm, 'tr': tr},
        success: function (data) {
            if(data.status){
                console.log(data.msg)
            }else {
                $('#total_balance').html(data.total_balance)
            }
        },
        error: function () {
            console.log('服务器错误，请重试！')
        }
    })
});

// 实现一键下载报表功能
$('#downloadcheck').click(function () {
    var date_day = $('#da_date_day').html() + $('#xiao_date_day').html();
    var date_mon = $('#da_date_mon').html() + $('#xiao_date_mon').html();
    console.log(date_day);
    console.log(date_mon);
    if(date_day && date_mon){
        var username = $('#setusername').html();
        if(username==''){
            console.log('没有获取到用户的信息')
        }else {
            url = '/downloadcheck?username=' + username + '&date_day=' + date_day + '&date_mon=' + date_mon;
            window.location.href = url
        }
    }else {
        console.log('没有获取到时间信息')
    }
});



