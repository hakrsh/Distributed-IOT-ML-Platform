const circles = document.querySelectorAll('.circle')

function fetchdata(){
    $.ajax({
            url: "/get_signal",
            type: 'GET',
            dataType: 'json',
            success: function(res) {
                console.log(res);
		changeLight(res)
            }
        });
}

function changeLight(cl) {
  circles[activeLight].className = 'circle';
  activeLight = cl;
  
  const currentLight = circles[activeLight]
  
  currentLight.classList.add(currentLight.getAttribute('color'));
}


$(document).ready(function(){
 changeLight(activeLight)
 setInterval(fetchdata,1000);
});
