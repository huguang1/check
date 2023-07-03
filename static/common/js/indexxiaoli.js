// 2获取银行卡最新的余额
function get_banlance(bankcard) {
	if(bankcard){
		$.ajax({
			url:'/getbalance',
			type:"post",
			dataType:"json",
			data:{'bankcard': bankcard},
			success:function (data) {
				if(data.status){
					console.log(data.msg)
				}else {
					$('.txt_zc').val(data.balance)
				}
			},
			error:function () {
				console.log('服务器错误，请重试！')
			}
		})
	}else {
		alert('没有查询到相应的银行卡！')
	}

}

// 3获取当前银行卡的对账余额
function get_checkbankcard(bankcard) {
    if(bankcard){
        $.ajax({
            url:'/get_checkbankcard',
            type:'post',
            dataType:'json',
            data:{'bankcard': bankcard},
            success:function (data) {
                if(data.status){
                    console.log('服务器错误，请重试！')
                }else {
                    console.log('这个接口正确')
                }
            },
            error:function () {
                console.log('服务器错误，请重试！')
            }
        })
    }else {
        alert('没有获取到银行卡的信息')
    }
}

// 4获取转出去的银行
function wai_bankcard() {
	var bank_type = $('#wai_bankcard_type').val();
	var html = "";
	if(bank_type){
		$.ajax({
		url:'/waibankcard',
		type:'get',
		dataType:'json',
		data:{'bank_type': bank_type},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				// console.log(data.bankcard_list);
				$.each(data.bankcard_list, function (i, item) {
					html += "<option>"+item+"</option>"
                });
				// console.log(html);
				if(html==''){html="<option></option>"}
				$('#wai_bankcards').html(html)
			}
        },
		error:function () {
			console.log('服务器错误，请重试！')
        }
	})
	}else {
		alert('没有获取到银行卡的种类')
	}

}

// 获取转出的银行
$(function () {
	$('#wai_bankcard_type').click(function () {
		wai_bankcard()
    })
});

// 外转出记录
$(function () {
	$('#waizhuanchu').click(function () {
		var list1 = get_showbankcard_name();
		var bankcard = list1[0];
		var now_time = list1[1];
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            var wai_bankcard = $('#wai_bankcards').val();
            var chu_amount = $('#chu_amount').val();
            var wai_bankcard_type = $('#wai_bankcard_type').val();
            var chu_fees = $('#chu_fees').val();
            if (wai_bankcard && wai_bankcard_type && bankcard && now_time) {
                if (chu_amount < 0) {
                    console.log('转出金额是负数')
                } else {
                    $.ajax({
                        url: '/transferout',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            'wai_bankcard': wai_bankcard,
                            'chu_amount': chu_amount,
                            'wai_bankcard_type': wai_bankcard_type,
							'bankcard': bankcard,
							'chu_fees': chu_fees,
							'now_time': now_time
                        },
                        success: function (data) {
                            if (data.status) {
                                console.log(data.msg)
                            } else {
                                console.log(data.msg);
								bankrecord(1, bankcard);
								check_now_bankcard();
                        		check_all_bankcard();
                        		get_banlance(bankcard);
                            }
                        },
                        error: function () {
                            console.log('服务器错误，请重试')
                        }
                    })
                }
            } else {
                alert('请输入完整数据')
            }
        }
    })
});

// 5获取时间
function get_time() {
	var html = '';
	$.ajax({
		url:"/indexinfo",
		type:"get",
		dataType:"json",
		async: false,
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
					var bankcard = get_onlybankcard_name();
                    if(bankcard==''){
                        console.log('没有获取到银行的信息')
                    }else {
                        bankrecord(1, bankcard);
                        get_banlance(bankcard);
                        check_now_bankcard();
                        check_all_bankcard();
                    }
				}
            },
			error:function () {
				console.log('服务器错误，请重试')
            }
		})
    });

	// 时间减少
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
					var bankcard = get_onlybankcard_name();
                    if(bankcard==''){
                        console.log('没有获取到银行的信息')
                    }else {
                        bankrecord(1, bankcard);
                        get_banlance(bankcard);
                        check_now_bankcard();
                        check_all_bankcard();
                    }
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
// get_bankcard_list();

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
// get_bankcard_list_out();

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


