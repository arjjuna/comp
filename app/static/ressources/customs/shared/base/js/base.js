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





});



/**/
