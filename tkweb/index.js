
function populate_comment(refdiv,tlc) {
  // Print tlc to console:
  console.log(tlc);

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
  ma0.textContent="Thread "
  div.appendChild(ma0)
  const ma1 = document.createElement("a");
  ma1.setAttribute('href',"https://www.youtube.com/watch?v="+tlc.yid+"&lc="+tlc.cid);
  ma1.textContent=" Online link";
  div.appendChild(ma1);
  const p2 = document.createElement("p");
  p2.textContent=tlc.cid
  div.appendChild(p2)
  const p3 = document.createElement("p");
  p3.textContent=tlc.yid
  div.appendChild(p3)

  refdiv.appendChild(div);
}


function populate_number_of_threads(obj) {
  const notdiv = document.querySelector("#nbthreads");
  notdiv.innerHTML = "";

  const p0 = document.createElement("p");
  p0.textContent="... and "+obj.nb+" more threads of interest..."
  notdiv.appendChild(p0)
}


function populate_oldest_threads(obj) {
  const oldest_thread_div = document.querySelector("#oldestthreaddiv");
  oldest_thread_div.innerHTML = "";
  for (const cmt of obj.tlist) {
    populate_comment(oldest_thread_div,cmt.tlc);
  }
}

function populate_newest_threads(obj) {
  const newest_thread_div = document.querySelector("#newestthreaddiv");
  newest_thread_div.innerHTML = "";
  for (const cmt of obj.tlist) {
    populate_comment(newest_thread_div,cmt.tlc);
  }
}

async function update_oldest_threads_of_interest() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_oldest_threads_of_interest" }')
    });
    const cidtext = await response.text();
     // Debug print the received text
     console.log(cidtext);

    const cidjson=JSON.parse(cidtext);
    populate_oldest_threads(cidjson);
  } catch (e) {
    console.error(e);
  }
}

async function update_newest_threads_of_interest() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_newest_threads_of_interest" }')
    });
    const cidtext = await response.text();
    const cidjson=JSON.parse(cidtext);
    populate_newest_threads(cidjson);
  } catch (e) {
    console.error(e);
  }
}

async function update_number_of_threads_of_interest() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_number_of_threads_of_interest" }')
    });
    const cidtext = await response.text();
    const cidjson=JSON.parse(cidtext);
   
    populate_number_of_threads(cidjson);
  } catch (e) {
    console.error(e);
  }
}

// On document load
window.addEventListener("load", function() {
  update_oldest_threads_of_interest();
  update_number_of_threads_of_interest();
  update_newest_threads_of_interest();
});
