function onFailure(err) {
    alert("Erreur : " + err.name + ", " + err.message);
}

var c = document.createElement("canvas"); // an invisible canvas for computations

var message;
var otherimage;
var video;
var face;

jQuery(document).ready(function () {
    // init global variables
    message=$("#message");
    otherimage=$("#otherimage");
    video = document.querySelector('#webcam');
    face=$($("#svgContainer")[0].children[0])
    
    // make overlaied objects
    var w=$("#webcam");
    $("#svgContainer").offset(w.offset());

    // start the video
    var constraints={video: {width:320, height:240}};
    navigator.mediaDevices.getUserMedia(constraints).then(
        function (localMediaStream) {
            video.srcObject = localMediaStream;
	    video.onloadedmetadata = function(e) {video.play();};	 
        }).catch(
	    function(err) {
		alert("Erreur : " + err.name + ", " + err.message);
	    });

    // start the fast interactive loop
    setTimeout(findFace,0);
    
    $("#nom").autocomplete({
	minLength: 3,
	source:    function(term, callback) {
            $.getJSON("/chercheNom", term, callback);
	},
	// effacer le prénom pendant qu'on bricole le nom !
	// et aussi : remttre en saisie de vidéo
	search: function( event, ui ) {$("#prenom").val("")},
	change: function( event, ui ) {$("#prenom").val("");},
    });
    $("#prenom").autocomplete({
	source:    function(term, callback) {
            $.getJSON("/cherchePrenom", {nom: $("#nom").val(), prenom: $("#prenom").val()}, callback);
	},
    });
});

/**
 * tries to find faces twice a second
 **/
function findFace(){
    c.width=video.videoWidth;
    c.height = video.videoHeight;
    var ctx=c.getContext('2d');
    ctx.drawImage(video,0,0,320,240);
    var photodata=c.toDataURL("image/jpeg");
    $.post("/encadre",{
	photo: photodata,
	nom: $("#nom").val(),
	prenom: $("#prenom").val(),
    }).done(function(data){
	if (data.status){
	    face.attr({
		x: 320-data.rect.x-data.rect.w, // because of the symmetry
		y: data.rect.y,
		width: data.rect.w,
		height: data.rect.h
	    });
	} else {
	    face.attr({x: "-100", y: "-100", width: "0", height: "0"});
	}
	console.log(data.message, data.oldimage.length > 0);
	if (data.message){
	    message.text(data.message);
	    message.show();
	} else {
	    message.hide();
	}
	if (data.oldimage){
	    otherimage.attr({src: data.oldimage});
	    otherimage.show();
	} else {
	    otherimage.hide();
	}
    });
    setTimeout(findFace,333);
}

function envoyer(){
    var nom=$("#nom").val();
    var prenom=$("#prenom").val();
    c.width=video.videoWidth;
    c.height = video.videoHeight;
    var ctx=c.getContext('2d');
    ctx.drawImage(video,0,0,320,240);
    var photodata=c.toDataURL("image/jpeg");
    $.ajax("/envoi",{
	type: "POST",
	data:{
	    prenom: prenom,
	    nom: nom,
	    photo: photodata,
	},
    }).done(
	function(data){
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
	    } else if (data["statut"]=="ok"){ 
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
			    }
 			    //showText: false
			},
		    ]
		});
	    } else if (data["statut"]=="malretouche"){ 
		$("#dialog").html(
		    "<img align='right' src='"+data["base64"]+"'/>" +
		    "<p>Le système détecte mal le visage à recadrer.</p>" +
			"<p>Veuillez refaire la photo.</p>"
		);
		$("#dialog").dialog({
		    width: 500,
		    buttons: [
			{
			    text: "OK",
			    icons: {
				primary: "ui-icon-heart"
			    },
			    click: function() {
				$( this ).dialog( "close" );
			    }
			},
		    ]
		});
	    } else { // dernière possibilité : data["statut"]=="nouveau"
		$("#dialog").html(
		    "<p>On ne trouve pas " +
			nom + " " + prenom +
			" dans la base de données actuelle</p>" +
			"<p>Voulez-vous créer cet enregistrement ?</p>"
		);
		$("#dialog").dialog({
		    width: 500,
		    buttons: [
			{
			    text: "OK",
			    icons: {
				primary: "ui-icon-heart"
			    },
			    click: function() {
				$( this ).dialog( "close" );
				nouvelEnvoi();
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
	    }
	}
    )
    return false;
}

function forcerEnvoi(){
    // fonction de rappel qui force l'envoi d'une photo après confirmation.
    var nom=$("#nom").val();
    var prenom=$("#prenom").val();
    c.width=video.videoWidth;
    c.height = video.videoHeight;
    var ctx=c.getContext('2d');
    ctx.drawImage(video,0,0,320,240);
    var photodata=c.toDataURL("image/jpeg");
    $.ajax("/force_envoi",{
	type: "POST",
	data:{
	    prenom: prenom,
	    nom: nom,
	    photo: photodata,
	},
    }).done(
	function(data){
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
			}
 			//showText: false
		    },
		]
	    });
	}
    )
    return false;
}

function nouvelEnvoi(){
    // on envoie la photo d'une personne encore inconnue de la base de
    // données, donc on doit faire un INSERT, pas un UPDATE
    var nom=$("#nom").val();
    var prenom=$("#prenom").val();
    c.width=video.videoWidth;
    c.height = video.videoHeight;
    var ctx=c.getContext('2d');
    ctx.drawImage(video,0,0,320,240);
    var photodata=c.toDataURL("image/jpeg");
    $.ajax("/nouvel_envoi",{
	type: "POST",
	data:{
	    prenom: prenom,
	    nom: nom,
	    photo: photodata,
	},
    }).done(
	function(data){
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
			}
 			//showText: false
		    },
		]
	    });
	}
    )
    return false;
}
