const express = require('express');
const app = express();
const router = express.Router();
const { v4: uuidv4 } = require("uuid");

// Body Parser helps to transfer data in forms from one route to other
app.use(express.urlencoded({ extended: true }))
app.use(express.json());  

// +++++++++++++++++++++++++ Models ++++++++++++++++++++++++++++
const User = require('../models/user');



// +++++++++++++++++++++ Auth Support +++++++++++++++++++++++++++
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

// ======================= ROUTES =============================

// @route   GET login/
// @desc    Redirects to the login page
// @access  Public
router.get('/',(req,res)=>{
    res.render("login");
})


// @route   POST login/
// @desc    Logs in a registered user
// @access  Public
router.post("/",
    passport.authenticate("local",{

        // Redirects to the home page on successful login
        successRedirect:'/user/dashboard',

        // Redirects to the login page if login fails
        failureRedirect:"/login"
    })
);
module.exports = router;