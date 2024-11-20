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
        console.log(medsData); // Debugging: Check the data structure
        medsData.forEach((med) => {
          let startDate = new Date(med.start_date);
          let endDate = new Date(med.end_date);
          let daysTaken = med.days_taken || [];
          const targetDays = med.days;

          while (startDate <= endDate) {
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
            }
            startDate.setDate(startDate.getDate() + 1); // Move to the next day
          }
        });
      })
      .catch((error) => console.error("Error fetching medications:", error));
});

function markMedicationTaken(medId, date) {
  fetch(`/medication/update_status/${medId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ date: date }),
  })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Update the calendar event color
          let event = calendar.getEventById(medId);
          if (event) {
            event.setProp("backgroundColor", "green");
          }
        }
      })
      .catch((error) => console.error("Error updating medication status:", error));
}

