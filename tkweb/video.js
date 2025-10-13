




// On document load
window.addEventListener("load", function () {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  tid = urlParams.getAll('yid')[0]
  update_threads(yid);
});
