document.addEventListener("DOMContentLoaded", function () {
  // Initialize the calendar
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    events: [],
  });

  // Render the calendar after it's been initialized
  calendar.render();

  fetch("/get_medications")
      .then((response) => response.json())
      .then((medsData) => {
        medsData.forEach((med) => {
          let createdAt = new Date(med.start_date);  // Use the creation date as the starting point
          let duration = med.duration;

          // Map numeric days (0=Sunday, 6=Saturday) from the `med.days` array
          const targetDays = med.days;

          // Track occurrences for each specific day
          let occurrences = {}; // e.g., { 1: 0, 3: 0, 5: 0 } for Monday, Wednesday, Friday

          // Initialize occurrences counter for each target day
          targetDays.forEach(day => occurrences[day] = 0);

          // Helper function to find the next occurrence of a target day
          function getNextTargetDay(date, targetDay) {
            let nextDate = new Date(date);
            while (nextDate.getDay() !== targetDay) {
              nextDate.setDate(nextDate.getDate() + 1);
            }
            return nextDate;
          }

          // Schedule events for each target day up to the specified duration
          targetDays.forEach(day => {
            let currentDate = getNextTargetDay(createdAt, day);
            while (occurrences[day] < duration) {
              // Add medication to the calendar on the corresponding day
              calendar.addEvent({
                title: "Taking " + med.name + " - " + med.dosage,
                start: currentDate.toISOString().split("T")[0], // Only the date part
                allDay: true,
              });

              // Move to the same day in the following week
              currentDate.setDate(currentDate.getDate() + 7);
              occurrences[day]++;
            }
          });
        });
      })
      .catch((error) => console.error("Error fetching medications:", error));
});
