/**
 * Created by python on 19-3-4.
 */
var roomName = '123';
// 前端发送websocket请求，会建立一个chatsocket的对象。
var chatSocket = new WebSocket(
    'ws://' + window.location.host +
    '/ws/chat/' + roomName + '/');

chatSocket.onmessage = function(e) {// 长链接接受后台传递过来的信息
    var data = JSON.parse(e.data);
    var message = data['message'];
    console.log(message);
    console.log(message.outbankcard);
    console.log(message.inbankcard);
    $('#pop').show();
    // $('#popTitle').text();
    $('#yinhangka').text(message.outbankcard);
    var html = '转给：' + message.inbankcard + '，转账金额：' + message.amount + '，转账的手续费：' + message.fees + '，剩余余额：' + message.balance;
    $('#neirong').text(html);
    $('<audio id="notice" controls="controls"><source src="common/images/notice.mp3" type="audio/mpeg">您的浏览器不支持 audio 元素。</audio>').appendTo('body');
    $('#notice')[0].play();
    setTimeout(function(){
        $('#pop').fadeOut();
    },10000);
};

chatSocket.onclose = function(e) {// 长链接断开的时候执行
    console.error('Chat socket closed unexpectedly');
};
$(function(){
    $('#popClose').click(function(){
      $('#pop').fadeOut();
    });
});