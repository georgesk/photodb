
window.onload = function(){
    var img1=document.querySelector("#img1");
    var img2=document.querySelector("#img2");
    img1.src = la_joconde;
    $.post("retouche",{
        data: la_joconde,
    }).done(
        function(data){
            if (data.status=="OK"){
		img2.src=data.imgdata;
	    }
        }
    );
};
