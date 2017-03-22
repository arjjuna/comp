$(document).ready(function(){
	$('.search-options-wrapper').addClass("hidden");

		$(".search-tile #more-options").on('click', function(){


			$('.search-options-wrapper').toggleClass("hidden");
			$(".search-tile #more-options .more").toggleClass("hidden");
			$(".search-tile #more-options .less").toggleClass("hidden");

			
		});



		$(".clickable-result").hover(
			function(){
				$(this).addClass("light-blue-hover")
			},
			function(){
				$(this).removeClass("light-blue-hover")
		});
});