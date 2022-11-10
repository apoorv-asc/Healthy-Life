const express = require('express');
const app = express();
const router = express.Router();

const { google } = require('googleapis');
const request = require('request');
const cors = require('cors');
const urlParse = require('url-parse');
const queryParse = require('query-string');
const bodyParser = require('body-parser');
const axios = require('axios');

const NodeCache = require('node-cache')
const myCache = new NodeCache()

// Body Parser helps to transfer data in forms from one route to other
app.use(express.urlencoded({ extended: true }))
app.use(express.json());  

// +++++++++++++++++++++++ Middlewares +++++++++++++++++++++++
const isLoggedIn = require('../middleware/auth');

// +++++++++++++++++++++++++ Models ++++++++++++++++++++++++++++
const UserData = require('../models/userdata');
const Chat = require('../models/chat');

// ============================== Routes ==========================================
router.get('/getURLTing',(req,res)=>{
    const oauth2Client = new google.auth.OAuth2(
        "385413997223-482vhtj4oucaaidu10jvgu018cdh88cf.apps.googleusercontent.com", // Client ID
        "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", // Client Secret
        "http://localhost:3001/fitbit/connect"  // link to redirect
    )

    const scopes = [
        "https://www.googleapis.com/auth/fitness.activity.read profile email openid",
        "https://www.googleapis.com/auth/fitness.activity.write profile email openid",
        "https://www.googleapis.com/auth/fitness.location.read",
        "https://www.googleapis.com/auth/fitness.location.write",
        "https://www.googleapis.com/auth/fitness.body.read profile email openid",
        "https://www.googleapis.com/auth/fitness.body.write profile email openid",
        "https://www.googleapis.com/auth/fitness.blood_glucose.read"
    ]

    const url = oauth2Client.generateAuthUrl({
        access_type: "offline",
        scope: scopes,
        state: JSON.stringify({
            callbackUrl : req.body.callbackUrl,
            userID: req.body.userid
        })
    })

    request(url,(err,response,body)=>{
        res.send({url});
    })
})



router.get('/connect',isLoggedIn,async (req,res)=>{
    const queryURL = new urlParse(req.url);
    const code = queryParse.parse(queryURL.query).code;
    
    const oauth2Client = new google.auth.OAuth2(
        "385413997223-482vhtj4oucaaidu10jvgu018cdh88cf.apps.googleusercontent.com", // Client ID
        "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", // Client Secret
        "http://localhost:3001/fitbit/connect"  // link to redirect
    )
    const tokens = await oauth2Client.getToken(code);

    await UserData.updateOne(
        {email:res.locals.user.username},
        {$set:{token:tokens.tokens.access_token,token_time:(new Date(tokens.tokens.expiry_date)).getTime()}}
    )

    res.redirect('/user/dashboard');
})

router.get('/fitness_para',isLoggedIn,async (req,res)=>{
    var today = new Date();
    var start_time = new Date(today.getFullYear(),today.getMonth(),today.getDate()-6).getTime();
    var end_time = new Date(today.getFullYear(),today.getMonth(),today.getDate()+1).getTime();


    const person = await UserData.findOne({email:res.locals.user.username});
    if(person.token_time == undefined || person.token_time<(new Date()).getTime()){
        res.redirect("https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.activity.read%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.activity.write%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.location.read%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.location.write%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.body.read%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.body.write%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.blood_glucose.read&state=%7B%7D&response_type=code&client_id=385413997223-482vhtj4oucaaidu10jvgu018cdh88cf.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3001%2Ffitbit%2Fconnect");
    }
        
    let token = person.token;

    let Calories = [];
    let Move_Mins = [];
    let Distance = [];
    let BucketData = [];

    var Dates = "";
    var result = await axios({
        method:"POST",
        headers:{
            authorization: "Bearer "+token
        },
        "Content-Type":"application/json",
        url:`https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate`,
        data:{ 
            aggregateBy:[
                {       
                    dataTypeName: "com.google.calories.expended"
                }
            ],
            bucketByTime :{durationMillis:86400000},
            startTimeMillis: start_time,
            endTimeMillis: end_time
        }
    })
    BucketData = result.data.bucket;
    (BucketData).forEach((bucket)=>{
        if(bucket.dataset[0].point[0] == null){
            Calories.push(0);
        }else{
            Calories.push(Math.round(bucket.dataset[0].point[0].value[0].fpVal));
        }
        var num = Number(bucket.startTimeMillis);
        Dates = Dates.concat((new Date(num)).getDate()+",");
    })

    var result = await axios({
        method:"POST",
        headers:{
            authorization: "Bearer "+token
        },
        "Content-Type":"application/json",
        url:`https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate`,
        data:{ 
            aggregateBy:[
                {       
                    dataTypeName:"com.google.active_minutes"
                }
            ],
            bucketByTime :{durationMillis:86400000},
            startTimeMillis: start_time,
            endTimeMillis: end_time
        }
    })
    BucketData = result.data.bucket;
    (BucketData).forEach((bucket)=>{
        if(bucket.dataset[0].point[0] == null){
            Move_Mins.push(0);
        }else{
            Move_Mins.push(bucket.dataset[0].point[0].value[0].intVal);
        }
    })
    
    var result = await axios({
        method:"POST",
        headers:{
            authorization: "Bearer "+token
        },
        "Content-Type":"application/json",
        url:`https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate`,
        data:{ 
            aggregateBy:[
                {       
                    dataTypeName:"com.google.distance.delta"
                }
            ],
            bucketByTime :{durationMillis:86400000},
            startTimeMillis: start_time,
            endTimeMillis: end_time
        }
    })
    BucketData = result.data.bucket;
    (BucketData).forEach((bucket)=>{
        if(bucket.dataset[0].point[0] == null){
            Distance.push(0);
        }else{
            Distance.push((bucket.dataset[0].point[0].value[0].fpVal/1000).toFixed(2));
        }
    })

    let user = await UserData.findOne({email:res.locals.user.username});

    res.render("fitbit",{Calories,Dates,Move_Mins,Distance,user});
})





module.exports = router;