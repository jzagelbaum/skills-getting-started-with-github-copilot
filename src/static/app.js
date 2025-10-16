document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  
  let isFetchingActivities = false;

  // Function to fetch activities from API
  async function fetchActivities() {
    if (isFetchingActivities) {
      return; // Prevent concurrent fetches
    }
    
    isFetchingActivities = true;
    try {
      const response = await fetch("/activities", {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache'
        }
      });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear and reset activity dropdown
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHTML = '';
        if (details.participants.length > 0) {
          const participantItems = details.participants
            .map(participant => `
              <li>
                <span class="participant-email">${participant}</span>
                <button class="delete-btn" data-activity="${name}" data-email="${participant}">
                  ✕
                </button>
              </li>
            `)
            .join('');
          participantsHTML = `
            <div class="participants-section">
              <h5>Current Participants:</h5>
              <ul class="participants-list">
                ${participantItems}
              </ul>
            </div>
          `;
        } else {
          participantsHTML = `
            <div class="participants-section">
              <h5>Current Participants:</h5>
              <p class="no-participants">No participants yet - be the first to sign up!</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    } finally {
      isFetchingActivities = false;
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    if (!email || !activity) {
      messageDiv.textContent = "Please fill in all fields";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities to show updated participant list
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete button clicks using event delegation
  activitiesList.addEventListener("click", (event) => {
    if (event.target.classList.contains("delete-btn")) {
      const activityName = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");
      unregisterParticipant(activityName, email);
    }
  });

  // Initialize app
  fetchActivities();
});

// Function to unregister a participant from an activity
async function unregisterParticipant(activityName, email) {
  const messageDiv = document.getElementById("message");
  
  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );
    
    const result = await response.json();

    if (response.ok) {
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      
      // Refresh activities to show updated participant list
      fetchActivities();
    } else {
      messageDiv.textContent = result.detail || "An error occurred while unregistering";
      messageDiv.className = "error";
    }

    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  } catch (error) {
    console.error("Error unregistering:", error);
    messageDiv.textContent = "Failed to unregister. Please try again.";
    messageDiv.className = "error";
    messageDiv.classList.remove("hidden");
  }
}
