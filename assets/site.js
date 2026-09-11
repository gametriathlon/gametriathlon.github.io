const menuButton = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");

if (menuButton && menu) {
  const closeMenu = () => {
    menuButton.setAttribute("aria-expanded", "false");
    menu.classList.remove("open");
  };

  menuButton.addEventListener("click", () => {
    const willOpen = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(willOpen));
    menu.classList.toggle("open", willOpen);
  });

  menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
}

const header = document.querySelector("[data-header]");
const updateHeader = () => header?.classList.toggle("scrolled", window.scrollY > 18);
updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const supportTabs = document.querySelectorAll("[data-support-tab]");
const supportPanels = document.querySelectorAll("[data-support-panel]");

supportTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const selected = tab.dataset.supportTab;
    supportTabs.forEach((candidate) => {
      const active = candidate === tab;
      candidate.classList.toggle("is-active", active);
      candidate.setAttribute("aria-selected", String(active));
    });
    supportPanels.forEach((panel) => {
      const active = panel.dataset.supportPanel === selected;
      panel.classList.toggle("is-active", active);
      panel.hidden = !active;
    });
  });
});

async function copySupportValue(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const field = document.createElement("textarea");
  field.value = value;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.opacity = "0";
  document.body.appendChild(field);
  field.select();
  document.execCommand("copy");
  field.remove();
}

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const label = button.textContent;
    const status = document.querySelector("[data-copy-status]");
    try {
      await copySupportValue(button.dataset.copy);
      button.textContent = "Скопировано";
      if (status) status.textContent = "Реквизиты скопированы в буфер обмена.";
      window.setTimeout(() => { button.textContent = label; }, 1600);
    } catch {
      button.textContent = "Выделите адрес";
      if (status) status.textContent = "Не удалось скопировать автоматически. Выделите адрес вручную.";
      window.setTimeout(() => { button.textContent = label; }, 2200);
    }
  });
});

document.querySelectorAll("[data-year]").forEach((element) => {
  element.textContent = String(new Date().getFullYear());
});

const gameplayVideo = document.querySelector("[data-gameplay-video]");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

if (gameplayVideo && "IntersectionObserver" in window) {
  const updateGameplayPlayback = (visible) => {
    if (visible && !reducedMotion.matches) {
      gameplayVideo.play().catch(() => {
        // Браузер может запретить autoplay; poster и controls остаются доступны.
      });
    } else {
      gameplayVideo.pause();
    }
  };

  const gameplayObserver = new IntersectionObserver((entries) => {
    const entry = entries[0];
    updateGameplayPlayback(entry?.isIntersecting === true && entry.intersectionRatio >= 0.35);
  }, { threshold: 0.35 });

  gameplayObserver.observe(gameplayVideo);
  reducedMotion.addEventListener?.("change", () => {
    updateGameplayPlayback(!reducedMotion.matches && gameplayVideo.getBoundingClientRect().top < window.innerHeight && gameplayVideo.getBoundingClientRect().bottom > 0);
  });
}

const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = lightbox?.querySelector("[data-lightbox-image]");
const lightboxCaption = lightbox?.querySelector("[data-lightbox-caption]");
let lightboxTrigger = null;

document.querySelectorAll("[data-lightbox-trigger]").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    if (!lightbox || !lightboxImage) return;
    lightboxTrigger = trigger;
    lightboxImage.src = trigger.dataset.lightboxSrc;
    lightboxImage.alt = trigger.dataset.lightboxAlt || "";
    if (lightboxCaption) lightboxCaption.textContent = trigger.dataset.lightboxCaption || "";
    lightbox.showModal();
  });
});

const closeLightbox = () => {
  lightbox?.close();
  lightboxTrigger?.focus();
};

lightbox?.querySelector("[data-lightbox-close]")?.addEventListener("click", closeLightbox);
lightbox?.addEventListener("click", (event) => {
  if (event.target === lightbox) closeLightbox();
});

function validRelease(value) {
  return value && value.available === true
    && typeof value.version === "string" && value.version.length > 0
    && typeof value.date === "string" && value.date.length > 0
    && typeof value.size === "string" && value.size.length > 0
    && typeof value.download === "string" && value.download.startsWith("https://github.com/gametriathlon/gametriathlon.github.io/releases/download/")
    && Array.isArray(value.changes) && value.changes.every((item) => typeof item === "string");
}

function applyRelease(release) {
  if (!validRelease(release)) return;

  document.querySelectorAll("[data-download]").forEach((link) => {
    link.href = release.download;
    link.removeAttribute("aria-disabled");
    link.classList.remove("is-disabled");
  });
  document.querySelectorAll("[data-download-label]").forEach((label) => {
    label.textContent = "Скачать для macOS";
  });

  const heroRelease = document.querySelector("[data-hero-release]");
  if (heroRelease) heroRelease.textContent = `${release.version} · ${release.size} · macOS 26+`;

  const title = document.querySelector("[data-release-title]");
  if (title) title.textContent = `Game Triathlon ${release.version}`;

  const meta = document.querySelector("[data-release-meta]");
  if (meta) meta.textContent = `${release.date} · ${release.size}`;

  const changes = document.querySelector("[data-changes]");
  if (changes) {
    changes.replaceChildren(...release.changes.map((text) => {
      const item = document.createElement("li");
      item.textContent = text;
      return item;
    }));
  }
}

fetch("release.json", { cache: "no-store" })
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(applyRelease)
  .catch(() => {
    // Статический HTML уже содержит безопасное состояние «Скоро».
  });
