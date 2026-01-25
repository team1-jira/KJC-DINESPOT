import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"canteen_{self.scope['url_route']['kwargs']['canteen_id']}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "order_notification",
                "message": data["message"],
            },
        )

    async def order_notification(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
