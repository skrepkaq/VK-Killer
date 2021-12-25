const sourse_info = JSON.parse(document.getElementById('posts_info').textContent);
const deletePost = document.getElementsByClassName("delete-post")
const box = document.querySelector('#posts-box')
const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const posts_socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/posts/`);
const staticUrl = '/static'

var box_max_scroll
var endOfPosts
var requestedMorePosts
var posts = []


posts_socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if ('posts' in data) {
        console.log(data.posts)
        showNewPosts(data.posts)
        for (let i in data.posts) {
            if (!data.posts[i].is_random_post) {
                posts.push(data.posts[i])
            }
        }
        requestedMorePosts = false;
        if (data.posts.length === 0) endOfPosts = true; //больше постов нет - конец ленты
    } else if ('postIsDeleted' in data) {
        window.location.reload()
    }
}

if (sourse_info.type != 'post') {
    window.addEventListener("load", function(){
        let objDiv = document.getElementById("posts-box");
        objDiv.scrollTop = objDiv.scrollHeight;
    });

    box.addEventListener('scroll', function(e) {
        if (box_max_scroll - 200 < Math.abs(box.scrollTop) && Math.abs(box.scrollTop) > 200 && !requestedMorePosts) {
            /*
            Если до конца преписки меньше 200 пикселей(или не пикселей, хз),
            а так же переписка прокручена вверх больше чем на 200 пикселей -
            запросить более старых сообщений
            */
            sendPostsRequest(sourse_info, posts.length > 0 ? posts[posts.length-1].id : -1)
            requestedMorePosts = true;
        }
    })
}

const sendPostsRequest = (sourse_info, last_post_id=-1) => {
    // запрашивает посты (по умолчанию - 15 последних т.к. last_post_id == -1)
    if (endOfPosts) return false; //если все посты прогружена - больше не запрашивать
    posts_socket.send(JSON.stringify(
        {
            type: 'posts_request',
            sourse_info: sourse_info,
            last_post_id: last_post_id
        }
        ))
    }

posts_socket.onopen = () => {
    sendPostsRequest(sourse_info)
}
    
    
const sendAction = (action, contentType, contentID, e=null) => {
    if (e) {
        let img = e.children[0]
        if (img.classList.contains("pressed")) {
            img.classList.remove("pressed")
        } else {
            img.classList.add("pressed")
        }
    }

    posts_socket.send(JSON.stringify(
            {
                type: 'action',
                action_type: action,
                content_type: contentType,
                content_id: contentID
            }
        ))
}


const showNewPosts = (newPosts) => {
    // выводит новые посты на страницу 
    for (let i = 0; i < newPosts.length; i++) {
        let post = newPosts[i]

        let mdiv = document.createElement('div')

        let divAvatar = document.createElement('div')
        let divImage = document.createElement('div')
        let divButtons = document.createElement('div')
        let divMessage = document.createElement('div')

        let aMessage = document.createElement('a')
        
        mdiv.classList.add("post-container")
        
        divAvatar.classList.add("avatar")
        divImage.classList.add("image")
        divButtons.classList.add("buttons")
        
        divMessage.classList.add("message")
        divMessage.appendChild(aMessage)
        
        
        mdiv.appendChild(divAvatar)
        mdiv.appendChild(divImage)
        mdiv.appendChild(divButtons)
        
        aMessage.textContent = `${post.message} `
        divAvatar.insertAdjacentHTML('afterbegin', `<a href="/profile/${post.user.url}"><img class="avatar small" src="${post.user.avatar}"></a><a class="username-text">${post.user.username}</a>`)
        
        divButtons.insertAdjacentHTML('afterbegin', `<div class="like"><p><a class="nickname-small">Likes</a>${post.likes.length}</p><button name="action" class="action-button" onClick="sendAction('like', 'post', ${post.id}, this)"><img class="like-image like${post.likes.includes(myID) ? ' pressed' : ''}"></button></div>`)
        if (sourse_info.type != 'post') {
            let delete_button = ''
            if (sourse_info.type == 'profile' && myID == post.user.id) {
                delete_button = `<div class="delete-post"><div class="pre-delete"><a class="delete-button"><img class="avatar tiny" src="${staticUrl}/images/cross.png"></a></div><div class="delete hide"><a>Удалить<br>пост?</a><button type="submit" name="action" class="action-button" onClick="sendAction('delete', 'post', ${post.id})"><img class="avatar tiny" src="${staticUrl}/images/cross.png"></button></div></div>`;
            }
            divButtons.insertAdjacentHTML('beforeend', `<div class="comment-button"><a>${post.comments_count}</a><a href="/post/${post.id}" target="_blank"><img class="avatar tiny" src="${staticUrl}/images/comments.png"></a></div>${delete_button}`)
        }
        
        if (post.image) {
            let img = document.createElement('img')
            img.classList.add("post-image")
            img.setAttribute('src', `${post.image}`)
            divImage.appendChild(img)
        }
        
        mdiv.appendChild(divMessage)
        divMessage.insertAdjacentHTML('beforeend', `<a class="timestamp">${post.time}</a>`)

        if (post.comments.length > 0) {
            let divComments = document.createElement('div')
            divComments.classList.add("comments")
            for (let i = 0; i < post.comments.length; i++) {
                let comm = post.comments[i]

                let divComment = document.createElement('div')
                divComment.classList.add("comment")
                let aUsername = document.createElement('a')
                aUsername.setAttribute('href', `/profile/${comm.user.url}`)
                aUsername.classList.add("link-text")
                aUsername.textContent = `${comm.user.username} `
                let aMessage = document.createElement('a')
                aMessage.textContent = `${comm.message} `
                divComment.appendChild(aUsername)
                divComment.appendChild(aMessage)
                
                divComments.appendChild(divComment)
                divComment.insertAdjacentHTML('afterbegin', `<a href="/profile/${comm.user.url}"><img class="avatar tiny" src="${comm.user.avatar}"></a>`)
                divComment.insertAdjacentHTML('beforeend', `<div class="comment-like"><button name="action" class="action-button" onClick="sendAction('like', 'comment', ${comm.id}, this)"><img class="comment-like-image like-image${comm.likes.includes(myID) ? ' pressed' : ''}"></button>${comm.likes.length}</div>`)
            }
            mdiv.appendChild(divComments)
        }

        box.appendChild(mdiv);
        let buttons = mdiv.children[2].children[2]
        if (buttons) {
            let deleteDivs = buttons.children
            deleteDivs[0].addEventListener("click", () => {
                deleteDivs[0].classList.add('hide')
                deleteDivs[1].classList.remove('hide')
            })
        }
    }

    box_max_scroll = box.scrollHeight - box.clientHeight
}
