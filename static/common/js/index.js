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

function setCookie(cname,cvalue,exdays){
    var d = new Date();
    d.setTime(d.getTime()+(exdays*24*60*60*1000));
    var expires = "expires="+d.toGMTString();
    document.cookie = cname+"="+cvalue+"; "+expires;
}
function getCookie(cname){
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name)==0) { return c.substring(name.length,c.length); }
    }
    return "";
}


// 这个是当有点击事件发生的时候就会向这个cookie中写入数据
var x = getCookie('navMsgName');
x = (x=='')?[]:JSON.parse(x);
$(document).on('click','.setck',function () {
    var x = getCookie('navMsgName');
    x = (x=='')?[]:JSON.parse(x);
	var url=$(this).attr('href');
	var name=$(this).text();
	var hasexit=true;
    var  navMsg= x;
	if(!navMsg[0] == ''){
        navMsg[0].statu=='o';
        for(var i=0;i<navMsg.length;i++){
            if(navMsg[i].name==name){
            	console.log(i);
                navMsg[i].statu='on';
                hasexit=false;
            }else{
                navMsg[i].statu='o';
            }
        }
	}
	if(hasexit){navMsg.push({url:url,name:name,statu:'on'});}
	navMsg=JSON.stringify(navMsg);
	setCookie('navMsgName',navMsg);
});


var Y = getCookie('navMsgNameOut');
Y = (Y=='')?[]:JSON.parse(Y);
$(document).on('click','.setckout',function () {
    var x = getCookie('navMsgNameOut');
    x = (x=='')?[]:JSON.parse(x);
	var url=$(this).attr('href');
	var name=$(this).text();
	var hasexit=true;
    var  navMsg= x;
	if(!navMsg[0] == ''){
        navMsg[0].statu=='o';
        for(var i=0;i<navMsg.length;i++){
            if(navMsg[i].name==name){
            	console.log(i);
                navMsg[i].statu='on';
                hasexit=false;
            }else{
                navMsg[i].statu='o';
            }
        }
	}
	if(hasexit){navMsg.push({url:url,name:name,statu:'on'});}
	navMsg=JSON.stringify(navMsg);
	setCookie('navMsgNameOut',navMsg);
});


// 展示cookie中的银行卡
function get_cookie_bankcard() {
    var x = getCookie('navMsgName');
    x = (x=='')?[]:JSON.parse(x);
     if(x.length>10){

                var navMsg=x;
                navMsg.reverse();
                console.log(navMsg);
                var newX = navMsg.splice(0,4);
                console.log(newX);
                newX=JSON.stringify(newX);
                setCookie('navMsgName',newX);
                get_cookie_bankcard();

            }

  // else if(!x[0]==''&&x.length<=4){
    else if(!x[0]==''){
        var hm='';
        $.each(x,function (i,item) {

            hm += '<li class="'+item.statu+'"><a href="'+item.url+'" class="setck">'+item.name+'<i class="icoclose" data_eq="'+i+'"></i></a></li>'

        });

        $('.tabsall .clearfix').html(hm);
        console.log(22);
    }else{$('.tabsall').hide()}
}
get_cookie_bankcard();




// 删除cookie中的信息
$('.icoclose').click(function () {

	$(this).parent().parent().remove();
    var navMsg=x;
    navMsg.splice($(this).attr('data_eq'),1);
    navMsg=JSON.stringify(navMsg);
    setCookie('navMsgName',navMsg);
    return false;
});

// 获取到当前银行卡名字和当前时间的信息
function get_nowbankcard_name() {
    get_time();
    var now_time = $('#da_date_mon').html()+$('#xiao_date_mon').html()+$('#da_date_day').html()+$('#xiao_date_day').html();
    var x = getCookie('navMsgName');
    x = (x=='')?[]:JSON.parse(x);
    var navMsg= x;
    var now_bankcard = '';
    if(!navMsg[0] == ''){
        for(var i=0;i<navMsg.length;i++){
            if(navMsg[i].statu=='on'){
                now_bankcard += navMsg[i].name
            }else{
                now_bankcard += ''
            }
        }
    }
    return [now_bankcard,now_time]
}

