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

function create_p(textcontent) {
  const p=document.createElement("p");
  p.textContent =textcontent;
  return p;
}

function getColor(value){
    //value from 0 to 1
    var hue=(value*120).toString(10); //hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}
