function create_a(href,textcontent) {
  const a=document.createElement("a");
  a.setAttribute('href',href);
  a.textContent =textcontent;
  return a;
}

function create_input(type,name,id) {
  input=document.createElement("input");
  input.setAttribute('type'   , type         );
  input.setAttribute('name'   , name         );
  input.setAttribute('id'     , name+"_"+id  );
  input.setAttribute('data-id', id           );
  return input;
}

function populate_video(div,ytv) {
  const mdv = document.createElement("div");
  cls='video';
  ytv.valid     = (ytv.valid.toLowerCase()     === "true");
  ytv.suspended = (ytv.suspended.toLowerCase() === "true");
  if (!ytv.valid) {
    cls=cls+" vnotvalid";
  } else if (ytv.suspended) {
    cls=cls+" vsuspended";
  }

  mdv.setAttribute('class',cls);

  const mi=document.createElement("img");
  mi.setAttribute('src',ytv.thumb_url_s);
  mi.setAttribute('width',"120");
  mi.setAttribute('height',"90");

  const a1 = create_a("https://www.youtube.com/watch?v="+ytv.yid,"");
  a1.appendChild(mi);
  mdv.appendChild(a1);

  mdv.appendChild(create_a("/video.html?yid="+ytv.yid,ytv.title));

  const mdc = document.createElement("div");
  mdc.setAttribute('class','vcontrol');

  const mip = create_input('checkbox','suspended',ytv.yid)
  mip.checked=ytv.suspended
  mdc.appendChild(mip);

  const lbl = document.createElement("label");
  lbl.setAttribute('for',mip.getAttribute('id'));
  if (mip.checked) lbl.textContent="Unsuspend";
  else lbl.textContent="Suspend";
  mdc.appendChild(lbl);

  const mip2 = create_input('range','monitor',ytv.yid);
  mip2.setAttribute('min',0);
  mip2.setAttribute('max',10);
  mip2.setAttribute('value',parseInt(ytv.monitor));
  mdc.appendChild(mip2);
  const lbl2 = document.createElement("label");
  lbl2.setAttribute('for',mip2.getAttribute('id'));
  mdc.appendChild(lbl2);

  mdv.appendChild(mdc);
  div.appendChild(mdv);
}

function populateVideoList(obj) {
  const videodiv = document.querySelector("#videodiv");
  videodiv.innerHTML = "";
  const ytvlist = obj.ytvlist;

  const mvldiv = document.createElement("div");
  mvldiv.setAttribute('class','videolist');
  for (const ytv of ytvlist) {
    populate_video(mvldiv,ytv)
  }
  videodiv.appendChild(mvldiv);
}

async function manage_buttons(loc) {
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
    if (action == 'suspended') {
      checked=button.checked;
      request.checked=checked
    };
    if (action == 'monitor') {
      value=button.value;
      request.value=value;
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
  manage_buttons(loc);
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
