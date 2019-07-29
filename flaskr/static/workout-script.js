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
    function changeColumn(x) {
        if (x.matches) { // If media query matches
            $(".workout-desc").removeClass("col-sm-3")
            $(".workout-desc").addClass("col-sm-6")
            $(".workout-item").removeClass("col-sm-9")
            $(".workout-item").addClass("col-sm-6")

        } else {
            $(".workout-desc").removeClass("col-sm-6")
            $(".workout-desc").addClass("col-sm-3")
            $(".workout-item").removeClass("col-sm-6 ")
            $(".workout-item").addClass("col-sm-9")
        }
    }

    var width991 = window.matchMedia("(max-width: 991px)")
    changeColumn(width991) // Call listener function at run time
    width991.addListener(changeColumn) // Attach listener function on state changes
})
