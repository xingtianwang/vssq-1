$(document).ready(function() {
			//导航条----适配移动端
			$('.cd-main-nav').on('click', function(event){
				if($(event.target).is('.cd-main-nav')) 
					$(this).children('ul').toggleClass('is-visible');
			});			 
		});