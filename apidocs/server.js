var express = require("express");
 
var app = express();

app.use(express.static('swagger-ui'));

//make way for some custom css, js and images
app.use('/', express.static(__dirname + '/swagger-ui'));

var server = app.listen(12345, function(){
    var port = server.address().port;
    console.log("Server started at http://localhost:%s", port);
});