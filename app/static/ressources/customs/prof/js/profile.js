$(function () {
	$('#birth_date').datetimepicker({
	    format: 'DD/MM/YYYY',
	});

	$('input.my_date_input').datetimepicker({
	    format: 'MM/YYYY',
	});

	$('.my_date').each(function(index, value){
		var d = $(this).data("date"), formatted_date;

		formatted_date = moment(d).isValid() ? moment(d).format("MMMM YYYY") : "";
		$(this).text(formatted_date);

	});

	$(".edit_education").each(function(index, value){
		$(this).on('click', function(){
			$(this).closest(".an_education").find(
				".education_form, .education_list, .edit-btn, .cancel-btn,\
				 .delete-btn, .copy-btn"
				).toggleClass("hidden");

			$(".add_education").toggleClass("hidden");
		});
	});

	$(".copy-btn").on('click', function(){
		$("#"+$(this).data("id")).click();
	});

	$(".delete_education").each(function(index, value){
		$(this).on('click', function(){

			var id=$(this).data("id");
			
			$.confirm({
			    title: 'Suppression',
			    content: 'Supprimer education?',
			    buttons: {
			        confirm: function () {
        				console.log(id);
        				$.ajax({
        					type: "POST",
        					url: delete_education_url,
        					data: JSON.stringify({ _id: id }),
						    contentType: "application/json; charset=utf-8",
						    dataType: "json",
						    success: function(data){
						    	$.alert('Supprimé!');
						    	location.reload();
						    },
						    failure: function(errMsg) {
						        console.log(errMsg);
						        $.alert("Une erreur c'est produite, contactez le support technique");
						    }

        				});


			            
			        },
			        cancel: function () {
			        },
			    }
			});

		});
	});

	$(".edit_experience").each(function(index, value){
		$(this).on('click', function(){
			$(this).closest(".an_experience").find(
				".experience_form, .experience_list, .edit-btn, .cancel-btn,\
				 .delete-btn, .copy-btn"
				).toggleClass("hidden");
			
			$(".add_experience").toggleClass("hidden");
		});
	});


	$(".delete_experience").each(function(index, value){
		$(this).on('click', function(){

			var id=$(this).data("id");
			
			$.confirm({
			    title: 'Suppression',
			    content: 'Supprimer éxpérience?',
			    buttons: {
			        confirm: function () {
        				console.log(id);
        				$.ajax({
        					type: "POST",
        					url: delete_experience_url,
        					data: JSON.stringify({ _id: id }),
						    contentType: "application/json; charset=utf-8",
						    dataType: "json",
						    success: function(data){
						    	$.alert('Supprimé!');
						    	location.reload();
						    },
						    failure: function(errMsg) {
						        console.log(errMsg);
						        $.alert("Une erreur c'est produite, contactez le support technique");
						    }

        				});


			            
			        },
			        cancel: function () {
			        },
			    }
			});

		});
	});



});