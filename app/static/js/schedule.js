document.addEventListener("DOMContentLoaded", function () {
  // Initialize the calendar
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth", // Start with month view
    events: [], // Initially set an empty event list
  });

  // Render the calendar after it's been initialized
  calendar.render();

  fetch("/get_medications")
    .then((response) => response.json())
    .then((medsData) => {
      medsData.forEach((med) => {
        console.log(med);
        let startDate = new Date(med.start_date);
        let endDate = new Date(med.end_date);

        startDate.setDate(startDate.getDate() + 1);
        endDate.setDate(endDate.getDate() + 1);

        console.log(startDate);

        // Loop through the dates from start to end
        let currentDate = new Date(startDate);
        while (currentDate <= endDate) {
          // Add medication to the calendar on the corresponding day
          calendar.addEvent({
            title: "Taking " + med.name + " - " + med.dosage,
            start: currentDate.toISOString(),
            end: currentDate.toISOString(),
            allDay: true,
          });

          // Move to the next day
          currentDate.setDate(currentDate.getDate() + 1);
        }
      });
    })
    .catch((error) => console.error("Error fetching medications:", error));
});
