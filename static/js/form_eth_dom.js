
var url_base="p/";
var url_export="/export/txt";

var list_url=[];
var nb_module=1;

// Send an url in the iframe which generate the preview
function convertir()
{

	console.log(list_url);
  var url_b="/apercu_home/";
  var frameHome=document.getElementById("framehome");
  var frame=document.getElementById("frametest");

  frame.setAttribute("src",url_b+list_url[0]);
}

// Send an url in the iframe which generate the preview
function convertir_home(url)
{
  var url='/apercu_home/'+url;
  var frame=document.getElementById("frametest");

  frame.setAttribute("src",url);
}

function convertir_module(url)
{
  var url='/apercu_module/'+url;
  var frame=document.getElementById("frametest");

  frame.setAttribute("src",url);
}

// Generate a random string of nb_char characters
function random_string(nb_char)
{
  var list = new Array("a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9");
  var res ="";
  for(i = 0; i < nb_char; i++)
    res = res + list[Math.floor(Math.random()*list.length)];
  return res;
}

//Generate a random link using url_base and a definite number of random char
//The results is inserted into list_url
function generate_link(etherpad_url, nb_char, is_module){
  rand=random_string(nb_char);
  if(is_module){
    rand="module-"+rand;
  }
  else{
    rand="home-"+rand;
  }

	url=etherpad_url+url_base+rand;
	list_url.push(rand);
	return url;
}

//set a link using nb_char random char to a definite iframe (using id)
function give_link_to_iframe(etherpad_url, idFrame, idInput, nb_char, is_module){
	var frame = document.getElementById(idFrame);
	var input = document.getElementById(idInput);
	var link=""
	if(nb_module+1<=list_url.length){
		link = etherpad_url+url_base+list_url[nb_module];
	}
	else{
		link = generate_link(etherpad_url, nb_char, is_module);
	}
	frame.setAttribute("src",link);
	input.setAttribute("value",link+url_export);

}


//remove a module for eth_dom
function remove_mod_eth(){
  if(nb_module>1){
    var module= document.getElementById("module"+nb_module);
    var modules= document.getElementById("modules").removeChild(module);
    nb_module+=-1;
    document.getElementById("nb_module").setAttribute("value",nb_module)

  }
}

// Create a module
function create_mod_eth(etherpad_url){

  nb_module+=1;
  var nbMod=document.getElementById("nb_module").setAttribute("value",nb_module);
  var modules= document.getElementById("modules");
  var new_module= document.createElement("div");
  new_module.setAttribute("id","module"+nb_module);

  var legend=document.createElement("legend");
  legend.innerHTML="Module "+nb_module+" :";
  new_module.appendChild(legend);

	/*
  var labelModule= document.createElement("label");
  labelModule.setAttribute('for','id_module_'+nb_module);
  labelModule.innerHTML="Module "+nb_module+" :";
	*/
  var labelMedia=document.createElement("label");
  labelMedia.setAttribute("for","id_module_"+nb_module);
  labelMedia.innerHTML="Media "+nb_module+" :";


	var inputMedia=document.createElement("input");
  inputMedia.setAttribute("id","id_media_"+nb_module);
  inputMedia.setAttribute("name","media_"+nb_module);
  inputMedia.setAttribute("type","file");

  var iframeModule=document.createElement("iframe");
  iframeModule.setAttribute("id","framemod"+nb_module);
  iframeModule.setAttribute("name","framemod"+nb_module);
  iframeModule.setAttribute("src","");
	iframeModule.setAttribute("height","400");
	iframeModule.setAttribute("width","600");

  var inputModule=document.createElement("input");
  inputModule.setAttribute("id","id_module_"+nb_module);
  inputModule.setAttribute("name","module_"+nb_module);
  inputModule.setAttribute("type","hidden");

  var p1=document.createElement("p");
  var p2=document.createElement("p");

  p1.appendChild(iframeModule);
  p1.appendChild(inputModule);
  new_module.appendChild(p1);
  p2.appendChild(labelMedia);
  p2.appendChild(inputMedia);
  new_module.appendChild(p2);

  modules.appendChild(new_module);

  give_link_to_iframe(etherpad_url,"framemod"+nb_module, "id_module_"+nb_module, 10, true);

}
