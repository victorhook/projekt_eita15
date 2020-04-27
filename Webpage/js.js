

  let counter=0;
       var swiper = new Swiper('.swiper-container', {
    effect: 'cube',
    loop: true,
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: false,
    },
    on: {
      slideNextTransitionEnd: function (){
          counter++;
          if(counter>3){
            counter=1;
          }
          console.log(counter);
          if(counter==1){
            document.getElementById("text1").style.display = "block";
            document.getElementById("text2").style.display = "none";
            document.getElementById("text3").style.display = "none";          }
          else if(counter==2){
            document.getElementById("text1").style.display = "none";
            document.getElementById("text2").style.display = "block";
            document.getElementById("text3").style.display = "none";
          }
          else{
            document.getElementById("text1").style.display = "none";
            document.getElementById("text2").style.display = "none";
            document.getElementById("text3").style.display = "block";
          }
        },
        slidePrevTransitionEnd: function(){
          counter--;
          if(counter<1){
            counter=3;
          }
          console.log(counter);
          if(counter==1){
            document.getElementById("text1").style.display = "block";
            document.getElementById("text2").style.display = "none";
            document.getElementById("text3").style.display = "none";          }
          else if(counter==2){
            document.getElementById("text1").style.display = "none";
            document.getElementById("text2").style.display = "block";
            document.getElementById("text3").style.display = "none";
          }
          else{
            document.getElementById("text1").style.display = "none";
            document.getElementById("text2").style.display = "none";
            document.getElementById("text3").style.display = "block";
          }
        },  
      }
  });

