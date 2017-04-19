console.log('hello!');


var nb_module=1;

function removeModule(){
  if(nb_module>1){
    var module= document.getElementById('module'+nb_module);
    var modules= document.getElementById('modules').removeChild(module);
    nb_module+=-1;
    document.getElementById('nb_module').setAttribute("value",nb_module)

  }

}

function createModule(){

  nb_module+=1;
  var nbMod=document.getElementById('nb_module').setAttribute("value",nb_module)

  var modules= document.getElementById('modules');
  var module= document.getElementById('module1');
  var new_module= module.cloneNode(true);
  new_module.setAttribute('id','module'+nb_module);

  var legend=new_module.getElementsByTagName("legend")[0];
  legend.innerHTML="Module "+nb_module+" :";

  var labelModule=new_module.getElementsByTagName("label")[0];
  labelModule.setAttribute('for','id_module_'+nb_module);
  labelModule.innerHTML="Module "+nb_module+" :";

  var labelMedia=new_module.getElementsByTagName("label")[1];
  labelMedia.setAttribute('for','id_module_'+nb_module);
  labelMedia.innerHTML="Media "+nb_module+" :";

  var inputModule=new_module.getElementsByTagName("input")[0];
  inputModule.setAttribute('id','id_module_'+nb_module);
  inputModule.setAttribute('name','module_'+nb_module);

  var inputMedia=new_module.getElementsByTagName("input")[1];
  inputMedia.setAttribute('id','id_media_'+nb_module);
  inputMedia.setAttribute('name','media_'+nb_module);


  modules.appendChild(new_module);

  //var txt= document.createTextNode("{{formMod.as_p}}");
  //doc.appendChild(txt);
}
