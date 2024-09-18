
function populateVideoList(obj) {
  const videodiv = document.querySelector("#videodiv");
  videodiv.innerHTML = "";
  const ytvlist = obj.ytvlist;

  for (var i in Array.from(Array(10))) {
    const span=document.createElement("span");
    span.textContent=i
    span.setAttribute('style','background-color: '+getColor(i/10.));
    videodiv.appendChild(span);
  };

  const mvldiv = document.createElement("div");
  mvldiv.setAttribute('class','videolist');
  // Refresh metadata button
  const mdv = document.createElement("div");
  mdv.setAttribute('class','gcontrol');
  const mip = create_input('button','refreshallmetadata',"allmetadata")
  mip.value="refresh all metadata"
  mdv.appendChild(mip);
  const lbl = document.createElement("label");
  lbl.setAttribute('for',"all");
  mdv.appendChild(lbl);
  mdv.appendChild(mip);
  mvldiv.appendChild(mdv);


  yl=new Array()
  for (const ytv of ytvlist) {
    yl.push(ytv)
  }

  // Display all ytvlist, sorted by mostrecentme
  yl.sort(function(a,b) {
    if (a.mostrecentme == "None") {
      if (b.mostrecentme == "None") {
        return 0;
      };
      return -1;
    };
    if (b.mostrecentme == "None") {
      return 1;
    };

    if (a.mostrecentme == b.mostrecentme) {
      return 0;
    };
    if (a.mostrecentme>b.mostrecentme) {
      return 1;
    }
    return -1;
  });
  yl.reverse();
  //console.error("________________________________");
  // FIXME: add a filter for suspended videos
  // FIXME: add a filter for valid videos
  for (const ytv of yl) {
    populate_video(mvldiv,ytv)
  }
  videodiv.appendChild(mvldiv);
}


async function manage_buttons(evtype,loc) {
  //console.error(loc.target);
  if (!(loc.target && loc.target.nodeName == "INPUT")) {
    return;
  }
  button=loc.target;
  try {
    action=button.getAttribute("name");
    yid=button.getAttribute("data-id");
    request={
        "command":"video_action",
        "action":action,
        "yid": yid
    };
    if (evtype =='change') {
      if (action == 'suspended') {
        checked=button.checked;
        request.checked=checked
      };
      if (action == 'monitor') {
        value=button.value;
        request.value=value;
      };
      if (action == 'refresh') { return; };
    } else {
      if (action == 'suspended') { return; };
      if (action == 'monitor') { return; };
      if (action == 'refresh') {
        dummy=1;
      };
    };
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });
    update_video_list();
  } catch (e) {
    console.error(e);
  }
}


const area = document.querySelector("#videodiv");
// Take over form submission
area.addEventListener("change", function(loc) {
  manage_buttons('change',loc);
});
area.addEventListener("click", function(loc) {
  manage_buttons('click',loc);
});

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
    let inputytid = document.getElementById('ytid');
    inputytid.value = "";
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

// On document load
window.addEventListener("load", function() {
  update_video_list();
});
