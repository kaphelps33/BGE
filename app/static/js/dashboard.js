function handleAddMedicationClick(button) {
  const medicationInfo = {
    id: button.getAttribute("data-med-id"),
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
