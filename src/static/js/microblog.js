window.addEventListener("load", function(){
    let objDiv = document.getElementById("posts-box");
    objDiv.scrollTop = objDiv.scrollHeight;
});

pi = document.getElementById("photo_input")
pi.addEventListener('change', (event) => {
    if (pi.files && pi.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
          selectedImage = e.target.result;
          document.getElementById("preview_image").setAttribute('src', selectedImage);
      };
      reader.readAsDataURL(pi.files[0]);
    }
});