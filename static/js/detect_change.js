
// must have url and is_home defined previously
// this script add a listener to the window and launch the preview update whenever an event is throw at it.
// The event comes from etherpad whenever a change is made into the pad. (thrown from collab_client.js -> handleMessageFromServer)

  var can_update = true;
  var waiting = false;

  function setValue(){
    can_update=true;
    waiting=false;
    update_preview();
  }

  function update_preview(){
    console.log(is_home);
    if (is_home){
      convertir_home(url);
    }
    else{
      convertir_module(url);
    }
  }

  function receiver(e) {
    if(!waiting){
     window.setTimeout("setValue()",5000);
     waiting=true;
    }
    if(can_update){
      can_update=false;
    }




  }

  function addlistener(){
    if (!window.addEventListener) {
       window.attachEvent('onmessage', receiver);
   } else {
       window.addEventListener('message', receiver, false);
   }
  }
