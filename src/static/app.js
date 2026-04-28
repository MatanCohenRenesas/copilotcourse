// Translations for different languages
const translations = {
  en: {
    'title': 'Extracurricular Activities',
    'available-activities': 'Available Activities',
    'signup-title': 'Sign Up for an Activity',
    'email-label': 'Student Email:',
    'activity-label': 'Select Activity:',
    'select-activity': '-- Select an activity --',
    'signup-btn': 'Sign Up',
    'loading': 'Loading activities...',
    'footer-text': 'Discover Your Passion',
    'schedule': 'Schedule:',
    'availability': 'Availability:',
    'spots-left': 'spots left',
    'participants': 'Participants',
  },
  es: {
    'title': 'Actividades Extraescolares',
    'available-activities': 'Actividades Disponibles',
    'signup-title': 'Regístrate para una Actividad',
    'email-label': 'Email del Estudiante:',
    'activity-label': 'Selecciona una Actividad:',
    'select-activity': '-- Selecciona una actividad --',
    'signup-btn': 'Registrarse',
    'loading': 'Cargando actividades...',
    'footer-text': 'Descubre Tu Pasión',
    'schedule': 'Horario:',
    'availability': 'Disponibilidad:',
    'spots-left': 'lugares disponibles',
    'participants': 'Participantes',
  },
  zh: {
    'title': '课外活动',
    'available-activities': '可用活动',
    'signup-title': '注册活动',
    'email-label': '学生邮箱:',
    'activity-label': '选择活动:',
    'select-activity': '-- 选择一个活动 --',
    'signup-btn': '注册',
    'loading': '正在加载活动...',
    'footer-text': '发现你的热情',
    'schedule': '时间表:',
    'availability': '可用性:',
    'spots-left': '个名额剩余',
    'participants': '参与者',
  }
};

let currentLanguage = localStorage.getItem('language') || 'en';

document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const languageSelect = document.getElementById("language-select");
  const darkModeToggle = document.getElementById("dark-mode-toggle");

  // Set up language switcher
  languageSelect.value = currentLanguage;
  languageSelect.addEventListener("change", (e) => {
    currentLanguage = e.target.value;
    localStorage.setItem('language', currentLanguage);
    updateLanguage();
    fetchActivities();
  });

  // Set up dark mode toggle
  const isDarkMode = localStorage.getItem('darkMode') === 'true';
  if (isDarkMode) {
    document.body.classList.add('dark-mode');
    darkModeToggle.textContent = '☀️';
  }

  darkModeToggle.addEventListener("click", () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    darkModeToggle.textContent = isDark ? '☀️' : '🌙';
  });



  // Update language on page
  function updateLanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = translations[currentLanguage][key] || translations['en'][key];
    });
  }

  // Function to get translation
  function t(key) {
    return translations[currentLanguage][key] || translations['en'][key];
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList = details.participants
          .map(email => `<li><span class="participant-email">${email}</span><button class="delete-participant" data-activity="${name}" data-email="${email}" title="Remove participant">×</button></li>`)
          .join('');

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>${t('schedule')}</strong> ${details.schedule}</p>
          <p><strong>${t('availability')}:</strong> ${spotsLeft} ${t('spots-left')}</p>
          <div class="participants-section">\n            <strong>${t('participants')} (${details.participants.length}/${details.max_participants}):</strong>\n            <ul class="participants-list">\n              ${participantsList}\n            </ul>\n          </div>\n        `;

        // Add delete functionality to each participant's delete button
        const deleteButtons = activityCard.querySelectorAll('.delete-participant');
        deleteButtons.forEach(button => {
          button.addEventListener('click', async (e) => {
            e.preventDefault();
            const activityName = button.getAttribute('data-activity');
            const email = button.getAttribute('data-email');
            
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
                { method: 'DELETE' }
              );
              
              if (response.ok) {
                fetchActivities(); // Refresh the list
              } else {
                const result = await response.json();
                alert(result.detail || 'Error removing participant');
              }
            } catch (error) {
              alert('Failed to remove participant');
              console.error('Error:', error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      updateLanguage();
    } catch (error) {
      activitiesList.innerHTML = `<p>${t('loading')}</p>`;
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

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
        messageDiv.className = "message success";
        signupForm.reset();
        fetchActivities(); // Refresh activity list to show updated participants
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "message error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "message error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  updateLanguage();
  fetchActivities();
});
