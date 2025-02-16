import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from account.services import messages, online


class MessagesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.profile_id = self.scope['url_route']['kwargs']['profile_id']  # id пользователя, с кем переписка
        self.profile_user = await messages.get_user(self.profile_id)  # пользователь, с кем переписка
        self.dm = await messages.get_or_create_dm(self.user, self.profile_user)  # переписка
        self.dm_group_name = f'dm_{self.dm.id}'  # название ws канала к которому подключится собеседник
        self.notifications_group_name = f'notifications_{self.profile_user.id}'  # название ws канала уведомлений

        # присоединиться к ws каналам
        await self.channel_layer.group_add(
            self.dm_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.notifications_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, _):
        # удалиться из ws каналов
        await self.channel_layer.group_discard(
            self.dm_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.notifications_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'messages_request':
            raw_msgs = await messages.get_messages(self.user, self.dm, data["last_msg_id"])
            if data["last_msg_id"] == -1:
                await self.channel_layer.group_send(
                    self.dm_group_name,
                    {'type': 'send_read_msg', 'data': -1, 'by_user_id': self.user.id}
                )
                # уведомить, что все сообщения прочитаны
            msgs = await self.serialize_messages(raw_msgs, self.user.timezone)
            await self.send(text_data=json.dumps({'messages': msgs}))
        elif data['type'] == 'message':
            content = data['content']
            if not content or all([s == ' ' for s in content]): return  # пустое сообщение
            if len(content) > 5000: return

            raw_msg = await messages.create(self.user, self.dm, content)
            msg = await self.serialize_messages([raw_msg], self.profile_user.timezone)
            my_msg = await self.serialize_messages([raw_msg], self.user.timezone)
            # отправить сообщение всем в ws канале
            await self.channel_layer.group_send(
                self.dm_group_name,
                {'type': 'send_new_message', 'data': msg}
            )
            # отправить уведомление пользователю кому было адресовано сообщение
            await self.channel_layer.group_send(
                self.notifications_group_name,
                {'type': 'send_notification', 'data': {'notification': 'new_message', 'userID': self.user.id}}
            )
            await self.send(text_data=json.dumps({'messages': my_msg}))  # отправить сообщение его автору

    async def send_notification(*_):
        '''Уведомление о новом сообщении от себя самого'''
        pass

    async def send_new_message(self, event):
        msg = event['data']

        if msg[0]["user"]["id"] != self.user.id:
            # отправить сообещние получателю
            await self.send(text_data=json.dumps({'messages': msg}))
            # отметить как прочитанное
            await messages.mark_read(msg[0]["message"]["id"])
            await self.channel_layer.group_send(
                self.dm_group_name,
                {'type': 'send_read_msg', 'data': msg[0]["message"]["id"], 'by_user_id': self.user.id}
            )

    async def send_read_msg(self, event):
        '''Оповещает всех о прочитанном сообщении'''
        msg_id = event['data']
        await self.send(text_data=json.dumps({'readMsg': msg_id, 'byUserID': event['by_user_id']}))

    @sync_to_async
    def serialize_messages(self, messages, tz: int) -> list[dict]:
        '''Сериализует список сообщений'''
        return [{'user': {'id': msg.user.id,
                          'username': msg.user.username,
                          'url': msg.user.url,
                          'lastSeen': msg.user.last_seen,
                          'avatar': msg.user.avatar.url},
                 'message': {'id': msg.id,
                             'time': online.convert_datetime_to_str(msg.timestamp, tz),
                             'content': msg.message,
                             'read': msg.read}} for msg in messages]
