// Contains information about various users
const mongoose = require('mongoose');
const AI_PredSchema =new mongoose.Schema({
    symptoms:[{
        type:String
    }],
    diseases:[{
        type:String
    }],
    chances:[{
        type:Number
    }],
    temp:{
        type:String
    },
    duration:{
        type:String
    },
    sev:{
        type:String
    }
});

module.exports = ai_pred = mongoose.model('ai_pred',AI_PredSchema);