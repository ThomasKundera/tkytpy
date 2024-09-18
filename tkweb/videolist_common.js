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
  //mdm.appendChild(create_p(ytv.mostrecentme));
  mdm.appendChild(create_p(ytv.yid+" "+ytv.mostrecentme))
  const mds = document.createElement("div");
  const s="Number of comments: "
    +ytv.recordedcommentcount+"/"+ytv.commentcount;
  mds.appendChild(create_p(s));
  mds.setAttribute('style','width: 50%; background-color: '+getColor((parseInt(ytv.recordedcommentcount))/(parseInt(ytv.commentcount)+1.))); //  FIXME
  mdm.appendChild(mds);
  mdv.appendChild(mdm);


  div.appendChild(mdv);
}
