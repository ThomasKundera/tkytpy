function populateVideoList(obj) {
  const videodiv = document.querySelector("#videodiv");
  videodiv.innerHTML = "";
  const ytvlist = obj.ytvlist;

  const mvldiv = document.createElement("div");
  mvldiv.setAttribute('class','videolist');
  for (const ytv of ytvlist) {
    const mdv = document.createElement("div");
    mdv.setAttribute('class','video');

    const ma1 = document.createElement("a");
    ma1.setAttribute('href',"https://www.youtube.com/watch?v="+ytv.yid)
    const mi=document.createElement("img");
    mi.setAttribute('src',ytv.thumb_url_s);
    mi.setAttribute('width',"120");
    mi.setAttribute('height',"90");
    ma1.appendChild(mi);
    mdv.appendChild(ma1);

    const ma2 = document.createElement("a");
    ma2.textContent = ytv.title;
    ma2.setAttribute('href',"/video.html?yid="+ytv.yid)
    mdv.appendChild(ma2)

    const mdc = document.createElement("div");
    mdc.setAttribute('class','vcontrol');

    const mip = document.createElement("input");
    mip.setAttribute('type','checkbox');
    mip.setAttribute('id',"vmonitor");
    mip.setAttribute('onclick',"monitor_video()");

    mdc.appendChild(mip);
    mdv.appendChild(mdc)

    mvldiv.appendChild(mdv)
  }
  videodiv.appendChild(mvldiv);
}


const form = document.querySelector("#addytvideo");

async function add_video() {
  // Associate the FormData object with the form element
  const formData = new FormData(form);
  formData.set('command', 'add_video')

  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify((Object.fromEntries(formData)))
    });
    update_video_list()
  } catch (e) {
    console.error(e);
  }
}

// Take over form submission
form.addEventListener("submit", (event) => {
  event.preventDefault();
  add_video();
});

async function update_video_list() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_video_list" }')
    });
    const yidtext = await response.text();
    const yidjson=JSON.parse(yidtext);
    populateVideoList(yidjson);

  } catch (e) {
    console.error(e);
  }
}


// Take over form submission
form.addEventListener("submit", (event) => {
  event.preventDefault();
  add_video();
});

async function update_video_list() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_video_list" }')
    });
    const yidtext = await response.text();
    const yidjson=JSON.parse(yidtext);
    populateVideoList(yidjson);

  } catch (e) {
    console.error(e);
  }
}

// On document load
window.addEventListener("load", function() {
  update_video_list();
});
