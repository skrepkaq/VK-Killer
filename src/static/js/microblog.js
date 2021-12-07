const deletePost = document.getElementsByClassName("delete-post")
const pi = document.getElementById("photo_input")


window.addEventListener("load", function(){
    let objDiv = document.getElementById("posts-box");
    objDiv.scrollTop = objDiv.scrollHeight;
});


if (pi) {
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
}


for (let i = 0; i < deletePost.length; i++) {
    let deleteDivs = deletePost[i].children
    deleteDivs[0].addEventListener("click", () => {
        deleteDivs[0].classList.add('hide')
        deleteDivs[1].classList.remove('hide')
    });
}
