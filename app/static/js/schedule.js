document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    events: [],
  });

  calendar.render();

  fetch("/get_medications")
      .then((response) => response.json())
      .then((medsData) => {
        console.log("Medications Data:", medsData); // Log entire data structure
        medsData.forEach((med) => {
          let startDate = new Date(med.start_date);
          let endDate = new Date(med.end_date);
          let daysTaken = med.days_taken || [];
          const targetDays = med.days; // Days of the week (e.g., [0, 2, 4])
          let occurrences = 0;

          // Iterate over the range of dates
          while (startDate <= endDate && occurrences < med.duration) {
            if (targetDays.includes(startDate.getDay())) {
              let color = daysTaken.includes(startDate.toISOString().split("T")[0])
                  ? "green" // Taken
                  : "blue"; // Not taken

              calendar.addEvent({
                title: `${med.name} - ${med.dosage}`,
                start: startDate.toISOString().split("T")[0],
                allDay: true,
                backgroundColor: color,
              });

              occurrences++;
            }

            // Move to the next day
            startDate.setDate(startDate.getDate() + 1);
          }

          console.log(`Total occurrences for ${med.name}: ${occurrences}`);
        });
      })
      .catch((error) => console.error("Error fetching medications:", error));
});
