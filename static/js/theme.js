document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) {
        return;
    }

    const enableTransition = () => {
        body.classList.add("theme-transition");
        setTimeout(() => {
            body.classList.remove("theme-transition");
        }, 400);
    };

    const icon = toggle.querySelector("i");
    const label = toggle.querySelector("span");

    const updateButton = () => {
        if (!icon || !label) {
            return;
        }
        if (body.classList.contains("dark")) {
            icon.className = "bi bi-sun";
            label.textContent = "Tryb jasny";
        } else {
            icon.className = "bi bi-moon-stars";
            label.textContent = "Tryb ciemny";
        }
    };

    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
        body.classList.add("dark");
    }
    if (saved === "light") {
        body.classList.remove("dark");
    }
    if (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        body.classList.add("dark");
    }

    updateButton();

    toggle.addEventListener("click", () => {
        enableTransition();
        body.classList.toggle("dark");
        const isDark = body.classList.contains("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
        updateButton();
    });
});