// 7查询银行卡全部记录
var pagesize = 50;
function bankrecord(page, bankcard, start_date, end_date, shuaixuan) {
	$.ajax({
		url:'/bankrecord?p='+page+'&size='+pagesize,
		type:'get',
		dataType:'json',
		data:{'bankcard': bankcard, 'shuaixuan':shuaixuan, 'start_date':start_date,'end_date':end_date},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				if(data.count != 0){
					var html = '';
					html += '<tr><th>ID</th><th>入款</th><th>转出</th><th>手续费</th><th>余额</th><th>备注</th><th>操作</th><th>锁定</th></tr>';
					$.each(data.record_list, function (i, item) {
						html += '<tr><td>' + item.id + '</td>';
						if(item.type){
							//　出款
							html += '<td style="color: red;">0</td><td style="color: red;">' + item.amount + '</td>';
							html += '<td style="color: red;">' + item.fees + '</td><td style="color: red;">' + item.balance + '</td><td style="color: red;">' + item.remark +
							'</td><td><input type="button" value="删除" class="btn_delete" onclick="deleteRow(this)" style="color: red;"></td><td><input type="text" class="input_nborder" id="changesort" value="'+ item.sort +'"></td></tr>'
						}else {
							// 入款
							html += '<td>' + item.amount + '</td><td>0</td>';
							html += '<td>' + item.fees + '</td><td>' + item.balance + '</td><td>' + item.remark +
							'</td><td><input type="button" value="删除" class="btn_delete" onclick="deleteRow(this)"></td><td><input type="text" class="input_nborder" id="changesort" value="'+ item.sort +'"></td></tr>'
						}
					});
					var sPage = Paging(page,pagesize,data.count,2,'bankrecord', 'cur','','上一页','下一页', '首页', '尾页');
					sPage += "<span>总共" + data.num_pages +"页<span>" + "<a class='btn_out' id='daochu'>导出</a>";
					sPage += "<input type='button' value='跳转' id='tiaozhuan' class='btn_jump' onclick='tiaozhuan(" + data.num_pages+ ")'/>";
					sPage +="<input type='text' name='lname' id='text_data' class='jump_select_val' placeholder='页数'/>";
					$(".pager").html(sPage);
					$('.table-exit').html(html);
				}else {
					$(".table-exit").html("<tr><td colspan='3'>未找到相关信息</td></tr>");
				}
			}
		},
		error:function () {
			console.log('服务器超时，请重试！')
		}
	})
}

function Paging(pageNum,pageSize,totalCount,skipCount,fuctionName,currentStyleName,currentUseLink,preText,nextText,firstText,lastText){
	var bankcard = get_onlybankcard_name();
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
			console.log(bankcard);
            var returnValue = "";
            var begin = 1;
            var end = 1;
            var totalpage = Math.floor(totalCount / pageSize);
            if (totalCount % pageSize > 0) {
                totalpage++;
            }
            if (preText == null) {
                firstText = "prev";
            }
            if (nextText == null) {
                nextText = "next";
            }
            begin = pageNum - skipCount;
            end = pageNum + skipCount;
            if (begin <= 0) {
                end = end - begin + 1;
                begin = 1;
            }
            if (end > totalpage) {
                end = totalpage;
            }
            for (count = begin; count <= end; count++) {
                if (currentUseLink) {
                    if (count == pageNum) {
                        returnValue += "<li><a class=\"" + currentStyleName + "\" href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'"+bankcard+"');\">" + count.toString() + "</a></li>";
                    }
                    else {
                        returnValue += "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'" + bankcard + "');\">" + count.toString() + "</a></li>";
                    }
                }
                else {
                    if (count == pageNum) {
                        returnValue += "<li><span class=\"" + currentStyleName + "\">" + count.toString() + "</span></li>";
                    }
                    else {
                        returnValue += "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'" + bankcard + "');\">" + count.toString() + "</a></li>";
                    }
                }
            }
            if (pageNum - skipCount > 1) {
                returnValue = " ... " + returnValue;
            }
            if (pageNum + skipCount < totalpage) {
                returnValue = returnValue + " ... ";
            }
            if (pageNum > 1) {
                returnValue = "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum - 1).toString() + ",'" + bankcard + "');\"> " + preText + "</a></li>" + returnValue;
            }
            if (pageNum < totalpage) {
                returnValue = returnValue + " <li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum + 1).toString() + ",'" + bankcard + "');\">" + nextText + "</a></li>";
            }
            if (firstText != null) {
                if (pageNum > 1) {
                    returnValue = "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(1" + ",'" + bankcard + "');\">" + firstText + "</a></li>" + returnValue;
                }
            }

            if (lastText != null) {
                if (pageNum < totalpage) {
                    returnValue = returnValue + " " + " <li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + totalpage.toString() + ",'" + bankcard + "');\">" + lastText + "</a></li>";
                }
            }


            return returnValue;
        }
}

