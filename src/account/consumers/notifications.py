import json
from channels.generic.websocket import AsyncWebsocketConsumer
from account.services import online, dms


class NotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.notifications_group_name = f'notifications_{self.user.id}'  # название ws канала уведомлений

        # присоединиться к ws каналу
        await self.channel_layer.group_add(
            self.notifications_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, _):
        # удалиться из ws канала
        await self.channel_layer.group_discard(
            self.notifications_group_name,
            self.channel_name
        )
        await online.disconnect(self.user)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'online_state':
            if data['state']:  # user подключился или отключился
                is_new_session = await online.connect(self.user)
                if is_new_session:
                    await self.send_is_unread_messages()
            else:
                await online.disconnect(self.user)
        elif data['type'] == 'path':
            if data['path'].startswith('/dm/'):
                # если пользователь в переписках - проверить прочитал ли он сообщения
                await self.send_is_unread_messages()

    async def send_notification(self, event):
        # принять уведомление о сообщении, отправить через сокет
        notification_type = event['data']
        await self.send(text_data=json.dumps({'notification': notification_type}))

    async def send_is_unread_messages(self):
        '''Проверяет если ли непрочитанные сообщения и отправляет данные через сокет'''
        is_unread_messages = await dms.is_unread_messages(self.user)
        await self.send(text_data=json.dumps({'isUnreadMessages': is_unread_messages}))
