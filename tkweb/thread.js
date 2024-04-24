function populate_thread(obj) {
  const thread_div = document.querySelector("#threaddiv");
  thread_div.innerHTML = "";
  const p0 = document.createElement("p");
  p0.textContent=obj.tlc.cid
  thread_div.appendChild(p0);
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
