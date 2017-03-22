
$(document).ready( function() {
	// we should make a post request

	$('.abooking.waiting .cancel').on('click', function() {
		//$.post('/client/test', {'key1': 1, 'key2': '2'});

		var booking = {"id": $(this).closest(".abooking.waiting").data("id")}


		function make_ajax_call(){
					$.ajax({
						url:'/client/cancelation',
						type: 'post',
						dataType: 'text',
						contentType: "application/json",
						success: function(data, textStatus, request){
									if (textStatus == "success") {
						                //window.location.href = request.getResponseHeader('location');
						            }
						            else {
						                // Process the expected results...
						            }
								},
						data: JSON.stringify(booking)
					});
		}

		$.confirm({
		    title: 'Annulation',
		    content: 'ê'.toUpperCase() + 'tes vous sure de vouloir annuler la réservation?',
		    buttons: {
				        confirmer: function () {
				            make_ajax_call();
				            $.confirm({
				            	title: '',
				            	content: 'Réservation annulée!',
				            	buttons: {
				            		ok: function(){
				            			location.reload();
				            		}
				            	}


				        	});
				        },

				        annuler: function () {
				        },
		    		  },
		    //backgroundDismiss: true,
		});
		

	});


});

