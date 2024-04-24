function populate_oldest_thread(obj) {
  const oldest_thread_div = document.querySelector("#oldestthreaddiv");
  oldest_thread_div.innerHTML = "";
  const tlc = obj.tlc;

  const olddiv = document.createElement("div");
  olddiv.setAttribute('class','tidcomment');
  const p0 = document.createElement("p");
  p0.textContent=tlc.author
  olddiv.appendChild(p0)
  const p1 = document.createElement("p");
  p1.textContent=tlc.text
  olddiv.appendChild(p1)
  const ma0 = document.createElement("a");
  ma0.setAttribute('href',"/thread.html?tid="+tlc.cid)
  ma0.textContent="Thread"
  olddiv.appendChild(ma0)
  const ma1 = document.createElement("a");
  ma1.setAttribute('href',"https://www.youtube.com/watch?v="+tlc.yid+"&lc="+tlc.cid)
  ma1.textContent="Online link"
  olddiv.appendChild(ma1)

  oldest_thread_div.appendChild(olddiv);
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