// 跳转的函数
function tiaozhuan(num_pages){
	var text_page = $("#text_data").val();
	var reg=/^[1-9]\d*$/; //由 1-9开头 的正则表达式
	if (text_page == ''){
		alert("请输入页码");
		return false
	}

	if(reg.test(text_page)){
		if(Number(text_page)>num_pages){
			alert("页码超出范围");
			return false
		}else {
			bankrecord(Number(text_page));
		}
		}else {
			alert("请输入正确的页码");
			return false
	}
}


// 8按条件查询银行记录
var searchpagesize = 50;
function searchbankrecord(page, bankcard, start_date, end_date, shuaixuan, yinhang, intype) {
	$.ajax({
		url:'/searchbankrecord?p='+page+'&size='+searchpagesize,
		type:'get',
		dataType:'json',
		data:{'bankcard': bankcard, 'shuaixuan':shuaixuan, 'start_date':start_date,'end_date':end_date, 'yinhang': yinhang, 'intype': intype},
		success:function (data) {
			if(data.status){
				console.log('服务器错误，请重试！')
			}else {
				if(data.count != 0){
					var html = '';
					html += '<tr><th>ID</th><th>入款</th><th>转出</th><th>手续费</th><th>余额</th><th>备注</th><th>操作</th></tr>';
					$.each(data.record_list, function (i, item) {
						html += '<tr><td>' + item.id + '</td>';
						if(item.type){
							//　出款
							html += '<td style="color: red;">0</td><td style="color: red;">' + item.amount + '</td>';
							html += '<td style="color: red;">' + item.fees + '</td><td style="color: red;">' + item.balance + '</td><td style="color: red;">' + item.remark +
							'</td><td><input type="button" value="删除" class="btn_delete" onclick="deleteRow(this)" style="color: red;"></td></tr>'
						}else {
							// 入款
							html += '<td>' + item.amount + '</td><td>0</td>';
							html += '<td>' + item.fees + '</td><td>' + item.balance + '</td><td>' + item.remark +
							'</td><td><input type="button" value="删除" class="btn_delete" onclick="deleteRow(this)"></td></tr>'
						}
					});
					var sPage = searchPaging(page,searchpagesize,data.count,2,'searchbankrecord', 'cur','','上一页','下一页', '首页', '尾页');
					sPage += "<span>总共" + data.num_pages +"页<span>" + "<a class='btn_out' id='daochu'>导出</a>";
					sPage += "<input type='button' value='跳转' id='tiaozhuan' class='btn_jump' onclick='tiaozhuan(" + data.num_pages+ ")'/>";
					sPage +="<input type='text' name='lname' id='text_data' class='jump_select_val' placeholder='页数'/>";
					$(".pager").html(sPage);
					$('.table-exit').html(html);
				}else {
					$(".table-exit").html("<tr><td colspan='3'>未找到相关信息</td></tr>");
				}
			}
		},
		error:function () {
			console.log('服务器超时，请重试！')
		}
	})
}

