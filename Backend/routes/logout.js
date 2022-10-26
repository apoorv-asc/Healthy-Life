const express = require("express");
const app = express();
const router = express.Router();


// @route   GET logout/
// @desc    Logs out the current user
// @access  Public
router.get("/", function (req, res, next) {
  req.logout(function (err) {
    if (err) {
      return next(err);
    }
    res.redirect("/login");
  });
});

module.exports = router;
