$(document).ready(function(){
	$('.search-options-wrapper').addClass("");

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

	function getProfs(data, url) {
		url = url || '/recherche/aprof'
		$.ajax({
			type: 'POST',
			url: USER_PREFIX + url,
			contentType: "application/json; charset=utf-8",
			data: JSON.stringify(data),

			dataType: 'html',

			success: function(data, textStatus, jqXHR){
				$(".search-results-wrapper .results_list").html(data);

				if (data == ""){
					$(".no_result").removeClass('hidden');
				} else {
					$(".no_result").addClass('hidden');
				}
				//$(".search-results-wrapper").append(data);
			},

			error: function(xhr, ajaxOptions, thrownError){
				console.log('error');
				console.log(xhr);
			},
		});
	}



	/*if (default_subject) {
		getProfs({'subject_id': default_subject}, '/recherche/subject')
	}*/

	$(".submit-div input.btn").on('click', function(){
		var data = {};

		data['keywords'] = $('<div/>').text($('#search_bar').val()).html();


		//if (!($('.search-options-wrapper').hasClass('hidden')))
		if (true)
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

		//console.log(data);

		$("#search_form textarea").text(JSON.stringify(data));
		//$("#search_form .submit").click();

		getProfs(data);
		
		/*
		$.ajax({
			type: 'POST',
			url: USER_PREFIX + '/recherche',
			contentType: "application/json; charset=utf-8",
			data: JSON.stringify(data),

			//dataType: 'json',

			success: function(data, textStatus, jqXHR){
				console.log('success');
			},

			error: function(xhr, ajaxOptions, thrownError){
				console.log(xhr);
			},

			timeout: 100000,

		}); 
		*/


	});


	$(".submit-div input.btn").click();





});