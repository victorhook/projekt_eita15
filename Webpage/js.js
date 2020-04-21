
<script src="swiper.js"></script>
var counter=0;
var swiper = new Swiper('.swiper-container', {
    effect: 'cube',
    loop: true,
    pagination: {
    el: '.swiper-pagination',
    type: 'bullets',
    clickable: true,
    on: {
      slideChange: function (){
        counter=counter+1
        console.log(counter)
      }
    }
  }
});

