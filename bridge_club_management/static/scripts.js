
$(document).ready(function() {
  let selectedAssignmentId = null;

  // Show modal when select button is clicked
  $(".select-substitute").click(function() {
    selectedAssignmentId = $(this).data("assignment-id");
    $("#email-modal").show();
  });

  // Handle email confirmation
  $("#confirm-email").click(function() {
    const email = $("#email-input").val();

    if (email) {
      $.ajax({
        url: "{% url 'select_substitute' %}",
        type: "POST",
        data: JSON.stringify({
          assignment_id: selectedAssignmentId,
          email: email,
        }),
        contentType: "application/json",
        headers: {
          "X-CSRFToken": "{{ csrf_token }}",
        },
        success: function(response) {
          if (response.success) {
            alert("Substitute selected successfully!");
            location.reload();  // Reload the page to see updated status
          } else {
            alert("Failed to select substitute.");
          }
        },
      });

      $("#email-modal").hide();
    } else {
      alert("Please enter your email.");
    }
  });

  // Hide modal when cancel button is clicked
  $("#cancel-email").click(function() {
    $("#email-modal").hide();
  });
});
