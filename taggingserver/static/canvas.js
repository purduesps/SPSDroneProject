var canvas, ctx, isout = false,
downX = 0,
upX = 0,
downY = 0,
upY = 0;
var  boxsize = 20;
tags ={};

function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

function addbox (t,xpos,ypos,height,width){
    t.Xpos.push(xpos);
    t.Ypos.push(ypos);
    t.heights.push(height);
    t.widths.push(width);
}

function init() {
    var reg = /\d+/g;
    cookdata = reg.exec( document.cookie);
    tags.ID = cookdata[0];
    tags.Xpos = [];
    tags.Ypos = [];
    tags.heights = [];
    tags.widths = [];
    console.log(tags.ID);
    canvas = document.getElementById('can');
    ctx = canvas.getContext("2d");
    w = canvas.width;
    h = canvas.height;

    canvas.addEventListener("mousemove", function (e) {
        findxy('move', e)
    }, false);
    canvas.addEventListener("mousedown", function (e) {
        findxy('down', e)
    }, false);
    canvas.addEventListener("mouseup", function (e) {
        findxy('up', e)
    }, false);
    canvas.addEventListener("mouseout", function (e) {
        findxy('out', e)
    }, false);
    canvas.addEventListener("mousein", function (e) {
        findxy('in', e)
    }, false);
}

function draw() {
    //addbox(tags,(downX+upX)/2,(downY+upY)/2,Math.abs(downX-upX),Math.abs(downY-upY));
    addbox(tags, downX, downY, boxsize,boxsize);
    ctx.beginPath();
    ctx.moveTo(downX-boxsize/2, downY-boxsize/2);
    ctx.lineTo(downX-boxsize/2, downY+boxsize/2);
    ctx.lineTo(downX+boxsize/2, downY+boxsize/2);
    ctx.lineTo(downX+boxsize/2, downY-boxsize/2);
    ctx.lineTo(downX-boxsize/2, downY-boxsize/2);
    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.closePath();
}
// Post to the provided URL with the specified parameters.
function post(path, parameters) {
    var form = $('<form></form>');

    form.attr("method", "post");
    form.attr("action", path);

    $.each(parameters, function(key, value) {
        var field = $('<input></input>');

        field.attr("type", "hidden");
        field.attr("name", key);
        field.attr("value", value);

        form.append(field);
    });

    // The form needs to be a part of the document in
    // order for us to be able to submit it.
    $(document.body).append(form);
    form.submit();
}

function erase() {
    var m = confirm("Want to clear");
    if (m) {
        tags.Xpos = [];
        tags.Ypos = [];
        tags.heights = [];
        tags.widths = [];
        ctx.clearRect(0, 0, w, h);
        document.getElementById("canvasimg").style.display = "none";
    }
}

function del() {
    ctx.clearRect(downX-boxsize/2, downY-boxsize/2,boxsize+5,boxsize+5)
}

function save() {
    console.log(JSON.stringify(tags));
    post('/return',tags);
}

function findxy(res, e) {
    if (res === "down") {
        downX = e.clientX - canvas.offsetLeft;
        downY = e.clientY - canvas.offsetTop;
        draw();
    }
    if ( res === "up") {
        upX = e.clientX - canvas.offsetLeft;
        upY = e.clientY - canvas.offsetTop;
    }
    if ( res === "in") {
        isout = false;
    }
    if ( res === "out") {
        upX = 0;
        upY = 0;
        isout = true;
    }
}
