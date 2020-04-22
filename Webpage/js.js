

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