// 获取到当前的银行卡和显示的时间
function get_showbankcard_name() {
    var now_time = $('#da_date_mon').html()+$('#xiao_date_mon').html()+$('#da_date_day').html()+$('#xiao_date_day').html();
    var x = getCookie('navMsgName');
    x = (x=='')?[]:JSON.parse(x);
    var navMsg= x;
    var now_bankcard = '';
    if(!navMsg[0] == ''){
        for(var i=0;i<navMsg.length;i++){
            if(navMsg[i].statu=='on'){
                now_bankcard += navMsg[i].name
            }else{
                now_bankcard += ''
            }
        }
    }
    return [now_bankcard,now_time]
}


// 仅仅获取当前银行卡名字
function get_onlybankcard_name() {
    var x = getCookie('navMsgName');
    x = (x=='')?[]:JSON.parse(x);
    var navMsg= x;
    var now_bankcard = '';
    if(!navMsg[0] == ''){
        for(var i=0;i<navMsg.length;i++){
            if(navMsg[i].statu=='on'){
                now_bankcard += navMsg[i].name
            }else{
                now_bankcard += ''
            }
        }
    }
    return now_bankcard
}

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
			    console.log(data.username);
				$('#setusername').html(data.username);
                // 首页展示
                $.ajax({
                    url:'/getuserpermissionbankcard',
                    type:'get',
                    dataType:'json',
                    data:{'username': data.username},
                    success:function (data) {
                        if(data.tat){
                            console.log('nihao');
                            location.href = "/static/addBank.html";
                        }
                        else if(data.status){
                            console.log('获取用户信息错误')
                        }else {
                            var group = data.group;
                            var bankcard = data.bankcard;
                            console.log(bankcard);
                            // 4获取转出取的银行
                            wai_bankcard();

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

                            // 将银行卡添加到cookie中
                            if(getCookie('navMsgName')==''){
                                // 2加载首页时，直接获取最终余额
                                get_banlance(bankcard);

                                // 3获取到当前银行卡最新余额
                                get_checkbankcard(bankcard);

                                // 7获取银行卡全部信息
                                bankrecord(1, bankcard);

                                // 9获取总的银行卡的对账额度
                                check_all_bankcard();
                                if(data.bankcardtype=='入款银行'){
                                    var navMsg ='[{"url":"index.html","name":"'+ bankcard +'","statu":"on"}]';
                                }else {
                                    var navMsg ='[{"url":"indexout.html","name":"'+ bankcard +'","statu":"on"}]';
                                }
                                
                                setCookie('navMsgName',navMsg);
                                // 展示cookie中的银行卡
                                get_cookie_bankcard();
                                $('.tabsall').show();

                                // 8统计当前银行卡的对账额度
                                check_now_bankcard();
                            }

                            var bankcardcookies = getCookie('navMsgName');
                            if(bankcardcookies=='[]'){
                                // 2加载首页时，直接获取最终余额
                                get_banlance(bankcard);

                                // 3获取到当前银行卡最新余额
                                // get_checkbankcard(bankcard);

                                // 7获取银行卡全部信息
                                bankrecord(1, bankcard);

                                // 8统计当前银行卡的对账额度
                                check_now_bankcard();

                                // 9获取总的银行卡的对账额度
                                check_all_bankcard();

                            }else {
                                var list1 = get_nowbankcard_name();
                                var now_bankcard = list1[0];

                                if(now_bankcard==''){
                                    // 2加载首页时，直接获取最终余额
                                    get_banlance(bankcard);

                                    // 3获取到当前银行卡最新余额
                                    // get_checkbankcard(bankcard);

                                    // 7获取银行卡全部信息
                                    bankrecord(1, bankcard);

                                    // 8统计当前银行卡的对账额度
                                    check_now_bankcard();

                                    // 9获取总的银行卡的对账额度
                                    check_all_bankcard();
                                }else {
                                    // 2加载首页时，直接获取最终余额
                                    get_banlance(now_bankcard);

                                    // 3获取到当前银行卡最新余额
                                    // get_checkbankcard(now_bankcard);

                                    // 7获取银行卡全部信息
                                    bankrecord(1, now_bankcard);

                                    // 8统计当前银行卡的对账额度
                                    check_now_bankcard();

                                    // 9获取总的银行卡的对账额度
                                    check_all_bankcard();
                                }
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

$(function(){
    var scrWidth = $('.tabsall ul li').width();
    $('.tabsall ul li').each(function(){
       scrWidth+= $(this).width()+10;
    });
    $('.tabsall ul').width(scrWidth);
    $('.tabsall ').perfectScrollbar();

    var DATAPICKERAPI = {
        // 默认input显示当 前月,自己获取后填充
        activeMonthRange: function () {
            return {
                begin: moment().set({ 'date': 1, 'hour': 0, 'minute': 0, 'second': 0 }).format('YYYY-MM-DD HH:mm:ss'),
                end: moment().set({ 'hour': 23, 'minute': 59, 'second': 59 }).format('YYYY-MM-DD HH:mm:ss')
            }
        },

        shortcutMonth: function () {
            // 当月
            var nowDay = moment().get('date');
            var prevMonthFirstDay = moment().subtract(1, 'months').set({ 'date': 1 });
            var prevMonthDay = moment().diff(prevMonthFirstDay, 'days');
            return {
                now: '-' + nowDay + ',0',
                prev: '-' + prevMonthDay + ',-' + nowDay
            }
        },

        // 注意为函数：快捷选项option:只能同一个月份内的
        rangeMonthShortcutOption1: function () {
            var result = DATAPICKERAPI.shortcutMonth();
            return [{
                name: '昨天',
                day: '-1,-1',
                time: '00:00:00,23:59:59'
            }, {
                name: '这一月',
                day: result.now,
                time: '00:00:00,'
            }, {
                name: '上一月',
                day: result.prev,
                time: '00:00:00,23:59:59'
            }];
        },
        // 快捷选项option
        rangeShortcutOption1: [{
            name: '最近一周',
            day: '-7,0'
        }, {
            name: '最近一个月',
            day: '-30,0'
        }, {
            name: '最近三个月',
            day: '-90, 0'
        }]
    };

    // 外转入的类型查询
    var inTypeHtml = "";
    $.ajax({
		url:'/transferintype',
		type:'get',
		dataType:'json',
		success:function (data) {
            // console.log(data.bankcard_list);
            $.each(data.data, function (i, item) {
                inTypeHtml += "<option>"+item.name+"</option>"
            });
            // console.log(html);
            if(inTypeHtml==''){inTypeHtml="<option></option>"}
            $('#transfer_in_type').html(inTypeHtml)

        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	});

    // 外转出的类型查询
    var outTypeHtml = "";
    $.ajax({
		url:'/transferouttype',
		type:'get',
		dataType:'json',
		success:function (data) {
            // console.log(data.bankcard_list);
            $.each(data.data, function (i, item) {
                outTypeHtml += "<option>"+item.name+"</option>"
            });
            // console.log(html);
            if(outTypeHtml==''){outTypeHtml="<option></option>"}
            $('#transfer_out_type').html(outTypeHtml)
        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	});

    // 查询所有的转账类型
    var allTypeHtml = "";
    $.ajax({
        url: '/transferalltype',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            allTypeHtml += "<option>"+ "所有" +"</option>";
            $.each(data.data, function (i, item) {
                allTypeHtml += "<option>"+item.name+"</option>"
            });
            $('#search_in_type').html(allTypeHtml)
        },
        error: function () {
            console.log('服务器错误，请重试！')
        }
    });

    //年月日单个
    $('.J-datepicker-day').datePicker({
        hasShortcut: true,
        format:'YYYY-MM-DD',
        shortcutOptions: [{
            name: '今天',
            day: '0'
        }, {
            name: '昨天',
            day: '-1'
        }, {
            name: '一周前',
            day: '-7'
        }]
    });
});


