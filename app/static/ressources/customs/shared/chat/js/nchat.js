var from_ = 1; 
var messages_number = 20;

// How sent and received messages are received
var received_msg	    = '<div class="left-message message">\n'
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
var sent_msg  		    = '<div class="right-message message">\n'
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


function prepend_one_message(messages_selector, type, message){
	//Prepends one message to the chat div, for messages that come from scrolling up
	if (type == 'received') {
		$(messages_selector).prepend(received_msg.replace('{{ text }}', message.text));
		return true;
	}

	if (type == 'sent') {
		$(messages_selector).prepend(sent_msg.replace('{{ text }}', message.text));
		return true;
	}

	return false;
}

function append_one_message(messages_selector, type, message){
	//Appends one message, for messaes that come from the chat socket
	if (type == 'received') {
		$(messages_selector).append(received_msg.replace('{{ text }}', message.text));
		return true;
	}

	if (type == 'sent') {
		$(messages_selector).append(sent_msg.replace('{{ text }}', message.text));
		return true;
	}

	return false;
}




function prepend_messages(data, callback=false) {
	//Prepends a bunch of messages as Json response
	$.each(data, function(n, message) {
		if (message.to_id == user_id){
			//message received
			prepend_one_message('.row.messages-row .messages-from-ajax', 'received', message)
		}
		else if (message.to_id == contact_id){
			prepend_one_message('.row.messages-row .messages-from-ajax', 'sent', message)
		};
	});

	if (callback != false) {
		callback();
	}
};



function fetch_messages(m_from, m_number, callback=false){
	//fetches <m_number> of messages, starting from <m_from>
	var url = chat_root
			+ safe_name + '/'
			+ m_from.toString() + '/'
			+ (m_from+m_number-1).toString()

	$.ajax({
		type: 'GET',
		dataType: 'json',
		url: url,
	  	success: function(data) {
	  		prepend_messages(data, callback);
	  	}
			  	
	});
};





















function scrollPercentFunction(selector, prop=1) {
	// Scrolls down a div
	return function() {
		$(selector).scrollTop($(selector).prop("scrollHeight")*prop);
	};
};







$(document).ready(function() {

	//Fetching messages on scrolling up
	$('.chat-tile .messages-row').scroll(function() {
		var pos = $(this).scrollTop();
		if (pos == 0) {
			fetch_messages(from_, messages_number, scrollPercentFunction('.row.messages-row', 0.05));
			from_ += messages_number;
		}
	});

	//Fetching messages whene clicking on "Voir plus"
	$('.row.messages-row .more-chat').on('click', function(){
		fetch_messages(from_, messages_number, scrollPercentFunction('.row.messages-row', 0.05));
		from_ += messages_number;
	});
});









$(document).ready(function() {
	// Loading the first batch of messages
	fetch_messages(from_, messages_number, scrollPercentFunction('.row.messages-row') );
	from_ += messages_number;
});




/*
function updateContacts() {
	console.log('ff')
	$.each($('.one-contact'), function(n, div){
		div.children('last-message').html('fooo');
	});
}
*/





// handling the socketIO connection

function htmlEntities(str) {
	// Makes text safe
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


var s

$(document).ready(function() {
	//Oppening a socket
	var socket = io.connect('http://' + document.domain + ':' + location.port);

	s = socket

	//Handling a connection to the socket
	socket.on("connect", function(){
		console.log("conected, emitting 'join'")
		socket.emit('join',  {"room": r} );
		console.log("joined")
	});

	//Emulating a click on the send button when pressing enter
	$("#chatBox").keyup(function(event){
	    if(event.keyCode == 13){
	        $("#sendButton").click();
	    }
	});

	//Sending a message
	$("#sendButton").on('click', function(){
		
		if ($("#chatBox").val() != '') {
			
			var message = {
				'text': htmlEntities($("#chatBox").val())
				};

			socket.emit('msg_to_server', {
										room: r,
										from_id: f['id'],
										to_id: t['id'],
										text: message['text']
									}
						);

			console.log('msg_to_server')

			//append_one_message('.row.messages-row .messages-from-ajax', 'sent', message);
			$('#chatBox').val('');
		}
		
	});

	//Handling incoming messages
	socket.on("msg_from_server", function(data){
		console.log('msg_from_server')

		if (data.from_id == f.id){
			append_one_message('.row.messages-row .messages-from-ajax', 'sent', data);
			scrollPercentFunction('.row.messages-row', 2)();
			console.log('msg_rec1');
		}

		if (data.from_id == t.id){
			append_one_message('.row.messages-row .messages-from-ajax', 'received', data);
			scrollPercentFunction('.row.messages-row', 2)();
			console.log('msg_rec2');
		}


		
	});



});
