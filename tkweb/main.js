async function update_main() {
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: ('{ "command": "get_main_stuff" }')
    });
    const yidtext = await response.text();
    const yidjson=JSON.parse(yidtext);
    // populateVideoList(yidjson);

  } catch (e) {
    console.error(e);
  }
}

// On document load
window.addEventListener("load", function() {
  update_main();
});
