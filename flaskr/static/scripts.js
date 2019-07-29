// wait for page to load
$(document).ready(function () {

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




    // listen for number of exercises to create form
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
            $("#workoutName").addClass("is-invalid");
            $("#name-feedback").html("Workout name required");
            event.preventDefault();
            return false;
        } else {
            $("#workoutName").removeClass("is-invalid");
        };

        // check number of exercises
        if ($("#numberExercises").val() === "") {
            $("#numberExercises").addClass("is-invalid");
            $("#number-feedback").html("Number required");
            event.preventDefault();
            return false;
        } else {
            $("#numberExercises").removeClass("is-invalid");
        };
        // remove invalid class if exists on exercise
        $('.tt-input').each(function () {
            $(this).removeClass("is-invalid")
        });
        //check if name exists and is all alphabetical and if is visible
        $('.tt-input').each(function (i) {
            console.log($(this).val())
            if (!/[a-z]+/i.test($(this).val()) && $(this).is(":visible") ) {
                $(this).addClass("is-invalid");
                $("#ex-feedback" + i).html("Input valid exercise name");
                event.preventDefault();
                return false;
            }
        });


    });

    //use typeahead for search results on create workout
    $(".search-bar").typeahead({
        highlight: true,
        minLength: 0
    },
    {
        display: "name" ,
        name: "exerciseSearch",
        source: searchExercises,
        limit: 35
        })



});


//button functions



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
//typeahead function to generate list of workouts asyn
function searchExercises(query, syncResults, asyncResults) {
    let param = {
        query: query
    }
    $.getJSON("/search", param, function (data) {
        asyncResults(data);
    })

}