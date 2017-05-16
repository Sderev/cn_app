
console.log('hehehe');


function iframeRef( frameRef ) {
    return frameRef.contentWindow
        ? frameRef.contentWindow.document
        : frameRef.contentDocument
}


/*
$('#framehome').load(function() {
  alert("the iframe has been loaded");
});*/

function initDetect(){



  console.log('detect!!!');

  /*
  var inside = iframeRef( document.getElementById('framehome') );
  var test= inside.getElementById("innerdocbody");
  console.log(test);
  */



  $(document).ready(function () {
    //var iframe = $('framehome').contents();
    //console.log(iframe);
    //iframe



    var res=$('#framehome').contents().find("html").html();
    console.log(res);



  });

  /*
  console.log('detect!!!');
  //var framehome = document.getElementById("innerdocbody");

  //code before the pause
  setTimeout(function(){
    console.log('detect!!!');
    //do what you need here
    var innerdocbody = document.getElementById("innerdocbody");

    console.log();
    console.log(innerdocbody);

        textNode.addEventListener("DOMCharacterDataModified", function(evt) {
            alert("Text changed from '" + evt.prevValue + "' to '" + evt.newValue + "'");
          }, false);
  }, 5000);*/
}
