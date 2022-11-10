// Contains all the chats done on various pages
const mongoose = require('mongoose');
const ChatScehma =new mongoose.Schema({
    ChatID:{
        type:String
    },
    ChatName:{
        type:String
    },
    Participants:[{type:String}],
    ChatOwner:{type:String},
    msg:[{
        username:{type:String},
        message:{type:String},
        timestamp:{type:String},
        msg_type:{type:String},
        symptoms:[{type:String}],
        diseases:[{type:String}],
        chances:[{type:Number}],
        temp:{type:String},
        duration:{type:String},
        sev:{type:String}
    }]
});

module.exports = Chat = mongoose.model('Chat',ChatScehma);