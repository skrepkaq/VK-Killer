messageSnd = new Audio(`${window.location.origin}/static/sounds/message.ogg`)
messageSnd.volume = 0.15
const myID = JSON.parse(document.getElementById('myID').textContent);
const navbarMessages = document.querySelector('#navbar-messages')
const notificationsSocket = new WebSocket(`${window.location.protocol == "https:" ? "wss" : "ws"}://${window.location.host}/ws/notifications/`);
var isUnreadMessages


notificationsSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if ('notification' in data) {
        if (data.notification = 'new_message') {
            messageSnd.play()
            if (window.location.pathname.endsWith(data.userID)) return
            // если пришло уведомление о сообщении, но вы сейчас в той самой переписке
            isUnreadMessages = true
            localStorage.setItem(`skrepka.social.isUnreadMessages.${myID}`, true);
            updateNavbar()
        }
    } else if ('isUnreadMessages' in data) {
        isUnreadMessages = data.isUnreadMessages
        localStorage.setItem(`skrepka.social.isUnreadMessages.${myID}`, isUnreadMessages);
        updateNavbar()
    } else if ('onlineCheck' in data) {
        sendOnlineState(true);
    }
}


const updateNavbar = () => {
    navbarMessages.innerHTML = `Сообщения${isUnreadMessages ? ' ●' : ''}`
}


const sendOnlineState = (state) => {
    notificationsSocket.send(JSON.stringify(
        {
            type: 'online_state',
            state: state,
            timezone: new Date().getTimezoneOffset()
        }
        ))
    }

notificationsSocket.onopen = () => {
    notificationsSocket.send(JSON.stringify({type: 'path', path: window.location.pathname}))
    sendOnlineState(true);
}


isUnreadMessages = localStorage.getItem(`skrepka.social.isUnreadMessages.${myID}`) == 'true' ? true : false;
updateNavbar()