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




	//$('.search-options-wrapper').removeClass("hidden"); //this must go later
	
	$('#search_bar').keyup(function(e){
		if (e.keyCode ==13){
			$(".submit-div input.btn").click();
		}
	});

	$(".submit-div input.btn").on('click', function(){
		var data = {};

		data['keywords'] = $('<div/>').text($('#search_bar').val()).html();

		if (!($('.search-options-wrapper').hasClass('hidden')))
		{
			$(".select2_multiple").each(function(index, value){
				data[$(this).attr('id')] = $(this).val();
			});

			$(".slider input").each(function(index, value){
				var slider_data = $(this).data("ionRangeSlider");

				data[$(this).attr('id')] = {
					from: slider_data.result.from,
					to:   slider_data.result.to
				}
			});
		};

		console.log(data);


	});






});