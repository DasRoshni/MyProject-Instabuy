var modal = document.getElementById('myModalReport');

// Get the button that opens the modal
var images = document.getElementsByClassName("zoom")
var i=0
for(var i = 0; i < images.length; i++){
    var btn=images[i]
    var modalImg = document.getElementById("img01");
    btn.onclick = function(){
        modal.style.display = "block";
        modalImg.src = this.src;
    }
}
