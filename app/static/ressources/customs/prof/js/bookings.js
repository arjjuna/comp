function make_ajax_call(url, data) {
			$.ajax({
				url: url,
				type: 'post',
				dataType: 'text',
				contentType: "application/json",
				success: function(data, textStatus, request) {
					window.location.href = request.getResponseHeader('location');
				},

				data: data,

			});
		}
		// function end

$(document).ready( function(){
	$('.abooking .accept').on('click', function() {
		//The booking to accept
		booking = {'id': $(this).data('bookingId')};

		make_ajax_call('reservation/accept', JSON.stringify(booking));
	});
	$('.abooking .decline').on('click', function() {
		//The booking to accept
		booking = {'id': $(this).data('bookingId')};

		make_ajax_call('reservation/decline', JSON.stringify(booking));
	});

});