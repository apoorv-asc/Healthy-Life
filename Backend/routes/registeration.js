const express = require('express');
const app = express();
const router = express.Router();
const { v4: uuidv4 } = require("uuid");

// Body Parser helps to transfer data in forms from one route to other
app.use(express.urlencoded({ extended: true }))
app.use(express.json());  


// +++++++++++++++++++++++++ Models ++++++++++++++++++++++++++++
const User = require('../models/user');
const UserData = require('../models/userdata');


// ++++++++++++++++++++++ Auth Support ++++++++++++++++++++++++++
var passport             = require("passport");
var LocalStrategy        = require("passport-local");
var passportLocalMongoose= require("passport-local-mongoose");

// Passes authentication key. This key is used for hashing of password
app.use(require("express-session")({
    secret:"Optum_S04",
    resave:false,
    saveUninitialized:false
}));

app.use(passport.initialize());
app.use(passport.session());



passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());


// +++++++++++++++++++++++ ROUTES ++++++++++++++++++++++++++++
// @route   GET registeration/
// @desc    Redirects to registration page
// @access  Public
router.get('/',(req,res)=>{
    res.render("register");
})


// @route   POST registeration/
// @desc    Registers a new user
// @access  Public
router.post('/',function(req,res){
    try{
        User.register(new User({username:req.body.username}),req.body.password, function(err){
            if(err){
                console.log(err.message);
                res.send(req.body.username+" "+req.body.password);
            }
            else{
                passport.authenticate("local")(req,res,function(){
                    res.render('register_user',{email:req.body.username})
                })
            }
        })
    }catch(err){
        console.log(err);
        res.redirect('/registration');
    }
})

// @route   POST registeration/reg_user
// @desc    Adds info of the recently added user
// @access  Public
router.post('/reg_user',async (req,res)=>{
    let UserInfo = new UserData(
        {
            name:req.body.name,
            email:req.body.email,
            prof:req.body.prof
        }
    )
    await UserInfo.save();
    res.redirect('/user/home');
})

module.exports = router;