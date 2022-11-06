const express = require('express');
const app = express();
const router = express.Router();
const { v4: uuidv4 } = require("uuid");
const axios = require('axios')

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

// @route   GET user/home
// @desc    Users Homepage
// @access  Private
router.get('/home',isLoggedIn,async (req,res)=>{
    let user = await UserData.findOne({email:res.locals.user.username});
    myCache.set('username', user.name);
    res.render('user_home',{"username":myCache.get('username')});
})

router.get('/dashboard',isLoggedIn,async (req,res)=>{
    const person = await UserData.findOne({email:res.locals.user.username});
    if(person.token_time == undefined || person.token_time<(new Date()).getTime())
    res.redirect("https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.activity.read%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.activity.write%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.location.read%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.location.write%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.body.read%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.body.write%20profile%20email%20openid%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Ffitness.blood_glucose.read&state=%7B%7D&response_type=code&client_id=385413997223-482vhtj4oucaaidu10jvgu018cdh88cf.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3001%2Ffitbit%2Fconnect");

    let token = person.token;

    var today = new Date();
    var start_time = new Date(today.getFullYear(),today.getMonth(),today.getDate()-6).getTime();
    var end_time = new Date(today.getFullYear(),today.getMonth(),today.getDate()+1).getTime();

    let BucketData = [];
    let heart_points = [];
    let steps = [];
    let Dates = [];

    for(let x=start_time;x<end_time;x=x+86400000){
        let q = new Date(x);
        Dates.push(q.getDate());

    }

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
                    dataTypeName:"com.google.heart_minutes"
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
            heart_points.push(0);
        }else{
            heart_points.push(bucket.dataset[0].point[0].value[0].fpVal);
        }
    })
    result = await axios({
        method:"POST",
        headers:{
            authorization: "Bearer "+token
        },
        "Content-Type":"application/json",
        url:`https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate`,
        data:{ 
            aggregateBy:[
                {       
                    dataTypeName :"com.google.step_count.delta"
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
            steps.push(0);
        }else{
            steps.push(bucket.dataset[0].point[0].value[0].intVal);
        }
    })

    let heart_score = heart_points.reduce((partialSum, a) => partialSum + a, 0);
    let total_steps = steps.reduce((partialSum, a) => partialSum + a, 0);

    res.render("dashboard",{"username":myCache.get('username'),heart_points,heart_score,steps,total_steps,Dates,person});
})

// @route   GET user/create_room
// @desc    Renders form to create a new chat room
// @access  Private
router.get('/create_room',isLoggedIn,async (req,res)=>{
    var isLoggedInUser = await UserData.findOne({email:res.locals.user.username});

    var ge = await UserData.find({prof:"General Physician"});
    var cardio = await UserData.find({prof:"Cardiologist"});
    var derma = await UserData.find({prof:"Dermatologists"});
    var ortho = await UserData.find({prof:"Orthopedic"});

    res.render('create_chatroom',
        {
            isLoggedInUser:isLoggedInUser,
            ge:ge,
            cardio:cardio,
            derma:derma,
            ortho:ortho,
            "username":myCache.get('username')
        }
    );
})

