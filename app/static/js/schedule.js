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
      .then((medsData) => { console.log(medsData)
        medsData.forEach((med) => {
          let createdAt = new Date(med.start_date);  // Use the creation date as the starting point
          let duration = med.duration;
          let occurrences = 0;

          // Map numeric days (0=Sunday, 6=Saturday) from the `med.days` array
          const targetDays = med.days;

          // Helper function to find the first occurrence of each target day
          function getNextTargetDay(startDate, targetDay) {
            let nextDate = new Date(startDate);
            while (nextDate.getDay() !== targetDay) {
              nextDate.setDate(nextDate.getDate() + 1);
            }
            return nextDate;
          }

          // Priority queue (array) to keep track of the next date for each target day
          let dateQueue = targetDays.map(day => getNextTargetDay(createdAt, day));
          dateQueue.sort((a, b) => a - b); // Sort by date to ensure correct order

          // Schedule events until the total occurrences reach the specified duration
          while (occurrences < duration) {
            // Take the earliest date from the queue
            let nextDate = dateQueue.shift();

            // Add the medication event to the calendar
            calendar.addEvent({
              title: "Taking " + med.name + " - " + med.dosage,
              start: nextDate.toISOString().split("T")[0], // Only the date part
              allDay: true,
            });

            // Increment the occurrences counter
            occurrences++;

            // Move this date to the same day in the following week and reinsert in the queue
            nextDate.setDate(nextDate.getDate() + 7);
            dateQueue.push(nextDate);

            // Sort the queue again to keep the earliest dates at the front
            dateQueue.sort((a, b) => a - b);
          }
        });
      })
      .catch((error) => console.error("Error fetching medications:", error));
});
