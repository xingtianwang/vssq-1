$(document).ready(function() {
			$('#fullpage').fullpage({
				anchors:  ['firstPage',  'secondPage',  '3rdPage','4thPage','5thPage','6thPage','7thPage','8thPage','9thPage'],
				navigation: true,
				navigationPosition: 'right',
				verticalCentered: false
			});
			 //返回顶部
		     var goTOTopFun=function(){
		      var fist_page=$("#fullpage>div:first").hasClass("active");
			    if(fist_page){
			    	$("#goTop").hide();
			    }else{
			    	$("#goTop").show();
			    }
		     };
		     if(navigator.userAgent.toUpperCase().indexOf("FIREFOX")>0){
		     	window.addEventListener("DOMMouseScroll",goTOTopFun);
		     }else{
		     	window.onmousewheel=goTOTopFun;
		     }
    		 //返回顶部按钮goTop点击事件
			$("#goTop").bind("click",function(){
				$("#fullpage").css({"transform":"translateY(0px)"});
				$("#fullpage>div:first").addClass("active fp-completely");
				$("#fp-nav a").removeClass('active');
				$("#fp-nav a:first").addClass('active');
				$("#fullpage>div:first").siblings("div").removeClass("active fp-completely");
				$(this).hide();
			});
		    //首屏向下按钮
			$("#next").bind("click",function(){
    		     $("#fp-nav a").eq(1).click();
			});
		});