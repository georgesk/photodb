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
            { video: {
		width:320,
		height:240,
	    }},
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
        ctxCanvas.drawImage(video, 75, 10, 170, 220, 0,0,320,240);
	videoLive.css({display: "none",});
	shot.css({display: "block"});
    }

    function reset(){
	shot.css({display: "none"});
	videoLive.css({display: "block",});
    }

    $("#nom").autocomplete({
	minLength: 3,
	source:    function(term, callback) {
            $.getJSON("chercheNom.php", term, callback);
	},
    });
    $("#prenom").autocomplete({
	source:    function(term, callback) {
            $.getJSON("cherchePrenom.php", {nom: $("#nom").val(), prenom: $("#prenom").val()}, callback);
	},
    });
});

function envoyer(){
    var nom=$("#nom").val();
    var prenom=$("#prenom").val();
    var canvas=$("#screenshot-canvas").get(0);
    var photodata=canvas.toDataURL("image/jpeg");
    $.ajax("envoi.php",{
	type: "POST",
	data:{
	    prenom: prenom,
	    nom: nom,
	    photo: photodata,
	},
    }).done(
	function(data){
	    console.log("grrr done", data)
	    if (data["statut"]=="dejavu"){
		// il y a déjà une photo!
		$("#dialog").html(
		    "<img style='float:right' alt='image'/>" +
			"<p>Il y a déjà une photo enregistrée pour " +
			nom + " " + prenom +
			"\nVoulez-vous la remplacer ?</p>"
		);
		$("#dialog img").attr("src", data["base64"]);
		$("#dialog").dialog({
		    width: 500,
		    buttons: [
			{
			    text: "Ok",
			    icons: {
				primary: "ui-icon-heart"
			    },
			    click: function() {
				$( this ).dialog( "close" );
				forcerEnvoi();
			    }
 			    //showText: false
			},
			{
			    text: "Échappement",
			    click: function() {
				$( this ).dialog( "close" );
			    }
 			    //showText: false
			},
		    ]
		});
	    } else { //data["statut"]!="dejavu"
		// c'est une nouvelle photo
		$("#dialog").html(
		    "<img style='float:right' alt='image'/>" +
			"<p>Photo enregistrée pour " +
			nom + " " + prenom +
			" avec succès</p>"
		);
		$("#dialog img").attr("src", data["base64"]);		
		$("#dialog").dialog({
		    width: 500,
		    buttons: [
			{
			    text: "Vu",
			    icons: {
				primary: "ui-icon-heart"
			    },
			    click: function() {
				$( this ).dialog( "close" );
				forcerEnvoi();
			    }
 			    //showText: false
			},
		    ]
		});
	    }
	}
    )
    return false;
}

function forcerEnvoi(){
    // fonction de rappel qui force l'envoi d'une photo après confirmation.
    var nom=$("#nom").val();
    var prenom=$("#prenom").val();
    var canvas=$("#screenshot-canvas").get(0);
    var photodata=canvas.toDataURL("image/jpeg");
    $.ajax("force_envoi.php",{
	type: "POST",
	data:{
	    prenom: prenom,
	    nom: nom,
	    photo: photodata,
	},
    }).done(
	function(data){
	    console.log("grrr done", data)
	}
    )
    return false;
}
