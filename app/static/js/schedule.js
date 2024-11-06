// Calendar setup
document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth", // Start with a month view
  });
  calendar.render();

  // Fetch medication data and log the response
  fetch("/get_medications")
    .then((response) => response.json())
    .then((data) => {
      console.log("Fetched data:", data); // Log the fetched data to inspect its structure
    })
    .catch((error) => console.error("Error fetching medications:", error));
});
