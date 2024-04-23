function populate_thread(cid) {
  const thread_div = document.querySelector("#threaddiv");
  thread_div.innerHTML = "";
  const p0 = document.createElement("p");
  p0.textContent=cid
  thread_div.appendChild(p0);
}




async function update_thread(cid) {
  try {
    populate_thread(cid);
  } catch (e) {
    console.error(e);
  }
}


// On document load
window.addEventListener("load", function() {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  cid=urlParams.getAll('cid')
  update_thread(cid);
});
