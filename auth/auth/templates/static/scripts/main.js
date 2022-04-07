function displayFaculty() {
    var d1 = document.getElementById("profilesHeading");
    var d2 = document.getElementById("facultyProfiles");
    var d3 = document.getElementById("phdProfiles");
    var d4 = document.getElementById("alumniProfiles");
    d1.innerHTML = "Faculty";
    d2.style.display = "block";
    d3.style.display = "none";
    d4.style.display = "none";
}

function displayStudents() {
    var d1 = document.getElementById("profilesHeading");
    var d2 = document.getElementById("facultyProfiles");
    var d3 = document.getElementById("phdProfiles");
    var d4 = document.getElementById("alumniProfiles");
    d1.innerHTML = "Students"
    d2.style.display = "none";
    d3.style.display = "block";
    d4.style.display = "none";
}

function displayAlumni() {
    var d1 = document.getElementById("profilesHeading");
    var d2 = document.getElementById("facultyProfiles");
    var d3 = document.getElementById("phdProfiles");
    var d4 = document.getElementById("alumniProfiles");
    d1.innerHTML = "Alumni"
    d2.style.display = "none";
    d3.style.display = "none";
    d4.style.display = "block";
}


function changeBGTheme() {
    console.log("change theme called");
    var navColor = window.prompt("Enter navbar color: ");
    console.log(navColor);
    var navDiv = document.getElementsByClassName("navbar")[0];
    var footyDiv = document.getElementsByClassName("footy2")[0];
    var bgButton = document.getElementById("changeBackgroundButton");
    var colorButton = document.getElementById("changeColorButton");
    var newsButton = document.getElementById("toggleNewsRoll");

    navDiv.style.backgroundColor = navColor;
    footyDiv.style.backgroundColor = navColor;
    bgButton.style.backgroundColor = navColor;
    colorButton.style.backgroundColor = navColor;
    newsButton.style.backgroundColor = navColor;
}

function changeColorTheme() {
    console.log("change theme called");
    var navColor = window.prompt("Enter navbar text color: ");
    console.log(navColor);
    var navDiv = document.getElementsByClassName("navText");
    var footyDiv = document.getElementsByClassName("footy2")[0];
    var bgButton = document.getElementById("changeBackgroundButton");
    var colorButton = document.getElementById("changeColorButton");
    var newsButton = document.getElementById("toggleNewsRoll");

    for (var i = 0, max = navDiv.length; i < max; i++) {
        navDiv[i].style.color = navColor;
    }
    footyDiv.style.color = navColor;
    bgButton.style.color = navColor;
    colorButton.style.color = navColor;
    newsButton.style.color = navColor;
}

let flag = 1;

function hideNewsRoll() {
    var news = document.getElementsByClassName("news-slider")[0];
    if (flag == 1) {
        news.style.display = "none";
        flag = 0;
    } else {
        news.style.display = "block";
        flag = 1;
    }
    console.log(news);
}

// function clickCounter() {
//     if (typeof(Storage) !== "undefined") {
//         if (sessionStorage.clickcount) {
//             sessionStorage.clickcount = Number(sessionStorage.clickcount) + 1;
//         } else {
//             sessionStorage.clickcount = 1;
//         }
//         document.getElementById("result").innerHTML = "You have clicked the button " + sessionStorage.clickcount + " time(s) in this session.";
//     } else {
//         document.getElementById("result").innerHTML = "Sorry, your browser does not support web storage...";
//     }
// }

function magnify(imgID, zoom) {
    var img, glass, w, h, bw;
    img = document.getElementById(imgID);
    /*create magnifier glass:*/
    glass = document.createElement("DIV");
    glass.setAttribute("class", "img-magnifier-glass");
    /*insert magnifier glass:*/
    img.parentElement.insertBefore(glass, img);
    /*set background properties for the magnifier glass:*/
    glass.style.backgroundImage = "url('" + img.src + "')";
    glass.style.backgroundRepeat = "no-repeat";
    glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
    bw = 3;
    w = glass.offsetWidth / 2;
    h = glass.offsetHeight / 2;
    /*execute a function when someone moves the magnifier glass over the image:*/
    glass.addEventListener("mousemove", moveMagnifier);
    img.addEventListener("mousemove", moveMagnifier);
    /*and also for touch screens:*/
    glass.addEventListener("touchmove", moveMagnifier);
    img.addEventListener("touchmove", moveMagnifier);

    function moveMagnifier(e) {
        var pos, x, y;
        /*prevent any other actions that may occur when moving over the image*/
        e.preventDefault();
        /*get the cursor's x and y positions:*/
        pos = getCursorPos(e);
        x = pos.x;
        y = pos.y;
        /*prevent the magnifier glass from being positioned outside the image:*/
        if (x > img.width - (w / zoom)) { x = img.width - (w / zoom); }
        if (x < w / zoom) { x = w / zoom; }
        if (y > img.height - (h / zoom)) { y = img.height - (h / zoom); }
        if (y < h / zoom) { y = h / zoom; }
        /*set the position of the magnifier glass:*/
        glass.style.left = (x - w) + "px";
        glass.style.top = (y - h) + "px";
        /*display what the magnifier glass "sees":*/
        glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
    }

    function getCursorPos(e) {
        var a, x = 0,
            y = 0;
        e = e || window.event;
        /*get the x and y positions of the image:*/
        a = img.getBoundingClientRect();
        /*calculate the cursor's x and y coordinates, relative to the image:*/
        x = e.pageX - a.left;
        y = e.pageY - a.top;
        /*consider any page scrolling:*/
        x = x - window.pageXOffset;
        y = y - window.pageYOffset;
        return { x: x, y: y };
    }
}

