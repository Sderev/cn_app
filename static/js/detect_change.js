
// must have url and is_home defined previously
// this script add a listener to the window and launch the preview update whenever an event is throw at it.
// The event comes from etherpad whenever a change is made into the pad. (thrown from collab_client.js -> handleMessageFromServer)

  var can_update = true;
  var waiting = false;

  // occur after we detect a change in the pad's content and 5 seconds has passed
  function setValue(){
    can_update=true;
    waiting=false;
    update_preview();
  }

  // update the iframe
  function update_preview(){
    console.log(is_home);
    if (is_home){
      convertir_home(url);
    }
    else{
      convertir_module(url);
    }
  }

  // occur after we detect a change in the pad's content
  // wait for 5 seconds, then update the preview in the other iframe
  function receiver(e) {
    if(!waiting){
     window.setTimeout("setValue()",5000);
     waiting=true;
    }
    if(can_update){
      can_update=false;
    }

  }

  // add the listener to the window
  function addlistener(){
    if (!window.addEventListener) {
       window.attachEvent('onmessage', receiver);
   } else {
       window.addEventListener('message', receiver, false);
   }
  }
