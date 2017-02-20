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



	$('.search-options-wrapper').addClass("hidden");

	$(".search-tile #more-options").on('click', function(){
		$('.search-options-wrapper').toggleClass("hidden");
		$(".search-tile #more-options .more").toggleClass("hidden");
		$(".search-tile #more-options .less").toggleClass("hidden");
	});



	$(".clickable-result").hover(
		function(){
			$(".clickable-result").addClass("light-blue-hover")
		},
		function(){
			$(".clickable-result").removeClass("light-blue-hover")
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
