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
