    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('collapsed');
    }

    // Function to set default values
    function setDefaultValues() {
        // Set current date as default for the date input
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0]; // YYYY-MM-DD format
        document.getElementById('call-date').value = formattedDate;

        // Get current hours and minutes
        const currentHour = today.getHours();
        const currentMinutes = today.getMinutes();

        // Determine shift based on current time
        let selectedShift;
        if (currentHour >= 6 && currentHour < 14) {
            selectedShift = "06:00 AM - 02:00 PM";
        } else if (currentHour >= 14 && currentHour < 22) {
            selectedShift = "02:00 PM - 10:00 PM";
        } else {
            selectedShift = "10:00 PM - 06:00 AM";
        }
        document.getElementById('shift').value = selectedShift;

        // Set time-called to the current time
        const currentTime = `${String(currentHour).padStart(2, '0')}:${String(currentMinutes).padStart(2, '0')}`;
        document.getElementById('time-called').value = currentTime;

        // Set time-ended to one hour after time-called
        const timeEndedHour = currentHour + 1;
        const timeEnded = `${String(timeEndedHour % 24).padStart(2, '0')}:${String(currentMinutes).padStart(2, '0')}`;
        document.getElementById('time-ended').value = timeEnded;
    }

    // Call the function on page load
    window.onload = setDefaultValues;


    // Conditional Form fields
    function toggleConditionalFields() {
        const reason = document.getElementById("reason-for-calling").value;
        document.getElementById("conditional-fields").style.display = reason === "Calling for another Person" ? "block" : "none";
    }

    function toggleSelfHarmingFields() {
        const risk = document.getElementById("risk-assessment").value;
        document.getElementById("self-harming-fields").style.display = (risk === "Moderate Risk" || risk === "High Risk") ? "block" : "none";
    }

    function saveEditableSummary() {
        const editedSummary = document.getElementById('editableSummary').innerText;
        console.log('Edited Summary:', editedSummary);
        // Send updated summary to the server
    }

    document.addEventListener("DOMContentLoaded", function() {
        let links = document.querySelectorAll(".nav-link");
        let currentPath = window.location.pathname.replace(/\/$/, ""); // Remove trailing slash if present

        links.forEach(link => {
            let linkPath = new URL(link.href).pathname.replace(/\/$/, ""); // Normalize link href

            if (currentPath === linkPath) {
                link.classList.add("active");
            }
        });
    });



