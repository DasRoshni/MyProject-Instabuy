var x = document.getElementById("demo");
var locationModal = document.getElementById('myModal');

function getLocation() {
    place=document.getElementById('autocomplete').value;
    if(place!="")
        document.getElementById("myBtn").innerHTML=place.substr(0, place.indexOf(','));
    locationModal.style.display = "none";
    }

function showPosition(position) {
    x.innerHTML="Latitude: " + position.coords.latitude +
    "<br>Longitude: " + position.coords.longitude;
}

var input = document.getElementById('autocomplete');
var autocomplete = new google.maps.places.Autocomplete(input,{types: ['(cities)']});
google.maps.event.addListener(autocomplete, 'place_changed', function(){
  var place = autocomplete.getPlace();
})

// When the user clicks the button, open the modal
var btn = document.getElementById("myBtn")
btn.onclick = function() {
    locationModal.style.display = "block";
}
