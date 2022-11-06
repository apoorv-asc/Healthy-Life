// Contains information about various users
const mongoose = require('mongoose');
const UserActivitySchema =new mongoose.Schema({
    email:{
        type:String,
        required: true
    },
    strt:{
        type:Number,
    },
    end:{
        type:Number
    },
    interval :{
        type:Number
    },
    medname:{
        type:Number
    }
});

module.exports = UserActivity = mongoose.model('UserActivity',UserActivitySchema);