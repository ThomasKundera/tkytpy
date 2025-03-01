function populate_comment(div, cmt) {
  const cdv = document.createElement("div");
  cdv.setAttribute('class', 'comment');

  const cmdv = document.createElement("div");
  cmdv.setAttribute('class', 'commentmeta');
  const p0 = document.createElement("p");
  p0.textContent = cmt.author
  cmdv.appendChild(p0)
  const ma1 = document.createElement("a");
  ma1.setAttribute('href', "https://www.youtube.com/watch?v=" + cmt.yid + "&lc=" + cmt.cid)
  ma1.textContent = cmt.updated
  cmdv.appendChild(ma1)
  cdv.appendChild(cmdv);

  const ctdv = document.createElement("div");
  ctdv.setAttribute('class', 'commenttext');
  const p2 = document.createElement("p");
  p2.innerHTML = cmt.text
  ctdv.appendChild(p2)
  cdv.appendChild(ctdv);

  const frm = document.createElement("form");
  frm.setAttribute('id', cmt.cid);
  const bt1 = document.createElement("button");
  bt1.setAttribute('name', 'IgnoreBefore');
  bt1.setAttribute('type', 'button');
  bt1.setAttribute('value', cmt.cid);
  bt1.textContent = "Ignore Before"
  frm.appendChild(bt1)
  cdv.appendChild(frm)
  div.appendChild(cdv);
}

function populate_top_buttons(div, tlc) {
  const tbd = document.createElement("div");
  const mip = create_input('button', 'update', tlc.cid)
  mip.setAttribute('value', "Update Thread");
  tbd.appendChild(mip);
  const mip2 = create_input('button', 'suspend_1w', tlc.cid)
  mip2.setAttribute('value', "Suspend a week");
  tbd.appendChild(mip2);
  const mip3 = create_input('button', 'suspend_1d', tlc.cid)
  mip3.setAttribute('value', "Suspend a day");
  tbd.appendChild(mip3);
  div.append(tbd);
}


function populate_thread(obj) {
  const thread_div = document.querySelector("#threaddiv");
  thread_div.innerHTML = "";
  const tlc = obj.tlc;

  populate_top_buttons(thread_div, tlc);

  populate_comment(thread_div, tlc);
  for (const cmt of obj.clist) {
    populate_comment(thread_div, cmt);
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
    const threadjson = JSON.parse(threadtext);
    populate_thread(threadjson);
  } catch (e) {
    console.error(e);
  }
}

async function manage_buttons(loc) {
  if (!(loc.target && (
    loc.target.nodeName == "BUTTON" || loc.target.nodeName == "INPUT"))) {
    return;
  }

  if (loc.target.nodeName == "BUTTON") {
    request = {
      "command": "set_ignore_from_comment",
      "cid": loc.target.getAttribute("value")
    };
  } else if (loc.target.nodeName == "INPUT") {
    if (loc.target.getAttribute("name") == 'update') {
      request = {
        "command": "force_refresh_thread",
        "tid": loc.target.getAttribute("data-id")
      };
    } else if (loc.target.getAttribute("name") == 'suspend_1w') {
      request = {
        "command": "suspend_thread",
        "tid": loc.target.getAttribute("data-id"),
        "duration": 7
      };
    } else if (loc.target.getAttribute("name") == 'suspend_1d') {
      request = {
        "command": "suspend_thread",
        "tid": loc.target.getAttribute("data-id"),
        "duration": 1
      };
    }
  }
  try {
    const response = await fetch("http://localhost:8000/post", {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });
  } catch (e) {
    console.error(e);
  }
}

const area = document.querySelector("#threaddiv");

// Take over form submission
area.addEventListener("click", function (loc) {
  manage_buttons(loc);
});




// On document load
window.addEventListener("load", function () {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  tid = urlParams.getAll('tid')[0]
  update_thread(tid);
});
