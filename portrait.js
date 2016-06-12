function onFailure(err) {
    alert("Erreur : " + err.name);
}
jQuery(document).ready(function () {

    var video = document.querySelector('#webcam');
    var button0 = document.querySelector('#screenshot-button');
    var button1 = document.querySelector('#reset-button');
    var canvas = document.querySelector('#screenshot-canvas');
    var ctxCanvas = canvas.getContext('2d');
    var videoLive = $("#videoLive");
    var shot = $("#shot");
    shot.css({display: "none"});
    var w=$("#webcam");
    $("#svgContainer").offset(w.offset());

    navigator.getUserMedia = (navigator.getUserMedia ||
                              navigator.webkitGetUserMedia ||
                              navigator.mozGetUserMedia ||
                              navigator.msGetUserMedia);
    if (navigator.getUserMedia) {
        navigator.getUserMedia
        (
            { video: true },
            function (localMediaStream) {
                video.src = window.URL.createObjectURL(localMediaStream);
            }, onFailure);
    }
    else {
        onFailure();
    }
    button0.addEventListener('click',snapshot, false);
    $("#svgContainer").on("click",snapshot);
    button1.addEventListener('click',reset, false);
    canvas.addEventListener('click',reset, false);
    
    function snapshot() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctxCanvas.drawImage(video, 150, 20, 340, 440, 0,0,640,480);
	videoLive.css({display: "none",});
	shot.css({display: "block"});
    }

    function reset(){
	shot.css({display: "none"});
	videoLive.css({display: "block",});
    }
});
