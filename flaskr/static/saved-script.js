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


//event listeners
$(document).ready(function () {

    //change nav into modal vice versa
    var modalToNav = function (x) {
        if (x.matches) { // If media query matches
            if ($("#saved-container").hasClass("col-6")) {
                $("#tab-container").removeClass("row")
                $("#saved-container").removeClass("col-6")
                $("#workout-container").removeClass("col-6")
                $(".workout-name-selected").css("display", "none")


                $("#tab-container").append(`<div class="modal" id="modal" tabindex="-1" role="dialog">
                                              <div class="modal-dialog" role="document">
                                                <div class="modal-content">
                                                  <div class="modal-header">
                                                    <h5 class="modal-title" id="modal-title"></h5>
                                                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                                      <span aria-hidden="true">&times;</span>
                                                    </button>
                                                  </div>
                                                  <div class="modal-body" id="modal-workout-container">
                                                  </div>
                                                </div>
                                              </div>
                                            </div>`)
                $("#modal-workout-container").append($("#workout-container"))

                $("#saved-container").attr("data-toggle", "modal")
                $("#saved-container").attr("data-target", "#modal")
            }

        }
        // revert changes back if screen width increased
        else {
            if (!$("#saved-container").hasClass("col-6")) {
                $("#tab-container").addClass("row")
                $("#saved-container").addClass("col-6")
                $("#workout-container").addClass("col-6")
                $(".workout-name-selected").css("display", "block")
                $("#tab-container").append($("#workout-container"))
                $(".modal").remove()
            }
        }
    }

    //event listener for tab pane change to change modal title
    $(".list-group-item").click(function () {
        if (!$("#saved-container").hasClass("col-6")) {
            $("#modal-title").text($(this).find(".workout-name")[0].textContent)
        }
     })


    var width991 = window.matchMedia("(max-width: 991px)")
    modalToNav(width991)
    width991.addListener(modalToNav)
})