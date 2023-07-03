
        //分页
    function Paging(pageNum,pageSize,totalCount,skipCount,fuctionName,currentStyleName,currentUseLink,preText,nextText,firstText,lastText){
		var firstpage = "<a href='javascript:;' onclick="+fuctionName+"(1)>首页</a>";
		var returnValue = "";
	    var begin = 1;
	    var end = 1;
	    var totalpage = Math.floor(totalCount / pageSize);//总条数除每页条数

	    if(totalCount % pageSize >0){
	        totalpage ++;
	    }
	    if(preText == null){
	        firstText = "prev";
	    }
	    if(nextText == null){
	        nextText = "next";
	    }
	    begin = pageNum - skipCount;
	    end = pageNum + skipCount;

	    if(begin <= 0){
	        end = end - begin +1;
	        begin = 1;
	    }
	    if(end > totalpage){
	        end = totalpage;
	    }
	    for(count = begin;count <= end;count ++){
	        if(currentUseLink){
	            if(count == pageNum){
	                returnValue += "<li><a class=\""+currentStyleName+"\" href=\"javascript:void(0);\" onclick=\""+fuctionName+"("+count.toString()+");\">"+count.toString()+"</a></li> ";
	            }
	            else{
	                returnValue += "<li><a href=\"javascript:void(0);\" onclick=\"" + fuctionName + "(" + count.toString() + ");\">" + count.toString() + "</a></li> ";
	            }
	        }
	        else {
	            if (count == pageNum) {
	                returnValue += "<li><span class=\""+currentStyleName+"\">"+count.toString()+"</span></li> ";
	            }
	            else{
	                returnValue += "<li><a href=\"javascript:void(0);\" onclick=\""+fuctionName+"("+count.toString()+");\">"+count.toString()+"</a></li> ";}
	            }
	        }
	        if(pageNum - skipCount >1){
	            returnValue = " ... "+returnValue;
	        }
	        if(pageNum + skipCount < totalpage){
	            returnValue = returnValue + " ... ";
	        }
	        if(pageNum > 1){
	            returnValue = "<li><a href=\"javascript:void(0);\" onclick=\""+fuctionName+"("+(pageNum - 1).toString()+");\"> " + preText + "</a></li> " + returnValue;
	        }
	        if(pageNum < totalpage){
	            returnValue = returnValue + " <li><a href=\"javascript:void(0);\" onclick=\""+fuctionName+"("+(pageNum+1).toString()+");\">" + nextText + "</a></li>";
	        }
	        if(firstText!= null){
	            if(pageNum >1){
	                returnValue = "<li><a href=\"javascript:void(0);\" onclick=\""+fuctionName+"(1);\">" + firstText + "</a></li> " + returnValue;}
	        }
	        if(lastText !=null){
	            if(pageNum < totalpage){
	                returnValue = returnValue + " " + " <li><a href=\"javascript:void(0);\" onclick=\""+fuctionName+"("+totalpage.toString()+");\">" + lastText + "</a></li>";}
	        }
	        returnValue += "<li><a href='javascript:;' onclick=" + fuctionName+ "("+ totalpage +")>尾页</a></li>";

            return firstpage + returnValue;
	}


    //跳转页面
    function tiaozhuan(num_pages, func){
			var text_page = $("#text_data").val();
			var reg=/^[1-9]\d*$/;                         //由 1-9开头 的正则表达式
			if (text_page == ''){
				alert("请输入页码");
				return false
				}
			if(reg.test(text_page)){
				if(Number(text_page)>num_pages){
					alert("页码超出范围");
					return false
				}else {
					func(Number(text_page));
				}
			}else {
				alert("请输入正确的页码");
				return false
			}
        }