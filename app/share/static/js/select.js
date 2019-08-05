// 下拉菜单js：第一份
window.onload=function() {
       var selBox= document.querySelector('.selBox');
       var selSpan= document.querySelector('.sel');
       var optionUL=document.querySelector('.options');
       var iconSan=document.querySelector('.san');
       var selOptions= document.querySelector('.options').childNodes;
       var selectedCode='0';
       var selBox2= document.querySelector('.selBox2');
       var selSpan2= document.querySelector('.sel2');
       var optionUL2=document.querySelector('.options2');
       var iconSan2=document.querySelector('.san2');
       var selOptions2= document.querySelector('.options2').childNodes;
       var selectedCode2='0';
       function getData() {
           $.ajax({
            url: "{{url_for('share.bireport_select', we_id='wxid_dmyhsfr6')}}",
            // url: "",
            data:{'c_type' : selectedCode, 'time_type' : selectedCode2},
            type: "GET",
            async: false,
            cache: false,
            success:function(result) {
                  var htmlData = "";
              for(var i=0;i<result['t_dic'].length;i++){
                  htmlData +='<div class="displayFlex con-data">'+
                                '<div class="flex1 bg1">'+result['t_dic'][i]['time']+'</div>'+
                                '<div class="flex1 bg2">'+result['t_dic'][i]['value']+'</div>'+
                            '</div>';
                  }
                  $(".title").siblings().remove();
                  $(".title").after(htmlData);
            },
            error:function() {

            }

           });
       }
       // 初始化时取数据
       //     getData();
           selBox.addEventListener('click',function(e) {
            optionUL2.style.display='none';
            iconSan2.className="san sanDown";
            if(optionUL.style.display=='block'){
              optionUL.style.display='none';
               iconSan.className="san sanDown";
              return;
            }
               optionUL.style.display='block';
               iconSan.className="san sanUp";
              e.stopPropagation();
           });
          var initOption=function() {
            for (var i = 0; i < selOptions.length; i++) {
                    if(selOptions[i].nodeName!='#text'){
                      selOptions[i].className="def";
                    }
                  };
           };
           for (var n = 0; n < selOptions.length; n++) {
             selOptions[n].addEventListener('click',function(e) {
                     initOption();
                     optionUL.style.display='none';
                     iconSan.className="san sanDown";
                     selectedCode=this.getAttribute('code');
                     selSpan.innerText=this.innerText;
                     this.className="selected";
                     // 取数据的方法
                     getData();
                     e.stopPropagation();
               });
           };

// 下拉菜单js：第2份
           //
           selBox2.addEventListener('click',function(e) {
             optionUL.style.display='none';
             iconSan.className="san sanDown";
            if(optionUL2.style.display=='block'){
              optionUL2.style.display='none';
               iconSan2.className="san2 sanDown";
              return;
            }
               optionUL2.style.display='block';
               iconSan2.className="san2 sanUp";
              e.stopPropagation();
           });
          var initOption2=function() {
            for (var i = 0; i < selOptions2.length; i++) {
                    if(selOptions2[i].nodeName!='#text'){
                      selOptions2[i].className="def";
                    }
                  };
           };
           for (var n = 0; n < selOptions2.length; n++) {
             selOptions2[n].addEventListener('click',function(e) {
                     initOption2();
                     optionUL2.style.display='none';
                     iconSan2.className="san2 sanDown";
                     selectedCode2=this.getAttribute('code');
                     selSpan2.innerText=this.innerText;
                     this.className="selected";
                     // 取数据的方法
                     getData();
                     e.stopPropagation();
               });
           };
           document.addEventListener('click', function(e) {
            optionUL.style.display='none';
            iconSan.className="san sanDown";
            optionUL2.style.display='none';
            iconSan2.className="san2 sanDown";
              e.stopPropagation();
           });
     }