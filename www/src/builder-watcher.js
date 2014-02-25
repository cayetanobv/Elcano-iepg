var watch = require('node-watch');
var exec = require('child_process').exec;

var param = (process.argv.length == 3 && process.argv[2]=="debug") ? "debug" : "";

watch('backend', function(filename) {
    exec("jake " + param,function (error, stdout, stderr){
        if (error) {
            console.log(error);
            console.log(stderr);
        }
        else{
            console.log(stdout);    
        }   
    });
});


