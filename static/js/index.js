$(function() {
  // import other js files
  $.getScript("./static/js/modal.js");
  $.getScript("./static/js/navigation.js");

  // subscription success alert
  $("#sub-success-alert").fadeTo(3000, 500).slideUp(500, function(){
        $("#success-alert").slideUp(500);
  });

  // onchange functionality to allow for responsive search through tags
  $("#filter-search-input").on("input", function() {
    let searchVal = $(this).val();
    console.log(searchVal);
    $(".filter-item").each(function(index) {
      if ($(this).val().toLowerCase().includes(searchVal.toLowerCase())) {
        $(this).parent().css("display", "");
      } else {
        $(this).parent().css("display", "none");
      }
    });
  });

  // test ajax post
  $("#myImage").click(function() {
    //if $(this).val() {
      //    $.post("./templates/show,
    console.log('click');
    $("#myModalReport").css("display", "block");
    $.get("./templates/index.html", function(data) {
      $("myModalReport").html(data).fadeIn();
    });
  });

  // location stuff
  var x = document.getElementById("demo");

  function getLocation() {
     if (navigator.geolocation) {
         navigator.geolocation.watchPosition(showPosition);
     } else {
         x.innerHTML = "Geolocation is not supported.";}
     }

  function showPosition(position) {
     x.innerHTML="Latitude: " + position.coords.latitude +
     "<br>Longitude: " + position.coords.longitude;
  autocomplete(document.getElementById("myInput"), countries);
  }

  // When the user clicks anywhere outside the modals, close them
  $(window).click( (event) => {
    let modals = Array.from($(".modal"));
    if (modals.includes(event.target)) {
          $(event.target).css("display", "none");
      }
  });

  // Close modal when you click the X
  $("span").click(() => {
    let modal = $("#myModal")[0]
    modal.style.display = "none";
  })
});
