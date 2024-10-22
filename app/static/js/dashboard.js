function showContent(contentId) {
  // Hide all content sections
  document.querySelectorAll('.tab-content').forEach(function (content) {
    content.style.display = 'none';
  });

  // Remove 'active' class from all links
  document.querySelectorAll('.list-group-item').forEach(function (link) {
    link.classList.remove('active');
  });

  // Show the selected content section
  document.getElementById(contentId).style.display = 'block';

  // Add 'active' class to the clicked link
  event.target.classList.add('active');
}

// Initialize the default view (Overview)
document.addEventListener('DOMContentLoaded', function () {
  showContent('overview');  // Show overview content by default
});

function handleAddMedicationClick(button) {
  const medicationInfo = {
    id: button.getAttribute("data-med-id"),
    name: button.getAttribute("data-med-name"),
  };

  // Select the modal element
  const modalElement = document.querySelector("#addMedicationModal");

  // Create a new Bootstrap modal instance
  const modal = new bootstrap.Modal(modalElement);

  // Show the modal
  modal.show();

  // Use fetch to send a POST request to the '/add_medication' endpoint
  fetch("/add_medication", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(medicationInfo),
  })
    .then((response) => response.json())
    .then((data) => {
      // Handle the response from the server
      console.log(data.message);
    })
    .catch((error) => {
      // Handle the error
      console.error("Error:", error);
    });
}

function submitAddMedication(event) {
  // Prevent the default form submission
  event.preventDefault();

  // Create a FormData object from the form
  const formData = new FormData(document.getElementById("medicationForm"));

  // Send the data to the Flask route using Fetch API
  fetch("/add_medication", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (response.ok) {
        return response.text();
      }
      throw new Error("Network response was not ok.");
    })
    .then((data) => {
      console.log(data);
      // close the modal or reset the form
      $("#addMedicationModal").modal("hide");
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}
