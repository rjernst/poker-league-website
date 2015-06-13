function stopSignout() {
  $("#popupContent").fadeOut("fast", function() {
    var $kids = $("#signout").children(".signout_control");
    $kids.hide();
    $("#control").show();
    centerPopup(false);
    $("#popupContent").fadeIn("slow");
  });
}

function reopenTournament() {
  $("#popupContent").fadeOut("fast", function() {
    $("#close_error").hide();
    $("#control").hide();
    var $kids = $("#signout").children(".signout_control");
    $kids.show();
    centerPopup(false);
    $("#popupBackground").show();
    $("#popupContent").fadeIn("slow");
  });
}

function signoutPlayer() {
  var name = $("#playerName").val();
  $("#signout_error").html("");
  $("#playerName").val('');

  // check if player is already signed out
  l = document.getElementById('signout_list').childNodes;
  for (var i = 0; i < l.length; i++) {
    if (l[i].innerHTML == name) {
      $("#signout_error").html("Player already signed out.");
      return;
    }
  }

  args = {
    'player.name': name,
    'tournament.id': $("#tournId").val()
  };

  $.ajax({
    'url': '/manage/tournament/signout', 
    'data': args, 
    'type': "POST",
    'dataType': "text",
    'success': function(data) {
      addPlayerToList(data, true);
    },
    'error': function(req, status, error) {
      $("#signout_error").html("Error signing out. Please try again");
    }
  });
}

function addPlayerToList(name, visual) {
  //alert('Adding player ' + name + ' to list');
  var li = document.createElement('li');
  li.appendChild(document.createTextNode(name));
  document.getElementById('signout_list').appendChild(li);

  centerPopup(visual);

  var highhandOption = document.createElement('option');
  highhandOption.value = name;
  highhandOption.text = name;
  document.getElementById('highhandName').appendChild(highhandOption);

  var badbeatOption = document.createElement('option');
  badbeatOption.value = name;
  badbeatOption.text = name;
  document.getElementById('badbeatName').appendChild(badbeatOption);

  var bountyOption = document.createElement('option');
  bountyOption.value = name;
  bountyOption.text = name;
  document.getElementById('bountyName').appendChild(bountyOption);
}

function closeTournament() {
  $("#popupContent").fadeOut("fast", function() {
    //$("#progress").show();
    
    var highhandname = $("#highhandName").val();
    if (highhandname == "None") {
      //$("#progress").hide()
      $("#close_error").html("Who got the high hand?");
      $("#close_error").show();
      centerPopup(true, function() {
        $("#popupContent").fadeIn("fast");
      });
      return;
    }

     
    args = {
      'highhand.name': highhandname,
      'tournament.id': $("#tournId").val()
    };
    var bountyname = $("#bountyName").val();
    if (bountyname != "None") {
      args['bounty.name'] =  bountyname;
    }
    var badbeatname = $("#badbeatName").val();
    if (badbeatname != "None") {
      args['badbeat.name'] =  badbeatname;
    }

    $.ajax({
      'url': '/manage/tournament/close', 
      'data': args, 
      'type': "POST",
      'success': function(data) {
        window.location = '/tournaments';
      },
      'error': function(req, status, error) {
        $("#close_error").html("Error closing tournament. Please try again");
        centerPopup(true, function() {
          $("#popupContent").fadeIn("fast");
        });
      }
    });
  });
}

function newTournament() {
  // need to check these values exist 
  date = $("#tournamentDate").val();
  if (!date) {
    alert("no date object");
  }
  loc = $("#tournamentLocation").val();
  if (!loc) {
    alert("no location object");
  }
  
  args = {
    'tournament.date': date,
    'tournament.location': loc
  };

  $.ajax({
    'url': '/manage/tournament/add', 
    'data': args, 
    'type': "POST",
    'dataType': "text",
    'success': function(data) {
      //alert("New tournament added with id: " + data);
      editTournament(data);
    },
    'error': function(req, status, error) {
      alert("Ajax call failed!: " + status + ", " + error);
    }
  });
}

function deleteTournament(id, date) {
  args = {
    'id': id,
  };

  var res = confirm("Do you really want to delete tournament on " + date );

  if (!res) {
    return;
  }

  $.ajax({
    'url': '/manage/tournament/delete', 
    'data': args, 
    'type': "POST",
    'success': function(data) {
      window.location = data;
    },
    'error': function(req, status, error) {
      alert("Reset tournament failed!: " + status + ", " + error);
    }
  });
}

function resetTournament(id, date) {
  args = {
    'id': id,
  };

  var del = confirm("Do you really want to reset tournament on " + date);

  if (!del) {
    return;
  }

  $.ajax({
    'url': '/manage/tournament/reset', 
    'data': args, 
    'type': "POST",
    'success': function(data) {
      window.location = data;
    },
    'error': function(req, status, error) {
      alert("Delete tournament failed!: " + status + ", " + error);
    }
  });
}

function editTournament(id) {

  args = {
    'id': id,
  };

  $.ajax({
    'url': '/manage/tournament/edit', 
    'data': args, 
    'type': "GET",
    'success': function(data) {
      //parse json
      j = JSON.parse(data);
      $("#tournId").val(j.id);
      $("#playerName").autocomplete(j.players);

      $("#tournDate").html(j.date);
      $("#tournLoc").html(j.location);
      $("#signout_list").html('');      
      $("#bountyName").html('<option name="" value="None" />');
      $("#highhandName").html('<option name="" value="None" />');
      $("#badbeatName").html('<option name="" value="None" />');
      for (var i = 0; i < j.data.length; i++) {
        addPlayerToList(j.data[i]);
      }

      reopenTournament();
    },
    'error': function(req, status, error) {
      alert("Ajax call failed!: " + status + ", " + error);
    }
  });
}
