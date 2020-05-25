$(document).ready(function() {
  
  $('#text2').hide();
  $('#text3').hide();

  let page = 0;
  let last_img = 1;

  var swiper = new Swiper('.swiper-container', {
    effect: 'cube',
    loop: true,
    pagination: {
    el: '.swiper-pagination',
    type: 'bullets',
    clickable: false,
    },
    on : {
      slideChangeTransitionEnd: function (){
        // Query current image
        img = $('.swiper-slide-active').css('background-image').split('/');
        // Seperate image name from the whole url
        img = img[img.length - 1].split('.');
        // Seperate the image-number from the image name
        img = img[img.length - 2];
        // Get the image-number
        img = img[img.length - 1];

        // Hide old image-text
        $('#text' + last_img).hide();
        // Display the new one
        $('#text' + img).show();
        // Update the last-image text variable
        last_img = img;
      }
    }
  });
  

});

