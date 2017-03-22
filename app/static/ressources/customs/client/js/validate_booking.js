
$(document).ready(function(){
	//Making a post request to the validation handler

	$('.provide-feedback .send-feedback').on('click', function(){
		var feedback_row = $(this).closest('.provide-feedback');
		var feedback_data = {
							 'id': $(this).data('id'),
							 'stars': feedback_row.find('#score-value').text(),
							 'message': feedback_row.find('#feedback-message').val()
						    };
		var request_global

		function make_ajax_call(){
					$.ajax({
						url:'/client/validation',
						type: 'post',
						dataType: 'text',
						contentType: "application/json",
						success: function(data, textStatus, request){
									if (textStatus == "success") {
						                //window.location.href = request.getResponseHeader('location');
						                request_global = request
						            }
						            else {
						                // Process the expected results...
						            }
								},
						data: JSON.stringify(feedback_data)
					});
		}


		$.confirm({
			'title': 'Confirmer la validation',
		    content: 'ê'.toUpperCase() + 'tes vous sure de vouloir valider la séance?',
		    buttons: {
				        confirmer: function () {
				            make_ajax_call();
				            //console.log(feedback_data);
				            $.confirm({
				            	title: '',
				            	content: 'Séance validée!',
				            	buttons: {
				            		ok: function(){
				            			window.location.href = request_global.getResponseHeader('location');
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