// @route   POST user/create_room
// @desc    Creates a chat room
// @access  Private
router.post('/create_room',isLoggedIn,async (req,res)=>{

    let id = uuidv4();
    const {name,fam1,fam2,genphy,cardio,derma,ortho} = req.body;
    let participants = [];

    if(fam1!=null)
        participants = participants.concat(fam1);
    if(fam1!=null)
        participants = participants.concat(fam1);
    if(genphy!=null)
        participants = participants.concat(genphy);
    if(cardio!=null)
        participants = participants.concat(cardio);
    if(derma!=null)
        participants = participants.concat(derma);
    if(ortho!=null)
        participants = participants.concat(ortho);
    

    await UserData.updateOne(
        {email:res.locals.user.username},
        {$push:{chatrooms:{name:name,id:id}}}
    );

    if(fam1!=null){
        await UserData.updateOne(
            {email:fam1},
            {$push:{chatrooms:{name:name,id:id}}}
        );
    }
    if(fam2!=null){
        await UserData.updateOne(
            {email:fam2},
            {$push:{chatrooms:{name:name,id:id}}}
        );
    }

    // ===================== Add General Physician ======================
    if(Array.isArray(genphy)){
        genphy.forEach(async (genp)=>{
            await UserData.One(
                {email:genp},
                {$push:{chatrooms:{name:name,id:id}}}
            )
        })
    }else if(genphy != null){
        await UserData.One(
            {email:genphy},
            {$push:{chatrooms:{name:name,id:id}}}
        )
    }

    // ===================== Add Cardiologist ======================
    if(Array.isArray(cardio)){
        cardio.forEach(async (card)=>{
            await UserData.One(
                {email:card},
                {$push:{chatrooms:{name:name,id:id}}}
            )
        })
    }else if(cardio!= null){
        await UserData.One(
            {email:cardio},
            {$push:{chatrooms:{name:name,id:id}}}
        )
    }

    // ===================== Add Dermatologist ======================
    if(Array.isArray(derma)){
        derma.forEach(async (derm)=>{
            await UserData.One(
                {email:derm},
                {$push:{chatrooms:{name:name,id:id}}}
            )
        })
    }else if(derma!= null){
        await UserData.One(
            {email:derma},
            {$push:{chatrooms:{name:name,id:id}}}
        )
    }

    // ===================== Add Ortho ======================
    if(Array.isArray(ortho)){
        ortho.forEach(async (orth)=>{
            await UserData.One(
                {email:orth},
                {$push:{chatrooms:{name:name,id:id}}}
            )
        })
    }else if(ortho!= null){
        await UserData.One(
            {email:ortho},
            {$push:{chatrooms:{name:name,id:id}}}
        )
    }

    const newChat = new Chat({
        ChatID:id,
        ChatName:req.body.name,
        Participants:participants,
        ChatOwner:res.locals.user.username
    });
    await newChat.save();
    res.redirect('/user/chat');
    
    
})

router.get('/chat',isLoggedIn, async (req,res)=>{

    const LoggedInUser = await UserData.findOne({email:res.locals.user.username});
    const Chat = null;
    res.render('start_chat',{rooms:LoggedInUser.chatrooms,prevChat:Chat,username:LoggedInUser.name,id:-1});
})


router.get('/chat/:id',isLoggedIn, async (req,res)=>{

    const LoggedInUser = await UserData.findOne({email:res.locals.user.username});
    const chat = await Chat.findOne({ChatID:req.params.id});
    res.render('chat_rooms',{rooms:LoggedInUser.chatrooms,prevChat:chat,id:req.params.id,username:LoggedInUser.name});
})

router.get('/health_risk',async (req,res)=>{
    res.render("health_risk",{"username":myCache.get('username')});
})

router.post('/health_risk',async (req,res)=>{
    const {age,emer,vent,cancer,diab,hypt,dial,ren,wt,ht} = req.body;
    let result = await axios("http://localhost:8000/sur_risk/",{
        method:"POST",
        data:{
            age:age,
            emer:emer,
            vent:vent,
            cancer:cancer,
            diab:diab,
            hypt:hypt,
            dial:dial,
            ren:ren,
            wt:wt,
            ht:ht
        },headers:{
            'Content-Type': 'application/json',
        }
    })
    let values = result.data.res;
    res.render("health_risk_res",{values,"username":myCache.get('username')});
})

