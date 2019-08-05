// RANDOM WORKOUT PAGE SCRIPTS
// save randomely generated workout
function saveWorkout(workout) {

    var workoutJSON = {
        'length': workout.length,
        'name': $('#random-workout-name').val()
    };
    for (var exercise in workout) {
        workoutJSON[exercise] = workout[exercise]['id'];
    }

    $.post('/saveWorkout', workoutJSON, function (data) {
        if (data == 'true') {
            $('#saveWorkout').prop('disabled', true);
            $('#saveWorkout').html('Saved');
            $('#close-save-modal').click();
            $('#save-modal-btn').prop('disabled', true);
        } else {
            $('#saveWorkout').prop('disabled', true);
            $('#saveWorkout').html('Error');
            $('#saveWorkout').attr('class', 'btn btn-warning')
            $('#createAlert').show();
            $('#close-save-modal').click();
            $('#save-modal-btn').prop('disabled', true);
        }
    });
}

$(document).ready(function(){
    //add listener to dynamically change column width
     var changeColumn = function(x) {
        if (x.matches) { // If media query matches
            $(".workout-desc").removeClass("col-sm-3")
            $(".workout-desc").addClass("col-sm-7")

        } else {
            $(".workout-desc").removeClass("col-sm-7")
            $(".workout-desc").addClass("col-sm-3")
        }
    }

    var fitImages = function(x) {
        if (x.matches) {

        }
    }

    var width1200 = window.matchMedia("(max-width: 1200px)")
    var width991 = window.matchMedia("(max-width: 991px)")
    changeColumn(width1200) // Call listener function at run time
    width1200.addListener(changeColumn) // Attach listener function on state changes
})
