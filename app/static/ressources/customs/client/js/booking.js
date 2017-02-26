function booking_data() {
	// Getting the data from the booking page
	var date = $('#datetimepicker').data('DateTimePicker').date();
	var price = $('#price-range').data("ionRangeSlider").result.from;
	var hours = $('#hours').text();
	var subject = $('#subject-select').val();
	var message = $('#feedback-message').val();

	var booking_json = {
		'date': date,
		'price': price,
		'hours': hours,
		'subject': subject,
		'message': message

	};

	return booking_json;
}

$(document).ready( function() {
	// we should make a post request

	$('#book-btn').on('click', function() {
		//$.post('/client/test', {'key1': 1, 'key2': '2'});
		$.ajax({
			url:'/client/reservation_handler',
			type: 'post',
			datatype: 'json',
			contentType: "application/json",
			success: function(data){
				alert(data)
			},
			data: JSON.stringify(booking_data())
		});
	});


});

