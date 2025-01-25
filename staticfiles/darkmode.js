document.addEventListener("DOMContentLoaded", function () {
    const toggleSwitch = document.querySelector(".toggle-switch");

    // Check for saved dark mode preference in localStorage
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        if (toggleSwitch) toggleSwitch.classList.add("active");
    } else {
        document.body.classList.remove("dark-mode");
        if (toggleSwitch) toggleSwitch.classList.remove("active");
    }
});

/**
 * Toggle dark mode on and off and save preference in localStorage
 * @param element The toggle element
 */
function toggleDarkMode(element) {
    element.classList.toggle("active");
    document.body.classList.toggle("dark-mode");

    // Save the dark mode preference in localStorage
    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "enabled");
    } else {
        localStorage.setItem("darkMode", "disabled");
    }
}
