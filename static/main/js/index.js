/*$(function () {
    var src=$('.item-img').eq(1).attr('src');
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'blob'; //so you can access the response like a normal URL
    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
            var img = document.createElement('img');
            img.src = URL.createObjectURL(xhr.response); //create <img> with src set to the blob
            document.body.appendChild(img);
        }
    };
    xhr.open('GET',src, true);
    xhr.setRequestHeader('referer', 'http://hqporner.com');
    xhr.send();
});*/