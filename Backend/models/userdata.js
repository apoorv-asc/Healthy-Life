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
    }],
    age:{type:Number},
    wt:{type:Number},
    ht:{type:Number},
    diabetes:{type:String},
    hypertension:{type:String},
    current_med:{type:String},
    allergy:{type:String},
    cholestrol:{type:String},
    bp_sys:{type:Number},
    bp_dia:{type:Number},
});

module.exports = UserData = mongoose.model('UserData',UserSchema);