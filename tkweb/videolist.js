function create_a(href,textcontent) { // FIXME
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
  //console.log(ytv.yid);
  console.error(ytv.mostrecentme);
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

  const mdi = document.createElement("div");
  mdi.setAttribute('class',"vmignature");

  const mi=document.createElement("img");
  mi.setAttribute('src',ytv.thumb_url_s);
  mi.setAttribute('width',"120");
  mi.setAttribute('height',"90");
  const a1 = create_a("https://www.youtube.com/watch?v="+ytv.yid,"");
  a1.appendChild(mi);
  mdi.appendChild(a1);
  mdv.appendChild(mdi);

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

  const br1 = document.createElement("br");
  mdc.appendChild(br1);

  const mip2 = create_input('range','monitor',ytv.yid);
  mip2.setAttribute('min',0);
  mip2.setAttribute('max',10);
  mip2.setAttribute('value',parseInt(ytv.monitor));
  mdc.appendChild(mip2);
  const lbl2 = document.createElement("label");
  lbl2.setAttribute('for',mip2.getAttribute('id'));
  mdc.appendChild(lbl2);

  const br2 = document.createElement("br");
  mdc.appendChild(br2);

  const mip3 = create_input('button','refresh',ytv.yid)
  mip3.value="refresh"
  mdc.appendChild(mip3);
  const lbl3 = document.createElement("label");
  lbl3.setAttribute('for',mip3.getAttribute('id'));
  mdc.appendChild(lbl3);

  mdv.appendChild(mdc);


  const mdm = document.createElement("div");
  mdm.appendChild(create_a("/video.html?yid="+ytv.yid,ytv.title));
  //if (! ytv.mostrecentme) {
  //  ytv.mostrecentme="None";
  //};
  mdm.appendChild(create_p(ytv.mostrecentme));
  //mdm.appendChild(create_p(ytv.yid)+" "+ytv.mostrecentme)
  const mds = document.createElement("div");
  const s="Number of comments: "
    +ytv.recordedcommentcount+"/"+ytv.commentcount;
  mds.appendChild(create_p(s));
  mds.setAttribute('style','width: 50%; background-color: '+getColor((parseInt(ytv.recordedcommentcount))/(parseInt(ytv.commentcount)+1.))); //  FIXME
  mdm.appendChild(mds);
  mdv.appendChild(mdm);


  div.appendChild(mdv);
}

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
