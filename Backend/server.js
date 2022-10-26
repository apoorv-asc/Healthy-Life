const express = require('express');
const app = express();

const bodyParser = require('body-parser');

const server = require("http").Server(app);
const io = require("socket.io")(server);


app.set("view engine","ejs");
app.use(express.static("public")); // Allows the use of files present in public directory

app.use(bodyParser.urlencoded({extended:true}));
app.use(express.json({extended: false}));

// +++++++++++++++++++ Connect to DB ++++++++++++++++++++++
const connectDB = require('./config/db'); // Connects to MongoDB database
connectDB();

// +++++++++++++++++++++++++ Models ++++++++++++++++++++++++++++
var User= require('./models/user');


// ++++++++++++++++++ IMPORT for Authentication ++++++++++++++++++++++++

var passport              = require("passport");
var LocalStrategy         = require("passport-local");
var passportLocalMongoose = require("passport-local-mongoose");


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

app.use(function(req,res,next){
    res.locals.user=req.user;
    next();
})

// +++++++++++++++++++++++ ROUTES ++++++++++++++++++++++++++++
app.use('/registeration',require('./routes/registeration'));
app.use('/login',require('./routes/login'));
app.use('/logout',require('./routes/logout'));

app.use('/user',require('./routes/user'));
app.use('/fitbit',require('./routes/fitbit'));

app.use('/ml',require('./routes/ml'));



app.get('/',(req,res)=>{
    res.render('optum_home');
})

io.on("connection", (socket) => {

    // Personal Chat (chat.ejs)
    socket.on('join',(options,callback)=>{
        socket.join(options.roomId);
        
        socket.on('sendMessage',async (data, callback) => {
            console.log(data.roomId);
            const chat =await Chat.findOne({ChatID:data.roomId});
            chat.msg.push({
                username:data.username,
                message:data.message,
                timestamp:data.time,
            })
            await chat.save();
            // Displays the message in the chat page
            io.to(data.roomId).emit('Show-Message', {username:data.username, msg:data.message})
            callback()
        })

    })

});




// +++++++++++++++ Start Server on PORT:3001 ++++++++++++++++

server.listen(3001,(req,res)=>{
    console.log("Listening on Port 3001");
})