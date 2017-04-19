$(function(){

	var crop_data = {x: 0, y: 0, width: 0, height: 0}

	$('#to_crop').cropper({
	  aspectRatio: 1 / 1,
	  viewMode: 2,
	  crop: function(e) {

	  	crop_data.x = e.x
	  	crop_data.y = e.y
	  	crop_data.width  = e.width
	  	crop_data.height = e.height


	    // Output the result data for cropping image.
	    //console.log("###########")
	    //console.log(e.x);
	    //console.log(e.y);
	    //console.log(e.width);
	    //console.log(e.height);
	  }
	});

	$("#save_crop").on('click', function(){
		$.ajax({
			type: 'POST',
			url: crop_picture_url,
			data: JSON.stringify(crop_data),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
			success: function(data){
				console.log(data);
				$(window).scrollTop(0);
		    	location.reload();
			},
			failure: function(errMsg) {
		        console.log(errMsg);
		        $.alert("Une erreur c'est produite, contactez le support technique");
		    }

		});

	});

});