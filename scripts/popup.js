
var popupStatus = 0;

function centerPopup(animate, callback) {
  var windowWidth = document.documentElement.clientWidth;
  var windowHeight = document.documentElement.clientHeight;
  var popupHeight = $("#popupContent").height();
  var popupWidth = $("#popupContent").width();

  newLoc = {
    "position": "absolute",
    "top": windowHeight/2-popupHeight/2,
    "left": windowWidth/2-popupWidth/2
  };

  if (typeof animate != 'undefined' && animate) {
    if (typeof callback != 'undefined') { 
      $("#popupContent").animate(newLoc, "normal", callback);
    } else {
      $("#popupContent").animate(newLoc, "normal");
    }
  } else {
    $("#popupContent").css(newLoc);
  }

  // for IE 6
  $("#popupBackground").css({
    "height": windowHeight
  });
}

function showPopup() {
  if (popupStatus == 0) {
    centerPopup();
    $("#popupBackground").css({"opacity": "0.7"});
    $("#popupBackground").fadeIn("slow");
    $("#popupContent").fadeIn("slow");
    popupStatus = 1;
  }
}

function hidePopup() {
  if (popupStatus == 1) {
    $("#popupBackground").fadeOut("slow");
    $("#popupContent").fadeOut("slow");
    popupStatus = 0;
  }
}


