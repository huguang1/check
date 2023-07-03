# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取到房间的名字
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        # 将小组的名字加入到通道中
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        # 将小组的名字从通道中取出
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    # 接受websocket传递过来的信息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        # 向通道中传递信息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    # 接受通道中传递过来的信息
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        # 将通道中的信息传递给前方
        await self.send(text_data=json.dumps({
            'message': message
        }))
