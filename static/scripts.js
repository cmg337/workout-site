// wait for page to load
$(document).ready(function () {

    // check if random workout submission had valid options selected
    $("#workout_form").on("submit", function (event) {
        const ERROR_MESSAGE = "At least one box must be checked for each option"


        // map through each of the 4 groups of checkboxes
        Array.prototype.map.call(document.getElementsByClassName("selection-group"),
            function (elem) {
                // create checking variable and map through all checkboxes of section
                var checker = false;
                Array.prototype.map.call(elem.children[1].children,
                    function (child) {
                        if (child.firstElementChild.checked) {
                            checker = true;
                        }
                    })
                // if checker was not changed to true, show error
                if (!checker) {
                    event.preventDefault();
                    $('#alert').addClass('alert alert-danger');
                    $('#alert').html(ERROR_MESSAGE);
                    return false;
                }
            })
    });




    // check if register meets requirements before sending to server
    $("#register-form").on("submit", function (event) {
        // variable to check if form passes test
        var pass = true;

        //check if first name given
        if ($("#first-name").val() === "") {
            $("#first-name").addClass("form-control is-invalid");
            $("#first-feedback").html("First name required");
            pass = false;
        } else {
            $("#first-name").removeClass("form-control is-invalid");
            $("#first-name").addClass("form-control is-valid");
        }

        //check if last name given
        if ($("#last-name").val() === "") {
            $("#last-name").addClass("form-control is-invalid");
            $("#last-feedback").html("Last name required");
            pass = false;
        } else {
            $("#last-name").removeClass("form-control is-invalid");
            $("#last-name").addClass("form-control is-valid");
        }


        //check password length and characters
        // https://stackoverflow.com/questions/12763974/checking-for-uppercase-lowercase-numbers-with-jquery
        var upperCase = new RegExp('[A-Z]');
        var lowerCase = new RegExp('[a-z]');
        var numbers = new RegExp('[0-9]');

        if ($("#password").val().length < 8 || $("#password").val().match(upperCase) === null || $("#password").val().match(lowerCase) === null || $("#password").val().match(numbers) === null) {
            $("#password").addClass("form-control is-invalid");
            $("#reg-feedback").html("<ul><li>Password must be 8 characters long</li><li>Must contain 1 character from each A-Z, a-z, 0-9</li></ul>");
            pass = false;
        } else {
            $("#password").removeClass("form-control is-invalid");
            $("#password").addClass("form-control is-valid");
        }

        // if one inputs doesnt meet requirement, do not submit
        if (!pass) {
            event.preventDefault();
            return false;
        }

        //check if passwords match
        if ($("#password-check").val() != $("#password").val()) {
            $("#password-check").addClass("form-control is-invalid");
            $("#check-feedback").html("Passwords don't match");
            event.preventDefault();
            return false;
        }
    });




    // listen for number of workouts to create form
    $("#numberExercises").change(function () {

        var number = $("#numberExercises").val();
        for (const x of Array(parseInt(number)).keys()) {
            $("#exercise" + x).show();
            for (const y of Array(12 - number).keys()) {
                $("#exercise" + (11 - y)).hide();
            };
        };

    });

    // check validity of create workout form
    $("#create-form").on('submit', function (event) {

        //check if name given
        if ($("#workoutName").val() === "") {
            $("#workoutName").addClass("form-control is-invalid");
            $("#name-feedback").html("Workout name required");
            event.preventDefault();
            return false;
        };

        // check number of exercises
        if ($("#numberExercises").val() === "") {
            $("#numberExercises").addClass("form-control is-invalid");
            $("#number-feedback").html("Number required");
            event.preventDefault();
            return false;
        };


    });

    //use typeahead for search results on create workout
    $(".search-bar").typeahead({
        highlight: true,
        minLength: 1

    },
    {
        display: "name" ,
        name: "exerciseSearch",
        source: searchExercises,
        limit: 30
    })
});


//button functions

// save workouts
function saveWorkout(workout) {

    var workoutJSON = {
        'length': workout.length,
        'name': $('#random-workout-name').text()
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

// handle delete all button for workouts
function deleteAllWorkouts() {
    var form = '<form action="/saved" method="post" hidden> <input name="edit_type" value="deleteAll"/></form>';
    $(form).appendTo('body').submit();
}

// handle deleting workouts from database
function deleteWorkout(id) {
    // create form to submit
    var form = '<form action="/saved" method="post" hidden> <input name="edit_type" value="delete" /><input name="id" value="' + id + '"/></form>';
    $(form).appendTo('body').submit();
}

// handle editing workouts from database
function editWorkout(id) {
    // create form to submit
    var form = '<form action="/saved" method="post" hidden> <input name="edit_type" value="edit" /><input name="id" value="' + id + '"/></form>';
    $(form).appendTo('body').submit();
}

//loads html for exercise description when modal is opened
function openExerciseModal(id) {
    $.get("/exercise?id=" + id, function (data) {

        $("#exercise-description" + id).html(data);

    });
}

function searchExercises(query, syncResults, asyncResults) {
    let param = {
        query: query
    }
    $.getJSON("/search", param, function (data) {
        asyncResults(data);
    })

}