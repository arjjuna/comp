var from_ = 1;
var messages_number = 20;

function append_messages(data, callback=false) {
	var received_msg    = '<div class="left-message message">\n'
					    + '\t<div class="image">\n'
						+ '\t\t<div class="image-container">\n'
						+ '\t\t\t<img src="/static/uploads/users/placeholder.jpg">\n'
						+ '\t\t</div>\n'
						+ '\t\t<div class="status-color online"></div>\n'
						+ '\t</div>\n'
						+ '\t<div class="message-text">\n'
						+ '\t\t{{ text }}\n' 
						+ '\t</div>\n'
						+ '</div>\n'
	var sent_msg        = '<div class="right-message message">\n'
					    + '\t<div class="image">\n'
						+ '\t\t<div class="image-container">\n'
						+ '\t\t\t<img src="/static/uploads/users/placeholder.jpg">\n'
						+ '\t\t</div>\n'
						+ '\t\t<div class="status-color online"></div>\n'
						+ '\t</div>\n'
						+ '\t<div class="message-text">\n'
						+ '\t\t{{ text }}\n' 
						+ '\t</div>\n'
						+ '</div>\n'


	$.each(data, function(n, message) {
		if (message.to_id == user_id){
			//message received
			$('.row.messages-row .messages-from-ajax').prepend(received_msg.replace('{{ text }}', message.text));
		}
		else if (message.to_id == contact_id){
			$('.row.messages-row .messages-from-ajax').prepend(sent_msg.replace('{{ text }}', message.text));
		};
	});

	if (callback != false) {
		callback();
	}
};



function fetch_messages(m_from, m_number, callback=false){
	var url = '/client/chat/'
			  + safe_name + '/'
			  + m_from.toString() + '/'
			  +	(m_from+m_number-1).toString()

	$.ajax({
		type: 'GET',
		dataType: 'json',
		url: url,
	  	success: function(data) {
	  		append_messages(data, callback);
	  	}
			  	
	});
};

function scrollPercent(selector, prop=1) {
	return function() {
		$(selector).scrollTop($(selector).prop("scrollHeight")*prop)
	};
};

$(document).ready(function() {
	fetch_messages(from_, messages_number, scrollPercent('.row.messages-row') );
	from_ += messages_number;

	$('.chat-tile .messages-row').scroll(function() {
		var pos = $(this).scrollTop();
		if (pos == 0) {
			fetch_messages(from_, messages_number, scrollPercent('.row.messages-row', 0.05));
			from_ += messages_number;
		}
	});

	$('.row.messages-row .more-chat').on('click', function(){
		fetch_messages(from_, messages_number, scrollPercent('.row.messages-row', 0.05));
		from_ += messages_number;
	});
});