function searchPaging(pageNum,pageSize,totalCount,skipCount,fuctionName,currentStyleName,currentUseLink,preText,nextText,firstText,lastText){
	var bankcard = get_onlybankcard_name();
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
			console.log(bankcard);
            var returnValue = "";
            var begin = 1;
            var end = 1;
            var start_date = $('#start_date').val();
            var end_date = $('#end_date').val();
            var shuaixuan = $('#shaixuan').val();
            var yinhang = $('#allbankcards').val();
            var intype = $('#search_in_type').val();
            var totalpage = Math.floor(totalCount / pageSize);
            if (totalCount % pageSize > 0) {
                totalpage++;
            }
            if (preText == null) {
                firstText = "prev";
            }
            if (nextText == null) {
                nextText = "next";
            }
            begin = pageNum - skipCount;
            end = pageNum + skipCount;
            if (begin <= 0) {
                end = end - begin + 1;
                begin = 1;
            }
            if (end > totalpage) {
                end = totalpage;
            }
            for (count = begin; count <= end; count++) {
                if (currentUseLink) {
                    if (count == pageNum) {
                        returnValue += "<li><a class=\"" + currentStyleName + "\" href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'"+bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype+"');\">" + count.toString() + "</a></li>";
                    }
                    else {
                        returnValue += "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype +"');\">" + count.toString() + "</a></li>";
                    }
                }
                else {
                    if (count == pageNum) {
                        returnValue += "<li><span class=\"" + currentStyleName + "\">" + count.toString() + "</span></li>";
                    }
                    else {
                        returnValue += "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype + "');\">" + count.toString() + "</a></li>";
                    }
                }
            }
            if (pageNum - skipCount > 1) {
                returnValue = " ... " + returnValue;
            }
            if (pageNum + skipCount < totalpage) {
                returnValue = returnValue + " ... ";
            }
            if (pageNum > 1) {
                returnValue = "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum - 1).toString() + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype + "');\"> " + preText + "</a></li>" + returnValue;
            }
            if (pageNum < totalpage) {
                returnValue = returnValue + " <li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + (pageNum + 1).toString() + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype + "');\">" + nextText + "</a></li>";
            }
            if (firstText != null) {
                if (pageNum > 1) {
                    returnValue = "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(1" + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype + "');\">" + firstText + "</a></li>" + returnValue;
                }
            }

            if (lastText != null) {
                if (pageNum < totalpage) {
                    returnValue = returnValue + " " + " <li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + totalpage.toString() + ",'" + bankcard + "','" + start_date + "','" + end_date + "','" + shuaixuan + "','" + yinhang + "','" + intype + "');\">" + lastText + "</a></li>";
                }
            }


            return returnValue;
        }
}

// 按条件筛选银行卡记录
$('.btn-search').click(function () {
	var yinhang = $('#allbankcards').val();
	var intype = $('#search_in_type').val();
	var page = 1;
	var shaixuan = $('#shaixuan').val();
	var start_date = $('#start_date').val();
	var end_date = $('#end_date').val();
	var bankcard = get_onlybankcard_name();
	if(bankcard==''){
		console.log('没有获取到银行的信息')
	}else {
		if (start_date && end_date) {
			searchbankrecord(page, bankcard, start_date, end_date, shaixuan, yinhang, intype);
		} else if(shaixuan){
			searchbankrecord(page, bankcard, start_date, end_date, shaixuan, yinhang, intype);
		}else {
			alert('请将日期输入完整！')
		}
	}
});

// 添加银行卡记录
$(function () {
	$('.btn-add').click(function () {
		var list1 = get_showbankcard_name();
		var bankcard = list1[0];
		var now_time = list1[1];
		console.log(now_time);
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            var amount = $('#jine').val();
            var fees = $('#shouxufei').val();
            var remark = $('#beizhu').val();
            if (amount && bankcard && now_time) {
                $.ajax({
                    url: '/addbankrecord',
                    type: 'post',
                    dataType: 'json',
                    data: {'amount': amount, 'fees': fees, 'remark': remark, 'type': 'in', 'bankcard': bankcard, 'now_time': now_time},
                    success: function (data) {
                        if (data.status) {
                            console.log(data.msg)
                        } else {
                            console.log(data.msg);
							bankrecord(1, bankcard);
							check_now_bankcard();
                        	check_all_bankcard();
                        	get_banlance(bankcard);
                        }
                    },
                    error: function () {
                        console.log('服务器超时，请重试！')
                    }
                })
            } else {
                alert('请输入完整的参数！')
            }
        }
        $('#jine').val('');
		$('#shouxufei').val('');
		$('#beizhu').val('');
    })
});

