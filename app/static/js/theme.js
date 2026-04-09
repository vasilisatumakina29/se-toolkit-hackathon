const root = document.documentElement;
const toggle = document.querySelector("[data-theme-toggle]");
const themeLabel = document.querySelector("[data-theme-label]");

const getPreferredTheme = () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light" || savedTheme === "dark") {
        return savedTheme;
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

const applyTheme = (theme) => {
    const isDark = theme === "dark";
    root.dataset.theme = theme;

    if (toggle) {
        toggle.setAttribute("aria-pressed", String(isDark));
    }

    if (themeLabel) {
        themeLabel.textContent = isDark ? "Dark" : "Light";
    }
};

applyTheme(getPreferredTheme());

if (toggle) {
    toggle.addEventListener("click", () => {
        const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
        localStorage.setItem("theme", nextTheme);
        applyTheme(nextTheme);
    });
}

window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
    if (localStorage.getItem("theme")) {
        return;
    }

    applyTheme(event.matches ? "dark" : "light");
});
