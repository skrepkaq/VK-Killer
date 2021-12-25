import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from account.models import Post
from account.services import posts, online


class PostsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'posts_request':
            tz = self.user.timezone if self.user.is_authenticated else 0
            psts = await posts.get(data['sourse_info'], data['last_post_id'])
            out_posts = await self.serialize_posts(psts, tz,
                                                   data['sourse_info']['type'] != 'post', False)
            if data['sourse_info']['type'] == 'feed':
                # подмешать случайные посты 3 в нормальном случае и до 10 если от друзей закончились
                psts = await posts.get_random_posts(self.user, 10-len(out_posts) if len(out_posts) < 10 else 3)
                out_posts += await self.serialize_posts(psts, tz, True, True)
            await self.send(text_data=json.dumps({'posts': out_posts}))
        elif data['type'] == 'action':
            if data['action_type'] == 'like':
                await posts.like(self.user, data['content_type'], data['content_id'])
            elif data['action_type'] == 'delete':
                is_post_deleted = await posts.delete(self.user, data['content_id'])
                if is_post_deleted:
                    await self.send(text_data=json.dumps({'postIsDeleted': True}))

    @sync_to_async
    def serialize_posts(self, psts: list[Post], tz: int, only_top_comment: bool, is_random_post: bool) -> list[dict]:
        '''Подготавливает посты с комментариями для отправки по ws'''
        out_posts = []
        for p in psts:
            comments = p.comments.all()
            comments_count = len(comments)

            if comments and only_top_comment:
                comments = [max(comments, key=lambda x: len(x.likes.all()))]

            comments = [{'user': {'id': com.user.id,
                                  'username': com.user.username,
                                  'url': com.user.url,
                                  'avatar': com.user.avatar.url},
                         'id': com.id,
                         'message': com.message,
                         'likes': [like.id for like in com.likes.all()]} for com in comments]

            out_posts.append({'user': {'id': p.user.id,
                                       'username': p.user.username,
                                       'url': p.user.url,
                                       'lastSeen': p.user.last_seen,
                                       'avatar': p.user.avatar.url},
                              'id': p.id,
                              'message': p.message,
                              'image': p.image.url if p.image else None,
                              'time': online.convert_datetime_to_str(p.timestamp, tz),
                              'is_random_post': is_random_post,
                              'comments': comments,
                              'comments_count': comments_count,
                              'likes': [like.id for like in p.likes.all()]})
        return out_posts