// 添加外转入记录
$(function () {
	// 添加外转入记录
	$('#waizhuanru').click(function () {
		var list1 = get_showbankcard_name();
		var bankcard = list1[0];
		var now_time = list1[1];
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            var transfer_type = $('#transfer_in_type').val();
            var transfer_amount = $('#transfer_in_amount').val();
            var transfer_remark = $('#transfer_in_remark').val();
            if (transfer_type && transfer_amount && bankcard && now_time) {
                $.ajax({
                    url: '/transferin',
                    type: 'post',
                    dataType: 'json',
                    data: {'transfer_type': transfer_type, 'transfer_amount': transfer_amount, 'bankcard': bankcard, 'now_time': now_time, 'transfer_remark': transfer_remark},
                    success: function (data) {
                        if (data.status) {
                            console.log('服务器错误，请重试！')
                        } else {
                            console.log(data.msg);
                            bankrecord(1, bankcard);
                            check_now_bankcard();
                        	check_all_bankcard();
                        	get_banlance(bankcard);
                        }
                    },
                    error: function () {
                        console.log('服务器错误，请重试！')
                    }
                })
            } else {
                alert('请输入完整参数！')
            }
        }
    })
});

// 添加外转出记录
$(function () {
	// 添加外转出记录
	$('#waizhuanchumoney').click(function () {
		var list1 = get_showbankcard_name();
		var bankcard = list1[0];
		var now_time = list1[1];
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            var transfer_type = $('#transfer_out_type').val();
            var transfer_amount = $('#transfer_out_amount').val();
            var waizhuanchu_fees = $('#waizhuanchu_fees').val();
            var transfer_remark = $('#transfer_out_remark').val();
            if (transfer_type && transfer_amount && bankcard && now_time) {
                $.ajax({
                    url: '/transferoutmoney',
                    type: 'post',
                    dataType: 'json',
                    data: {'transfer_type': transfer_type, 'transfer_amount': transfer_amount, 'bankcard': bankcard, 'now_time': now_time, 'waizhuanchu_fees': waizhuanchu_fees, 'transfer_remark': transfer_remark},
                    success: function (data) {
                        if (data.status) {
                            console.log('服务器错误，请重试！')
                        } else {
                            console.log(data.msg);
                            bankrecord(1, bankcard);
                            check_now_bankcard();
                        	check_all_bankcard();
                        	get_banlance(bankcard);
                        }
                    },
                    error: function () {
                        console.log('服务器错误，请重试！')
                    }
                })
            } else {
                alert('请输入完整参数！')
            }
        }
    })
});

// 删除操作
function deleteRow(obj) {
    var mytd = obj.parentNode.parentNode.childNodes;
    var mycars = new Array();
    $.each(mytd,function(i,n){
        mycars[i] = n.innerHTML;
    });
    if(mycars[0]){
    	var bankcard = get_onlybankcard_name();
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            $.ajax({
                url: '/deleterecord',
                type: 'post',
                dataType: 'json',
                data: {'id': mycars[0]},
                success: function (data) {
                    if (data.status) {
                        console.log('服务器错误，请重试！')
                    } else {
                        console.log('删除数据成功');
                        bankrecord(1, bankcard);
                        check_now_bankcard();
                        check_all_bankcard();
                        get_banlance(bankcard);
                    }
                },
                error: function () {
                    console.log('服务器错误，请重试！')
                }
            })
        }
    }else {
        alert('未获取到相应的删除信息，请重试！')
    }
}


// 8统计当前银行卡的对账额度
function check_now_bankcard() {
	var bankcard = get_onlybankcard_name();
	if(bankcard==''){
		console.log('没有获取到银行的信息')
	}else {
		$.ajax({
			url: '/checknowbankcard',
			type: 'get',
			dataType: 'json',
			data: {'bankcard': bankcard},
			success: function (data) {
				if(data.status){
					console.log(data.msg)
				}else {
					$('#past_balance_bankcard').html(data.msg.past_balance);
					$('#in_amount_bankcard').html(data.msg.in_amount);
					$('#fees_bankcard').html(data.msg.fees);
					$('#total_in_amount_bankcard').html(data.msg.total_in_amount);
					$('#now_balance_bankcard').html(data.msg.now_balance);
					console.log(data.msg)
				}
			},
			error: function () {
				console.log('服务器错误，请重试！')
			}
		})
	}
}