function addPublication() {

    let tableRef = document.getElementById("pubTable1");
    let newRow = tableRef.insertRow(-1);

    var title = window.prompt("Enter Title: ");
    var paperURL = window.prompt("Enter Scholar URL: ");
    var citations = window.prompt("Enter Citations: ");
    var year = window.prompt("Enter Year: ");
    let newText = document.createTextNode('New bottom row');


    let cell1 = newRow.insertCell(0);
    var a = document.createElement('a');
    let cell1Text = document.createTextNode(title);
    a.innerHTML = title;
    a.setAttribute('href', paperURL);
    cell1.appendChild(a);

    let cell2 = newRow.insertCell(1);
    let cell2Text = document.createTextNode(citations);
    cell2.classList.add("alignCenter");
    cell2.appendChild(cell2Text);

    let cell3 = newRow.insertCell(2);
    let cell3Text = document.createTextNode(year);
    cell3.classList.add("alignCenter");
    cell3.appendChild(cell3Text);

}

function addPublication2() {

    let tableRef = document.getElementById("pubTable2");
    let newRow = tableRef.insertRow(-1);

    var title = window.prompt("Enter Title: ");
    var paperURL = window.prompt("Enter Scholar URL: ");
    var citations = window.prompt("Enter Citations: ");
    var year = window.prompt("Enter Year: ");
    let newText = document.createTextNode('New bottom row');


    let cell1 = newRow.insertCell(0);
    var a = document.createElement('a');
    let cell1Text = document.createTextNode(title);
    a.innerHTML = title;
    a.setAttribute('href', paperURL);
    cell1.appendChild(a);

    let cell2 = newRow.insertCell(1);
    let cell2Text = document.createTextNode(citations);
    cell2.classList.add("alignCenter");
    cell2.appendChild(cell2Text);

    let cell3 = newRow.insertCell(2);
    let cell3Text = document.createTextNode(year);
    cell3.classList.add("alignCenter");
    cell3.appendChild(cell3Text);

}

function addPublication3() {

    let tableRef = document.getElementById("pubTable3");
    let newRow = tableRef.insertRow(-1);

    var title = window.prompt("Enter Title: ");
    var paperURL = window.prompt("Enter Scholar URL: ");
    var citations = window.prompt("Enter Citations: ");
    var year = window.prompt("Enter Year: ");
    let newText = document.createTextNode('New bottom row');


    let cell1 = newRow.insertCell(0);
    var a = document.createElement('a');
    let cell1Text = document.createTextNode(title);
    a.innerHTML = title;
    a.setAttribute('href', paperURL);
    cell1.appendChild(a);

    let cell2 = newRow.insertCell(1);
    let cell2Text = document.createTextNode(citations);
    cell2.classList.add("alignCenter");
    cell2.appendChild(cell2Text);

    let cell3 = newRow.insertCell(2);
    let cell3Text = document.createTextNode(year);
    cell3.classList.add("alignCenter");
    cell3.appendChild(cell3Text);

}

function addPublication4() {

    let tableRef = document.getElementById("pubTable4");
    let newRow = tableRef.insertRow(-1);

    var title = window.prompt("Enter Title: ");
    var paperURL = window.prompt("Enter Scholar URL: ");
    var citations = window.prompt("Enter Citations: ");
    var year = window.prompt("Enter Year: ");
    let newText = document.createTextNode('New bottom row');


    let cell1 = newRow.insertCell(0);
    var a = document.createElement('a');
    let cell1Text = document.createTextNode(title);
    a.innerHTML = title;
    a.setAttribute('href', paperURL);
    cell1.appendChild(a);

    let cell2 = newRow.insertCell(1);
    let cell2Text = document.createTextNode(citations);
    cell2.classList.add("alignCenter");
    cell2.appendChild(cell2Text);

    let cell3 = newRow.insertCell(2);
    let cell3Text = document.createTextNode(year);
    cell3.classList.add("alignCenter");
    cell3.appendChild(cell3Text);

}

function getRows() {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("get", "response", true);
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            showResult(this);
        }
    };
    xmlhttp.send(null);
}

function displayLoader() {
    let obj = document.getElementsByClassName("holds-the-iframe")[0]
    obj.style.display = "block";
    obj.style.background = "url(../images/1_5ngZiNtGMrp_xmZHxSvJ0g.gif) center center no-repeat"
    console.write(obj)
}

function hideLoader() {
    let obj = document.getElementsByClassName("holds-the-iframe")[0]
    obj.style.background = "none";
    console.log(obj)
        // await sleep(5 * 1000);
        // obj.style.display = "none";
}