router.get('/review',async (req,res)=>{
    const user = await UserData.findOne({email:res.locals.user.username});
    hospitals = ["CAMBRIDGE HEALTH ALLIANCE","HOLYOKE MEDICAL CENTER","LOWELL GENERAL HOSPITAL","BRIGHAM AND WOMEN'S HOSPITAL","ST ELIZABETH'S MEDICAL CENTER","MOUNT AUBURN HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL - PLYMOUTH","BAYSTATE MEDICAL CENTER","SHRINERS' HOSPITAL FOR CHILDREN (THE)","SAINT ANNE'S HOSPITAL","SOUTHCOAST HOSPITAL GROUP  INC","NORWOOD HOSPITAL","NEWTON-WELLESLEY HOSPITAL","SOUTH SHORE HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL-MILTON INC","NEW ENGLAND BAPTIST HOSPITAL","CARNEY HOSPITAL","LAHEY HOSPITAL & MEDICAL CENTER  BURLINGTON","SIGNATURE HEALTHCARE BROCKTON HOSPITAL","METROWEST MEDICAL CENTER","HALLMARK HEALTH SYSTEM","NORTH SHORE MEDICAL CENTER -","HALLMARK HEALTH MEDICAL ASSOCIATES INC","BROCKTON AREA MULTI-SERVICES  INC.","GOOD SAMARITAN MEDICAL CENTER","MILFORD REGIONAL MEDICAL CENTER","HEALTHALLIANCE HOSPITALS  INC","BAYSTATE FRANKLIN MEDICAL CENTER","MASSACHUSETTS GENERAL HOSPITAL","WINCHESTER HOSPITAL","ANNA JAQUES HOSPITAL","BETH ISRAEL DEACONESS HOSPITAL - NEEDHAM","COOLEY DICKINSON HOSPITAL INC THE","BOSTON CHILDREN'S HOSPITAL","BOSTON MEDICAL CENTER CORPORATION-","MORTON HOSPITAL","MARLBOROUGH HOSPITAL","MERCY MEDICAL CTR","CAPE COD HOSPITAL","BEVERLY HOSPITAL CORPORATION","NOBLE HOSPITAL","PCP89345","PCP128586","HARRINGTON MEMORIAL HOSPITAL-1","Plymouth Outreach Clinic","AT CARE PLLC","Edith Nourse Rogers Memorial Veterans Hospital (Bedford VA)","HEYWOOD HOSPITAL -","UMASS MEMORIAL MEDICAL CENTER INC","ST VINCENT HOSPITAL","ADCARE HOSPITAL OF WORCESTER INC","PCP205980","STURDY MEMORIAL HOSPITAL","NANTUCKET COTTAGE HOSPITAL","MASSACHUSETTS EYE AND EAR INFIRMARY -","BRIGHAM AND WOMEN'S FAULKNER HOSPITAL","LAWRENCE GENERAL HOSPITAL","BETH ISRAEL DEACONESS MEDICAL CENTER","TUFTS MEDICAL CENTER","EMERSON HOSPITAL -","Hyannis Outpatient Clinic","COUNSELING ASSOCIATES OF DRACUT AND METHUEN","CLINTON HOSPITAL ASSOCIATION","Quincy Outpatient Clinic","ORTHOPEDIC AND SPORTS PHYSICAL THERAPY  LLP","FRANCISCAN CHILDREN'S HOSPITAL & REHAB CENTER","FALMOUTH HOSPITAL","PCP26110","HOLY FAMILY HOSPITAL","UHS OF WESTWOOD PEMBROKE INC","BERKSHIRE MEDICAL CENTER INC - 1","Framingham Outpatient Clinic","REHAB RESOLUTIONS INC","NEW ENGLAND ORAL SURGERY ASSOCIATES LLC","BAYSTATE WING HOSPITAL AND MEDICAL CENTERS","PCP44465","PCP136067","SOUTH BAY MENTAL HEALTH CENTER  INC.","PCP10127","VA Boston Healthcare System  Jamaica Plain Campus","Worcester Outpatient Clinic","PCP166697","CAREWELL URGENT CARE CENTERS OF MA  PC","Worcester Vet Center","FAIRVIEW HOSPITAL","Gloucester Community Based Outpatient Clinic (CBOC)","Lowell Outpatient Clinic","PCP191696","PCP67787","PCP139219","Boston Vet Center","Haverhill Community Based Outpatient Clinic (CBOC)","NASHOBA VALLEY MEDICAL CENTER","SHRINERS' HOSPITAL FOR CHILDREN - BOSTON  THE","RIVERSIDE RADIOLOGY MEDICAL GROUP INC","ADAMS PHYSICAL THERAPY  LLC","DENTAL SURGEONS OF FALL RIVER PC","Fitchburg Outpatient Clinic","PCP4453","PCP9047","New Bedford Outpatient Clinic","Springfield Vet Center","MARTHA'S VINEYARD HOSPITAL INC","PCP13802","New Bedford Vet Center","ATHOL MEMORIAL HOSPITAL","PCP52699","PCP77608","VA Boston Healthcare System  Brockton Campus","PCP3184","PCP26077","PCP118611","CAMBRIDGE PUBLIC HEALTH COMMISSION","HAMPDEN PODIATRY ASSOCIATES","SOUTH SHORE RADIOLOGICAL ASSOCIATES  INC.","HEBREW REHABILITATION CENTER","MILTON CHIROPRACTIC AND REHABILITATION INC","MERRIMACK VALLEY PHYSICAL THERAPY"];
    res.render('review.ejs',{hospitals});
})

router.get('/treatment_cost',async (req,res)=>{
    res.render('treatment_cost',{"username":myCache.get('username')})
})

router.get('/outpatient_cost',async (req,res)=>{
    res.render('outpatient_cost',{"username":myCache.get('username')})
})

router.get('/physiotherapy',async (req,res)=>{
    res.render('physiotherapy')
})

router.get('/profile',async (req,res)=>{
    res.render('profile')
})

router.post('/profile',async (req,res)=>{
    let UserInfo = new UserData(
        {
            name:req.body.name,
            email:req.body.email,
            prof:req.body.prof
        }
    )
    await UserInfo.save();
    res.redirect('/user/dashboard');
})

module.exports = router;