// 9获取总的银行卡的对账额度
function check_all_bankcard() {
	$.ajax({
		url: '/checkallbankcard',
		type: 'get',
		dataType: 'json',
		data: {},
		success: function (data) {
			if(data.status){
				console.log(data.msg)
			}else {
				$('#all_past_balance_bankcard').html(data.msg.past_balance); //昨天总余额  入款
				$('#all_in_amount_bankcard').html(data.msg.in_amount);
				$('#all_fees_bankcard').html(data.msg.fees);
				$('#all_total_in_amount_bankcard').html(data.msg.total_in_amount);
				$('#all_now_balance_bankcard').html(data.msg.now_balance);
				$('#zhong_past_balance_bankcard').html(data.msg.zhong_past_balance);// 昨天总余额 中转
				$('#zhong_in_amount_bankcard').html(data.msg.zhong_in_amount);
				$('#zhong_fees_bankcard').html(data.msg.zhong_fees);
				$('#zhong_total_in_amount_bankcard').html(data.msg.zhong_total_in_amount);
				$('#zhong_now_balance_bankcard').html(data.msg.zhong_now_balance);
				console.log(data.msg)
			}
        },
		error: function () {
			console.log('服务器错误，请重试！')
        }
	})
}


// 移除银行卡中的金额
$(function () {
	$('#waiyichu').click(function () {
		var list1 = get_showbankcard_name();
		var bankcard = list1[0];
		var now_time = list1[1];
		if(bankcard==''){
			console.log('没有获取到银行的信息')
		}else {
            var chu_amount = $('#yichu_amount').val();
            var chu_remark = $('#yichu_remark').val();
            if (chu_amount && bankcard) {
				$.ajax({
					url: '/removeamount',
					type: 'post',
					dataType: 'json',
					data: {
						'chu_amount': chu_amount,
						'bankcard': bankcard,
						'now_time': now_time,
						'chu_remark': chu_remark
					},
					success: function (data) {
						if (data.status) {
							console.log(data.msg)
						} else {
							console.log(data.msg);
							bankrecord(1, bankcard);
							check_now_bankcard();
							check_all_bankcard();
							get_banlance(bankcard);
						}
					},
					error: function () {
						console.log('服务器错误，请重试')
					}
				})

            } else {
                alert('请输入完整数据')
            }
        }
    })
});


// 导出银行卡的记录
$('.pager').on('click', '#daochu', function () {
	var yinhang = $('#allbankcards').val();
	var intype = $('#search_in_type').val();
	var shaixuan = $('#shaixuan').val();
	var start_date = $('#start_date').val();
	var end_date = $('#end_date').val();
	var bankcard = get_onlybankcard_name();
	if(bankcard==''){
		console.log('没有获取到银行的信息')
	}else {
		url = '/searchbankrecorddaochu?yinhang='+yinhang +'&intype='+intype+'&shaixuan='+shaixuan+'&start_date='+start_date+'&end_date='+end_date+'&bankcard='+bankcard;
		window.location.href = url
	}
});


// 修改记录的排序
$(function () {
	$(document).on('blur', '#changesort', function () {
		var sort = $(this).val();
		var id = $(this).closest('tr').children('td:first').text();
		if(id && sort){
			$.ajax({
				url: '/changesort',
				type: 'post',
				dataType: 'json',
				data: {
					'id': id,
					'sort': sort
				},
				success:function (data) {
					if(data.status){
						console.log(data.msg)
					}else {
						console.log(data.msg);
						var list1 = get_showbankcard_name();
						var bankcard = list1[0];
						if(bankcard==''){
							console.log('没有获取到银行的信息')
						}else {
							bankrecord(1, bankcard);
						}
					}
                },
				error: function () {
					console.log('服务器错误，请重试！')
                }
			})
		}else {
			console.log('没有获取到id和sort的信息！')
		}
    })
});