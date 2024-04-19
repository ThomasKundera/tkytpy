function populate_oldest_thread(obj) {
  const oldest_thread_div = document.querySelector("#oldestthreaddiv");
  otdiv.innerHTML = "";
  const tlc = obj.tlc;

  const olddiv = document.createElement("div");
  olddiv.setAttribute('class','commentthread');

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
  ot.appendChild(mvldiv);
}





async function update_oldest_thread_of_interest() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_oldest_thread_of_interest" }')
    });
    const cidtext = await response.text();
    const cidjson=JSON.parse(cidtext);
    populate_oldest_thread(cidjson);
  } catch (e) {
    console.error(e);
  }
}


// On document load
window.addEventListener("load", function() {
  update_oldest_thread_of_interest();
});
