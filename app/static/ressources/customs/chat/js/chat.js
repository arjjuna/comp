$(document).ready(function(){
	$(".time").each(function(){

		$(this).html(
				moment($(this).data("time")).format('LLL')
			);
	});
});

function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


$(window).on('load', function(){
	console.log("creating socket")

	var socket = io.connect('http://' + document.domain + ':' + location.port);
	var x = 0;

	console.log("socket created");

	$(".live-chat-body .scrollable").scrollTop($(".live-chat-body .scrollable")[0].scrollHeight);
	
	
	socket.on("connect", function(){
		//console.log("conected, emitting 'join'")
		socket.emit('join',  {room: r} );
		//console.log("joined")
	});
	


	$("#chatBox").keyup(function(event){
	    if(event.keyCode == 13){
	        $("#sendButton").click();
	    }
	});

	$("#sendButton").on('click', function(){
		
		if ($("#chatBox").val() != '') {
			socket.emit('msg_out', {
										room: r,
										from_id: f['id'],
										to_id: t['id'],
										message: htmlEntities($("#chatBox").val())
									});
			//console.log("Sent");
			$('#chatBox').val('');
		}

		
	});

	socket.on("msg_in", function(data){
		//console.log(data);
		if (data['from_id'] == t['id']) {
			// The client (browser user) is the sender of the message
			$("#messages").append('\
				<div class="answer left"> \
                  <div class="avatar"> \
                    <img src="http://bootdey.com/img/Content/avatar/avatar1.png" alt="User name"> \
                    <div class="status online"></div> \
                  </div> \
                  <div class="name">' + f['name'] + '</div> \
                  <div class="text"> ' + data["message"] + ' </div> \
                  <div class="time"></div> \
                </div> \
				');
		}

		if (data['from_id'] == f['id']){
				$("#messages").append('\
					<div class="answer right"> \
						<div class="avatar"> \
						  <img src="http://bootdey.com/img/Content/avatar/avatar2.png" alt="User name"> \
						  <div class="status offline"></div> \
						</div> \
						<div class="name">' + f['name'] + '</div> \
						<div class="text"> ' + data["message"] + ' </div> \
						<div class="time"></div> \
					</div> \
					');
		}


		$(".live-chat-body .scrollable").scrollTop($(".live-chat-body .scrollable")[0].scrollHeight);
	
	});

});


