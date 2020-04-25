

  let counter=0;
       var swiper = new Swiper('.swiper-container', {
    effect: 'cube',
    loop: true,
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true,
    },
    on: {
      slideNextTransitionEnd: function (){
          counter++;
          if(counter>3){
            counter=1;
          }
          console.log(counter);
          if(counter==1){
            document.getElementById("text12").style.visibility="hidden";
          }
        },
        slidePrevTransitionEnd: function(){
          counter--;
          if(counter<1){
            counter=3;
          }
          console.log(counter);
        },  
      }
  });

