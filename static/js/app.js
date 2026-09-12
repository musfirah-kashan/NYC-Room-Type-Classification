// ============================================================
// SHARED: ambient skyline lights (decorative, runs on every page)
// ============================================================
const REDUCE_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function buildSkylineLights() {
  const container = document.getElementById("skylineBg");
  if (!container || REDUCE_MOTION) return;

  const count = 42;
  for (let i = 0; i < count; i++) {
    const light = document.createElement("div");
    light.className = "window-light";
    const size = Math.random() < 0.5 ? 2 : 3;
    light.style.width = `${size}px`;
    light.style.height = `${size}px`;
    light.style.left = `${Math.random() * 100}%`;
    light.style.bottom = `${8 + Math.random() * 32}vh`;
    light.style.animationDelay = `${Math.random() * 5}s`;
    light.style.animationDuration = `${3.5 + Math.random() * 3}s`;
    container.appendChild(light);
  }
}

// ============================================================
// SHARED: mobile nav toggle
// ============================================================
function wireNavToggle() {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  links.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => {
      links.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  buildSkylineLights();
  wireNavToggle();
});
