const profile_user_id = JSON.parse(document.getElementById('profile_user_id').textContent);
const box = document.querySelector('#messages-box')
const form = document.querySelector("#send-message")
const socket = new WebSocket(`ws://${window.location.host}/ws/messages/${profile_user_id}`);
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
    let table = document.querySelector('#msgs-table')
    table.innerHTML = "" // удалить все старые сообщения

    for (let i = 0; i < messages.length; i++) {
        let msg = messages[i]
        let tr1 = document.createElement('tr')
        let tr2 = document.createElement('tr')
        let thAvatar = document.createElement('th')
        let thUser = document.createElement('th')
        let thMessage = document.createElement('th')
        let img = document.createElement('img')
        let aTime = document.createElement('a')

        thAvatar.setAttribute('rowspan', "2")
        img.classList.add("avatar", "small")
        img.setAttribute('src', `${msg.user.avatar}`)
        aTime.classList.add("timestamp")
        thMessage.classList.add("msg")
        thUser.classList.add("user")
        aTime.textContent = msg.message.time
        thUser.textContent = `${msg.user.username} `
        thMessage.textContent = msg.message.content

        thUser.appendChild(aTime)
        thAvatar.appendChild(img)

        tr1.appendChild(thAvatar)
        tr1.appendChild(thUser)
        tr2.appendChild(thMessage)
        table.appendChild(tr1);
        table.appendChild(tr2);
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
