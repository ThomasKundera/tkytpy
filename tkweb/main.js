
function populate_comment(refdiv,tlc) {
  refdiv.innerHTML = "";

  const div = document.createElement("div");
  div.setAttribute('class','tidcomment');
  const p0 = document.createElement("p");
  p0.textContent=tlc.author
  div.appendChild(p0)
  const p1 = document.createElement("p");
  p1.innerHTML=tlc.text
  div.appendChild(p1)
  const ma0 = document.createElement("a");
  ma0.setAttribute('href',"/thread.html?tid="+tlc.cid)
  ma0.textContent="Thread"
  div.appendChild(ma0)
  const ma1 = document.createElement("a");
  ma1.setAttribute('href',"https://www.youtube.com/watch?v="+tlc.yid+"&lc="+tlc.cid);
  ma1.textContent="Online link";
  div.appendChild(ma1);
  refdiv.appendChild(div);
}


function populate_oldest_thread(obj) {
  const oldest_thread_div = document.querySelector("#oldestthreaddiv");
  populate_comment(oldest_thread_div,obj.tlc);
}

function populate_newest_thread(obj) {
  const newest_thread_div = document.querySelector("#newestthreaddiv");
  populate_comment(newest_thread_div,obj.tlc);
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

async function update_newest_thread_of_interest() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_newest_thread_of_interest" }')
    });
    const cidtext = await response.text();
    const cidjson=JSON.parse(cidtext);
    populate_newest_thread(cidjson);
  } catch (e) {
    console.error(e);
  }
}
// On document load
window.addEventListener("load", function() {
  update_oldest_thread_of_interest();
  update_newest_thread_of_interest();
});
