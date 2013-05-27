$(document).ready(function() {
	$("img.thumb").unveil();

	$('.contactform textarea').autosize();

	if (ml_show_disclaimer) {
		if ($.cookie('tos') != undefined) {
			$(".tos_buttons").hide();
		} else {
			if (document.location.href.indexOf(ml_disclaimer_page) == -1 ) {
				document.location.href = ml_disclaimer_page + "?next=" + encodeURIComponent(document.location.href);
			}

			$(".tos_buttons .agree").click(function() {
				$.cookie('tos', 'accepted', { 'expires': 365, 'path': '/' });

				next = $.url().param('next');
				if (!next) next = "/";

				document.location.href = next;
			});

			$(".tos_buttons .disagree").click(function() {
				document.location.href = "about:blank";
			});
		}
	} else {
		$(".tos_buttons").hide();
	}

	var interval_function;
	var focused_on_image = true;
	var current_loop_index = 0;

	$(".videos .video").mouseenter(function() {

		focused_on_image = false;

		var image = $(this).find(".thumb");

		var thumbs = image.attr("data-slides").split("|");
		thumbs.pop();

		if (thumbs.length < 1) return;

		$(thumbs).each(function(){
			(new Image()).src = this;
    	});

    	thumbs.push(image.attr("data-src"));

		function select_thumb_element() {
			if (current_loop_index > thumbs.length - 1) {
				current_loop_index = 0;
			}

			var image_for_return = thumbs[current_loop_index];

			current_loop_index++;

			return image_for_return;
		}

		interval_function = self.setInterval(function(){
			image.attr("src", select_thumb_element())
		}, 1000);

	}).mouseleave(function() {
		focused_on_image = false;
		current_loop_index = 0;

		clearInterval(interval_function);

		$(this).find(".thumb").attr("src", $(this).find(".thumb").attr("data-src"));
  	});

  	window.report_video_not_playing = function(id){
		$.ajax({
			method: "POST",
			url: "/" + ml_current_locale + "/report_video_not_playing/",
			data: { id: id }
		}).done(function(data){
			alert(data);
		});
	}
});