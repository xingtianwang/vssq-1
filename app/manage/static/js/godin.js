$(document).ready(function(){
    $('a#clickCaptcha').click(function() {
       $("#captcha_img").attr("src", "/vssq/auth/captcha?d="+Math.random());
    });
    $('#start_time_picker').datetimepicker(
    {
            format: 'YYYY-MM-DD HH:mm:ss'
     });
    $('#end_time_picker').datetimepicker(
    {
        format: 'YYYY-MM-DD HH:mm:ss'
    });
    $('#date_picker').datetimepicker(
    {
        format: 'YYYY-MM-DD'
    });
    $('#start_date_picker').datetimepicker(
    {
        format: 'YYYY-MM-DD'
    });
    $('#end_date_picker').datetimepicker(
    {
        format: 'YYYY-MM-DD'
    });


    $(function(){
        $(".form-count").blur(function(){
            var unit_price, total_price, total_count

            if ($(this).attr("name")=="unit_price"){
                unit_price=$(this).val();
                total_price=$("#total_price").val();
            }
            if ($(this).attr("name")=="total_price"){
                total_price=$(this).val();
                unit_price=$("#unit_price").val();
            }
            if (unit_price != 0){
                total_count = total_price/unit_price;
                $("#total_count").val(Math.round(total_count));
            }
        })
    })
    $(function(){
        $(".form_pay_price").blur(function(){
            var price, common_discount, gold_discount, discount, pay_price

            if ($(this).attr("name")=="price"){
                price=$(this).val();
                common_discount=$("#common_discount").val();
                gold_discount=$("#gold_discount").val();
                discount=$("#discount").val();

                pay_price = price*common_discount;
                $("#pay_price").val(pay_price.toFixed(2));
                pay_price = price*gold_discount;
                $("#gold_pay_price").val(pay_price.toFixed(2));
                pay_price = price*discount;
                $("#platinum_pay_price").val(pay_price.toFixed(2));
            }
            if ($(this).attr("name")=="common_discount"){
                discount=$(this).val();
                price=$("#price").val();
                pay_price = price*discount;
                $("#pay_price").val(pay_price.toFixed(2));
            }
            if ($(this).attr("name")=="gold_discount"){
                discount=$(this).val();
                price=$("#price").val();
                pay_price = price*discount;
                $("#gold_pay_price").val(pay_price.toFixed(2));
            }
            if ($(this).attr("name")=="discount"){
                discount=$(this).val();
                price=$("#price").val();
                pay_price = price*discount;
                $("#platinum_pay_price").val(pay_price.toFixed(2));
            }



        })
    })
    $(function() {
        //全选和全部选按钮事件
        $("#checkAll").click(function() {
                $("input[name=subBox]").each(function(index){
                    if($("#checkAll").prop("checked")==true){
                      $(this).prop("checked",true);
                    }else{                                                                                                                                                                                         
                      $(this).prop("checked",false);
                    }   
                }); 
        })  
          //单点每个复选框到全选中
        $("input[name=subBox]").click(function(){
                if($("input[name=subBox]:checked").length==$("input[name=subBox]").length){
                   $("#checkAll").prop("checked",true);
                }else{
                   $("#checkAll").prop("checked",false);
                }   
        }); 
    }) 
});
