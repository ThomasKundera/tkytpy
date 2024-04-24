function populate_comment(div,cmt) {
  const cdv = document.createElement("div");
  cdv.setAttribute('class','comment');
  const p0 = document.createElement("p");
  p0.textContent=cmt.author+" "+cmt.updated
  cdv.appendChild(p0)
  const p1 = document.createElement("p");
  p1.textContent=cmt.text
  cdv.appendChild(p1)
  div.appendChild(cdv);
}


function populate_thread(obj) {
  const thread_div = document.querySelector("#threaddiv");
  thread_div.innerHTML = "";
  const tlc = obj.tlc;

  const tlcdiv = document.createElement("div");
  tlcdiv.setAttribute('class','tlccomment');
  const p0 = document.createElement("p");
  p0.textContent=tlc.author+" "+tlc.updated
  tlcdiv.appendChild(p0)
  const p1 = document.createElement("p");
  p1.textContent=tlc.text
  tlcdiv.appendChild(p1)

  const ma1 = document.createElement("a");
  ma1.setAttribute('href',"https://www.youtube.com/watch?v="+tlc.yid+"&lc="+tlc.cid)
  ma1.textContent="Online link"
  thread_div.appendChild(tlcdiv);

  for (const cmt of obj.clist) {
    populate_comment(thread_div,cmt)
  }
}

async function update_thread(tid) {
  let jqr = { command: "get_thread", tid: tid };
  let tjqr = JSON.stringify(jqr);

  try {
      const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: (tjqr)
    });
    const threadtext = await response.text();
    const threadjson=JSON.parse(threadtext);
    populate_thread(threadjson);
  } catch (e) {
    console.error(e);
  }
}



// On document load
window.addEventListener("load", function() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  tid=urlParams.getAll('tid')[0]
  update_thread(tid);
});
