$(window).click(function() {
	$(".navbar-header .message-list, \
	   .navbar-header .notification-list, \
	   .navbar-header .profile-list").addClass("hidden");
});

$(" .navbar-header .message-icon, .navbar-header .message-list, \
	.navbar-header .notification-icon, .navbar-header .notification-list, \
	.navbar-header .name-wrapper, .navbar-header .profile-list ").click(function(event){
    event.stopPropagation();
});

$(document).ready(function(){

	var LONG_POLL_DURATION = 60000;
	var TIME_OUT_DURATION  = 5000;

	var WINDOW_NOTIFICATIONS         = 0;
	var WINDOW_NOTIFICATIONS_COUNTER = 0;
	var WINDOW_MESSAGES_COUNTER      = 0;

	function UpdateTitle() {
		//console.log("updating title");
		WINDOW_NOTIFICATIONS = WINDOW_NOTIFICATIONS_COUNTER + WINDOW_MESSAGES_COUNTER;
		if (WINDOW_NOTIFICATIONS == 0){
			$('title').text("ostudy") ;
		} else {
			$('title').text("(" + WINDOW_NOTIFICATIONS.toString() + ") " + "ostudy") ;	
		}
		
	};

	UpdateTitle();


	function ParseMessagesTimes()
	{
		$(".message-time").each( function(i, obj){

			if (moment($(this).data('time')	).isSame(moment(), 'day')) {
				$(this).text(
					moment(
							$(this).data('time')
						).format("hh:mm"));
			}
			else {
				$(this).text(
					moment(
							$(this).data('time')
						  ).fromNow());
			}
		});
	 }


	function ParseNotificationsTimes()
	{
		$(".notification-time").each( function(i, obj){

			if (moment($(this).data('time')	).isSame(moment(), 'day')) {
				$(this).text(
					moment(
							$(this).data('time')
						).format("hh:mm"));
			}
			else {
				$(this).text(
					moment(
							$(this).data('time')
						  ).fromNow());
			}
		});
	 }


	 ParseNotificationsTimes()
	 ParseMessagesTimes();

	$(".navbar-header .message-icon").on('click', function(){
		$(".navbar-header .notification-list").addClass("hidden");
		$(".navbar-header .profile-list").addClass("hidden");
		$(".navbar-header .message-list").toggleClass("hidden");
	});

	$(".navbar-header .notification-icon").on('click', function(){
		$(".navbar-header .message-list").addClass("hidden");
		$(".navbar-header .profile-list").addClass("hidden");
		$(".navbar-header .notification-list").toggleClass("hidden");

	});
	$(".navbar-header .name-wrapper").on('click', function(){
		$(".navbar-header .message-list").addClass("hidden");
		$(".navbar-header .notification-list").addClass("hidden");
		$(".navbar-header .profile-list").toggleClass("hidden");
	});



	

	$(".profile-tile .overview .see-more-text span.more").on('click', function(){
		$(".overview .overview-text").removeClass('crippled');
		$(this).addClass("hidden");
		$(".profile-tile .overview .see-more-text span.less").removeClass("hidden");
	});

	$(".profile-tile .overview .see-more-text span.less").on('click', function(){
		$(".overview .overview-text").addClass('crippled');
		$(this).addClass("hidden");
		$(".profile-tile .overview .see-more-text span.more").removeClass("hidden");
	});




	$(".message-icon").on('click', function() {

		
		$.ajax({
		type: 'POST',
		dataType: 'json',
		url: 'reset_unread',
	  	success: function(data) {
		  		//console.log("Noice");
		  		WINDOW_MESSAGES_COUNTER = 0;
		  	}
			  	
		});

		$(".message-icon .unread-number").text("");
		UpdateTitle();

		

	}); 

	$(".notification-icon").on('click', function() {

		$.ajax({
		type: 'POST',
		dataType: 'json',
		url: 'reset_notification',
	  	success: function(data) {
		  		//console.log("Noice");
		  		WINDOW_NOTIFICATIONS_COUNTER = 0;
		  	}
			  	
		});

		$(".notification-icon .notification-number").text("");
		UpdateTitle();


	}); 






function LoadUnreadMessages()
{
	var ERROR = 0;

	//console.log("loading messages");

	$.ajax({
		type: 'POST',
		url: USER_PREFIX + '/unread_msgs_number_lp',
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify({'n': $(".message-icon .unread-number").first().text()}),

		dataType: 'json',

	  	success: function(data, textStatus, jqXHR) {
	  			ERROR = 0;
	  			if (data.n == 0){
		  			$(".message-icon .unread-number").text("");
	  			}
	  			else{
	  				WINDOW_MESSAGES_COUNTER =  data.n;
		  			$(".message-icon .unread-number").text(data.n);
	  			}
	  			UpdateTitle();
		  	},
		error: function() {
				ERROR = 1;
			},

		complete: function(){
				if (ERROR){
					setTimeout(LoadUnreadMessages, TIME_OUT_DURATION);
				} else {
					LoadUnreadMessages();
				}
			},

		timeout:  LONG_POLL_DURATION,

		
		});
}



function LoadNotifications()
{
	var ERROR = 0;

	//console.log("loading notifs");
	$.ajax({
		type: 'POST',
		url: USER_PREFIX + '/notification_number_lp',
		contentType: "application/json; charset=utf-8",
		data: JSON.stringify({'n': $(".notification-icon .notification-number").first().text()}),

		dataType: 'json',

	  	success: function(data, textStatus, jqXHR) {
	  			ERROR = 0;
	  			if (data.n == 0){
		  			$(".notification-icon .notification-number").text("");
		  			//$('title').text("ostudy");
	  			}
	  			else{
	  				WINDOW_NOTIFICATIONS_COUNTER =  data.n;
		  			$(".notification-icon .notification-number").text(data.n);
		  			//$('title').text("(" + WINDOW_NOTIFICATIONS.toString() + ") " + "ostudy") ;
	  			}
	  			UpdateTitle();
		  	},
		error: function(xhr, ajaxOptions, thrownError) {
				ERROR = 1;
				console.log("eroooooooooor c");
				console.log(xhr);
			},

		complete: function(){
				if (ERROR){
					setTimeout(LoadNotifications, TIME_OUT_DURATION);
				} else {
					LoadNotifications();
				}
			},

		timeout:  LONG_POLL_DURATION,

		
		});
}






$(".message-icon .unread-number").first().text("")
$(".notification-icon .notification-number").first().text("")

LoadUnreadMessages();
LoadNotifications();

//setInterval(LoadUnreadMessages2, 2000);

/*
function AppendNotification(picture, text, timestamp, link)
{	
	var notification_template = '<li> \
									<a href="' + link + '" class="div-link"> \
										<div> \
											<img src="' + picture + '"> \
											<div class="middle-wrapper"> \
												<div class="notification-text">' + text + '</div> \
											</div> \
											<div class="notification-time" data-time="' + timestamp + '"></div> \
										</div> \
									</a> \
								</li>';


	$(".notification-list ul").append(notification_template);
}
*/

/*
function AppendMessage(chat_link, picture_link, full_name, text, time, type)
{	
	var message_template, arrow='', unread_class;

	if (type == "sent"){
		arrow = '<i class="fa fa-arrow-left" aria-hidden="true"></i>';
	}
	else if (type == "received"){
		arrow = '<i class="fa fa-arrow-right" aria-hidden="true"></i>';
	}

	message_template = '<a href=' + chat_link + ' class="div-link"> \
							<div>	\
								<li>	\
									<img src="' + picture_link + '">	\
									<div class="middle-wrapper">	\
										<div class="message-sender">' + full_name + ' </div>	\
										<div class="message-prev">'	+ arrow + " " + text + '</div>	\
									</div>	\
									<div class="message-time" data-time="' + time + '"> </div>	\
								</li>	\
							</div>	\
						</a>';




	$(".message-list ul").append(message_template);
}
*/


/*
function FetchNotifications()
{
	$.ajax({
		type: 'POST',
		url: 'fetch_notifications',
		contentType: "application/json; charset=utf-8",
		data: {},

		dataType: 'json',

	  	success: function(data, textStatus, jqXHR) {
	  		UpdateAllNotifications(data);
		  	},
		error: function (jqXHR, exception) {
			// error handling logic here..
		},
		
		});

}
*/

function FetchNotificationsHtml()
{
	$.ajax({
		type: 'POST',
		url: USER_PREFIX + '/fetch_notifications_html',
		contentType: "application/json; charset=utf-8",
		data: {},

		dataType: 'html',

	  	success: function(data, textStatus, jqXHR) {
	  		UpdateAllNotificationsHtml(data);
		  	},
		error: function (jqXHR, exception) {
			// error handling logic here..
		},
		
		});

}
 /*
function FetchMessages()
{	
	$.ajax({
		type: 'POST',
		url: USER_PREFIX + '/fetch_messages',
		contentType: "application/json; charset=utf-8",
		data: {},

		dataType: 'json',

	  	success: function(data, textStatus, jqXHR) {
	  		UpdateAllMessages(data);
		  	},
		error: function (jqXHR, exception) {
			// error handling logic here..
			console.log("pewpew");
		},
		
		});

}
*/

function FetchMessagesHtml()
{	
	$.ajax({
		type: 'POST',
		url: USER_PREFIX + '/fetch_messages_html',
		contentType: "application/json; charset=utf-8",
		data: {},

		dataType: 'html',

	  	success: function(data, textStatus, jqXHR) {
	  		UpdateAllMessagesHtml(data);
		  	},
		error: function (jqXHR, exception) {
			// error handling logic here..
			console.log("pewpew");
		},
		
		});

}
/*
function UpdateAllNotifications(data)
{	
	var n;
	$(".notification-list ul").text(""); 

	for (var i = 0; i < data.length; i++){
		n = data[i];
		AppendNotification(n['picture'], n['text'], n['timestamp'], n['link']);

	}

	ParseNotificationsTimes();	
}
*/

function UpdateAllNotificationsHtml(data)
{	
	$(".notification-list ul").text(""); 

	$(".notification-list ul").append(data);

	ParseNotificationsTimes();	
}


function UpdateAllMessagesHtml(data)
{	
	$(".message-list ul").text(""); 

	$(".message-list ul").append(data);

	ParseMessagesTimes();	
}


/*
function UpdateAllMessages(data)
{	
	var n;
	$(".message-list ul").text(""); 

	for (var i = 0; i < data.length; i++){
		//n = JSON.parse(data[i]);

		//console.log('appending message');
		//console.log(data[i].message_obj.text);

		AppendMessage(  
			data[i].who.chat_link,
			data[i].who.picture_link,
			data[i].who.full_name,
			data[i].message_obj.text,
			data[i].message_obj.timestamp,
			data[i].type
			);

	}

	ParseMessagesTimes();	
}
*/




$(".notification-icon").on('click', FetchNotificationsHtml);
$(".message-icon").on('click', FetchMessagesHtml);




});





/**/
