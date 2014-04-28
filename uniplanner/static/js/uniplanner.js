$(document).ready( function( ){
	$(window).scroll(function(e) {
		if ($(this).scrollTop() >= 60 && $('#navbar').css('position') != 'fixed') 
		{
			$('#navbar').css({
				'position': 'fixed',
				'top': '-60px',
				'width': $(this).width()
			}),
			$('#content').css({
				'margin-top': '140px'
			});
		}
		else if ($(this).scrollTop() < 60 && $('.scroller').css('position') != 'relative') 
		{
			$('#navbar').css({
				'position': 'relative',
				'top': '0px',
				'width': ''
			}),
			$('#content').css({
				'margin-top': '0px'
			});
		}
		else if ($('#navbar').css('position') == 'fixed' && !($(this).scrollTop() < 60))
		{
			$('#navbar').css({
				'width': $(this).width()
			});
		}
	});
	$(window).resize(function(e) {
		if ($('#navbar').css('position') == 'fixed')
		{
			$('#navbar').css({
				'width': $(this).width()
			});
		}

		if (parseInt($('.content').css('margin-right')) > 15)
		{
			//console.log($('.content').css('margin-left'));
			$('.content').css({
				'margin-left':'auto'
			});
		}
		else {
			//console.log($('.content').css('margin-left') + " hi");
			$('.content').css({
				'margin-left':'15px'
			});
		}
		$("#update-well").css({
			"margin-left": $("#update-container").width()/2 - 250
		});
		if ($("#content").width()<756){
			$("#side").css({
				"height": "auto",
				"border-right": "none"
			}),
			$("#pic-column").css({
				"margin": "0 0 0 0"
			})
		} else {
			$("#side").css({
				"height": $("#test").height(),
				"border-right": "2px solid #7b7c7f"
			}),
			$("#pic-column").css({
				"margin-left":"120px"
			})
		}
		
	});
	if (('{{form.non_field_errors}}'+'{{form.course_subject.errors}}'+'{{form.course_number.errors}}').length > 0)
		{
			$('#course-add').modal('show')
		};
		
	if ($("#content").width()<756){
		$("#side").css({
			"height": "auto",
			"border-right": "none"
		}),
		$("#pic-column").css({
			"margin": "0 0 0 0"
		})
	} else {
		$("#side").css({
			"height": $("#test").height(),
			"border-right": "2px solid #7b7c7f"
		}),
		$("#pic-column").css({
			"margin-left":"120px"
		})
	}
});
$(function () {
    $(".tool-tip").tooltip();
});