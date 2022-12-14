const socket = io();
console.log("username");
// Elements
const $messageForm = document.querySelector('#message-form')
const $messageFormInput = $messageForm.querySelector('input')
const $messageFormSelect = $messageForm.querySelector('select')
const $messageFormButton = $messageForm.querySelector('button')
const $messages = document.querySelector('#messages')

// Templates
const messageTemplate1 = document.querySelector('#message-template1').innerHTML
const messageTemplate2 = document.querySelector('#message-template2').innerHTML
const messageTemplate3 = document.querySelector('#message-template3').innerHTML

// Triggered when "Send" button is pushed
$messageForm.addEventListener('submit', (e) => {
    e.preventDefault()

    $messageFormButton.setAttribute('disabled', 'disabled')

    const message = e.target.elements.message.value
    const msg_type = e.target.elements.msg_type.value
    console.log(message,msg_type);

    socket.emit('sendMessage', 
        {
            message:message,
            msg_type: msg_type,
            roomId:roomId,
            username:username,
            time:moment(message.createdAt).format('h:mm a')
        },
        (error) => {
        $messageFormButton.removeAttribute('disabled')
        $messageFormInput.value = ''
        $messageFormInput.focus()

        if (error) {
            return console.log(error)
        }

        console.log('Message delivered!')
    })
})

// Adds the message recieved on the screen
socket.on('Show-Message',(message)=>{
    console.log(message.username);
    console.log(message.msg);

    if(username == message.username){
        const html = Mustache.render(messageTemplate1, {
            username: message.username,
            message: message.msg,
            createdAt: moment(message.createdAt).format('h:mm a')
        })
        $messages.insertAdjacentHTML('beforeend', html)
    }else{
        const html = Mustache.render(messageTemplate2, {
            username: message.username,
            message: message.msg,
            createdAt: moment(message.createdAt).format('h:mm a')
        })
        $messages.insertAdjacentHTML('beforeend', html)
    }

    if(message.msg_type === "prs"){
        console.log("Reached here");
        const html = Mustache.render(messageTemplate3, {
            username: message.username,
            message: message.msg,
            createdAt: moment(message.createdAt).format('h:mm a')
        })
        $messages.insertAdjacentHTML('beforeend', html)
    }
    
    autoscroll()
})

socket.emit('join', { username, roomId }, (error) => {
    if (error) {
        alert(error)
        location.href = '/'
    }
})

// AutScroll Feature
const autoscroll = () => {
    // New message element
    const $newMessage = $messages.lastElementChild

    // Height of the new message
    const newMessageStyles = getComputedStyle($newMessage)
    const newMessageMargin = parseInt(newMessageStyles.marginBottom)
    const newMessageHeight = $newMessage.offsetHeight + newMessageMargin

    // Visible height
    const visibleHeight = $messages.offsetHeight

    // Height of messages container
    const containerHeight = $messages.scrollHeight

    // How far have I scrolled?
    const scrollOffset = $messages.scrollTop + visibleHeight

    if (containerHeight - newMessageHeight <= scrollOffset) {
        $messages.scrollTop = $messages.scrollHeight
    }
}