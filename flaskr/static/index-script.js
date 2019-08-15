$(document).ready(function () {
    //INDEX PAGE

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

    //https://www.w3schools.com/howto/howto_js_media_queries.asp

    //add listener to dynamically change column width
    function changeColumn(x) {
        if (x.matches) { // If media query matches
            $("#index-num-label").removeClass("col-sm-3")
            $("#index-num-label").addClass("col-sm-6")
            $("#index-num").removeClass("col-sm-9")
            $("#index-num").addClass("col-sm-6")

        } else {
            $("#index-num-label").removeClass("col-sm-6")
            $("#index-num-label").addClass("col-sm-3")
            $("#index-num").removeClass("col-sm-6 ")
            $("#index-num").addClass("col-sm-9")
        }
    }

    var width991 = window.matchMedia("(max-width: 991px)")
    changeColumn(width991) // Call listener function at run time
    width991.addListener(changeColumn) // Attach listener function on state changes

})

//loads html for exercise description when modal is opened
function openExerciseModal(id) {
    $.get("/exercise?id=" + id, function (data) {

        $("#exercise-description" + id).html(data);

    });
}