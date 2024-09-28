from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from .models import Chat, Group

class MyWebsocketConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['msg']
        
        group = Group.objects.get(name=self.group_name)
        chat = Chat(
            content = data['msg'],
            group = group
        )
        chat.save()
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,{
                'type':'chat.message',
                'message':message
            }
        )
    def chat_message(self,event):
            self.send(text_data=json.dumps({
                'msg':event['message']
            }))
    
    def disconnect(self, code):
         async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )