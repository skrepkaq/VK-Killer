const profile_user_id = JSON.parse(document.getElementById('profile_user_id').textContent);
const box = document.querySelector('#messages-box')
const form = document.querySelector("#send-message")
const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const socket = new WebSocket(`${ws_scheme}://${window.location.host}/ws/messages/${profile_user_id}`);
var loaded, requested_more_messages, end_of_dm;
var box_max_scroll;
var messages = [];


socket.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if ('messages' in data) {
        console.log(data.messages)
        messages = messages.concat(data.messages)
        showMessages()
        requested_more_messages = false;
        if (data.messages.length === 0) end_of_dm = true; //больше сообщений нет - конец переписки
    } else if ('readMsg' in data) {
        for (let i = 0; i < messages.length; i++) {
            if ((messages[i].message.id == data.readMsg || (data.readMsg === -1 && data.byUserID != myID)) && !messages[i].message.read) {
                //если пришло -1 - отметить все сообщения как прочитанные, иначе только с нужным id
                messages[i].message.read = true
            }
        }
        showMessages()
    }
}

socket.onopen = () => {
    send_messages_request()
}

form.onclick = (e) => {
    e.preventDefault();
    msg = document.querySelector('#message');
    socket.send(JSON.stringify(
        {
            type: 'message',
            content: msg.value
        }
    ))
    msg.value = ''
}


send_messages_request = (last_msg_id=-1) => {
    // запрашивает сообщения (по умолчанию - 30 последних т.к. last_msg_id == -1)
    if (end_of_dm) return false; //если вся переписка прогружена - больше сообщений не запрашивать
    socket.send(JSON.stringify(
        {
            type: 'messages_request',
            last_msg_id: last_msg_id
        }
    ))
}


box.addEventListener('scroll', function(e) {
    if (box_max_scroll - box.scrollTop > 200 && box.scrollTop < 200 && !requested_more_messages) {
        /*
        Если до конца преписки меньше 200 пикселей(или не пикселей, хз),
        а так же переписка прокручена вверх больше чем на 200 пикселей -
        запросить более старых сообщений
        */
        send_messages_request(messages[0].message.id)
        requested_more_messages = true;
    }
})


const showMessages = () => {
    // выводит сообщения на страницу
    messages.sort((a, b) => a.message.id - b.message.id) // отсортировать сообщения по id
    let boxdiv = document.querySelector('#messages-box')
    boxdiv.innerHTML = "" // удалить все старые сообщения

    for (let i = 0; i < messages.length; i++) {
        let msg = messages[i]
        let mdiv = document.createElement('div')
        let divAvatar = document.createElement('div')
        let divUser = document.createElement('div')
        let divMessage = document.createElement('div')
        let img = document.createElement('img')
        let aTime = document.createElement('a')
        let aImg = document.createElement('a')
        let aUsername = document.createElement('a')

        mdiv.classList.add("message")
        img.classList.add("avatar", "small")
        img.setAttribute('src', `${msg.user.avatar}`)
        aUsername.setAttribute('href', `/profile/${msg.user.id}`)
        aImg.setAttribute('href', `/profile/${msg.user.id}`)
        aTime.classList.add("timestamp")
        divMessage.classList.add("msg")
        divUser.classList.add("user")
        divAvatar.classList.add("divavatar")
        if (!msg.message.read && msg.user.id === myID) {
            mdiv.classList.add("unread")
        }
        aTime.textContent = msg.message.time
        aUsername.textContent = `${msg.user.username} `
        divMessage.textContent = msg.message.content
        aImg.appendChild(img)

        divUser.appendChild(aUsername)
        divUser.appendChild(aTime)
        divAvatar.appendChild(aImg)

        mdiv.appendChild(divAvatar)
        mdiv.appendChild(divUser)
        mdiv.appendChild(divMessage)

        boxdiv.appendChild(mdiv);
    }

    let old_max_scorll = box_max_scroll
    box_max_scroll = box.scrollHeight - box.clientHeight
    if (requested_more_messages) {
        // пришли более старые сообщения - прокрутить страницу ниже
        box.scrollTop += (box_max_scroll - old_max_scorll);
    }

    if (!loaded || box_max_scroll - box.scrollTop < 200) {
        // если пришло новое сообщение и страница не прокручена вверх - прокрутить в самый низ
        box.scrollTop = box_max_scroll
        loaded = true;
    }
}
