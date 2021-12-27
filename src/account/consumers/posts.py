import json
from channels.generic.websocket import AsyncWebsocketConsumer
from account.services import posts


class PostsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'posts_request':
            psts = await posts.get(self.user, data['sourse_info'], data['last_post_id'])

            await self.send(text_data=json.dumps({'posts': psts}))

        elif data['type'] == 'action':
            if data['action_type'] == 'like':
                await posts.like(self.user, data['content_type'], data['content_id'])

            elif data['action_type'] == 'delete':
                is_post_deleted = await posts.delete(self.user, data['content_id'])

                if is_post_deleted:
                    await self.send(text_data=json.dumps({'postIsDeleted': True}))
