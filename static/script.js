// script.js – Optional enhancements for IndocNow

// Smooth scroll for anchors
const links = document.querySelectorAll("a[href^='#']");
links.forEach(link => {
  link.addEventListener("click", function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth"
    });
  });
});

// Show toast/alert for subscription success
function showToast(message) {
  const toast = document.createElement("div");
  toast.innerText = message;
  toast.style.cssText = "position:fixed;top:10px;right:10px;background:#333;color:#fff;padding:10px;border-radius:5px;z-index:9999";
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Optional dark mode toggle (button required in HTML)
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
}

// Placeholder for future auto-translation enhancements via JS
function translatePage(language) {
  console.log("Language to switch:", language);
  // Integration with translation APIs like Google Cloud, LibreTranslate etc. can be added here
}

// Auto-submit language form on dropdown change
document.addEventListener("DOMContentLoaded", function () {
  const languageForm = document.querySelector(".language-form select");
  if (languageForm) {
    languageForm.addEventListener("change", () => {
      languageForm.closest("form").submit();
    });
  }

  // Auto-submit search form on Enter key
  const searchInput = document.querySelector("input[name='q']");
  if (searchInput) {
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        this.closest("form").submit();
      }
    });
  }

  // Optional: Clickable cards (can turn off if unwanted)
  const cards = document.querySelectorAll(".article-card");
  cards.forEach(card => {
    const link = card.querySelector("a.read-more");
    if (link) {
      card.style.cursor = "pointer";
      card.addEventListener("click", () => {
        window.location.href = link.href;
      });
    }
  });
});

function startSlider(containerId) {
  const container = document.getElementById(containerId);
  const track = container.querySelector('.vertical-ad-track');
  const frames = container.querySelectorAll('.ad-frame');
  let currentIndex = 0;

  setInterval(() => {
    currentIndex = (currentIndex + 1) % frames.length;
    track.style.transform = `translateY(-${currentIndex * 200}px)`;
  }, 3000); // 3-second delay
}

document.addEventListener("DOMContentLoaded", function () {
  startSlider("match-slider");
  startSlider("ad-slider");
  startSlider("movie-slider");
});


function loadWeather() {
  navigator.geolocation.getCurrentPosition(async (position) => {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`);
    const data = await res.json();
    const temp = data.current_weather.temperature;
    document.getElementById("weather-text").innerText = `🌡️ ${temp}°C`;
  }, () => {
    document.getElementById("weather-text").innerText = "Location denied";
  });
}



fetch("https://api.exchangerate-api.com/v4/latest/USD")
  .then(res => res.json())
  .then(data => {
    const rates = data.rates;
    const currencyList = document.getElementById("currency-list");

    const wantedCurrencies = [
      { code: "RWF", name: "Rwandan Franc" },
      { code: "KES", name: "Kenyan Shilling" },
      { code: "UGX", name: "Ugandan Shilling" },
      { code: "EUR", name: "Euro" },
      { code: "GBP", name: "British Pound" },
      { code: "TZS", name: "Tanzanian Shilling" }
    ];

    currencyList.innerHTML = ""; // Clear "Loading..."

    wantedCurrencies.forEach(curr => {
      const li = document.createElement("li");
      li.textContent = `1 USD = ${rates[curr.code]} ${curr.code} (${curr.name})`;
      currencyList.appendChild(li);
    });
  })
  .catch(err => {
    document.getElementById("currency-list").innerHTML = "<li>Currency data unavailable</li>";
    console.error("Currency fetch error:", err);
  });


window.onload = () => {
  loadWeather();
  loadCurrency();
};


function shareArticle() {
  if (navigator.share) {
    navigator.share({
      title: document.title,
      text: "Check out this article from IndocNow!",
      url: window.location.href
    })
    .then(() => console.log('Shared successfully'))
    .catch((error) => console.log('Error sharing', error));
  } else {
    alert("Sharing not supported on this browser.");
  }
}

function copyLink() {
  navigator.clipboard.writeText(window.location.href)
    .then(() => alert("Link copied!"))
    .catch(() => alert("Failed to copy link."));
}