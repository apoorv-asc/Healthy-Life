// Contains information about various users
const mongoose = require('mongoose');
const UserSchema =new mongoose.Schema({
    name:{
        type:String,
        required: true
    },
    email:{
        type:String,
        required: true
    },
    prof:{
        type:String,
        required: true
    },
    token:{
        type:String
    },
    token_time :{
        type:Number
    },
    chatrooms:[{
        name:{type:String},
        id:{type:String}
    }]
});

module.exports = UserData = mongoose.model('UserData',UserSchema);