const templateSelect = document.getElementById("template-select");
const templatePicker = document.getElementById("template-picker");
const templatePreviewImage = document.getElementById("template-preview-image");
const templatePreviewName = document.getElementById("template-preview-name");
const previewDownload = document.getElementById("preview-download");
const generateForm = document.getElementById("generate-form");
const generateStatus = document.getElementById("generate-status");
const catalogList = document.getElementById("catalog-list");
const generatedList = document.getElementById("generated-list");
const profileStatus = document.getElementById("profile-status");
const toast = document.getElementById("toast");

const navCatalog = document.getElementById("nav-catalog");
const navGenerate = document.getElementById("nav-generate");
const navProfile = document.getElementById("nav-profile");
const pageCatalog = document.getElementById("page-catalog");
const pageGenerate = document.getElementById("page-generate");
const pageProfile = document.getElementById("page-profile");

const topUserLabel = document.getElementById("top-user-label");
const navLogin = document.getElementById("nav-login");
const navRegister = document.getElementById("nav-register");
const navLogout = document.getElementById("nav-logout");
const themeToggle = document.getElementById("theme-toggle");

const authModal = document.getElementById("auth-modal");
const authModalBackdrop = document.getElementById("auth-modal-backdrop");
const authModalTitle = document.getElementById("auth-modal-title");
const authClose = document.getElementById("auth-close");
const authForm = document.getElementById("auth-form");
const authEmail = document.getElementById("auth-email");
const authPassword = document.getElementById("auth-password");
const authSubmit = document.getElementById("auth-submit");
const authStatus = document.getElementById("auth-status");

let templatesById = new Map();
let previewObjectUrl = null;
let previewDebounceTimer = null;
let previewRequestController = null;
let authMode = "login";
let currentUser = null;
const THEME_STORAGE_KEY = "dc_theme_v3";

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
}

function loadStoredUser() {
  try {
    const raw = localStorage.getItem("dc_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveStoredUser(user) {
  localStorage.setItem("dc_user", JSON.stringify(user));
}

function clearStoredUser() {
  localStorage.removeItem("dc_user");
}

function loadStoredTheme() {
  const theme = localStorage.getItem(THEME_STORAGE_KEY);
  return theme === "dark" ? "dark" : "light";
}

function applyTheme(theme) {
  const isDark = theme === "dark";
  document.documentElement.classList.toggle("theme-dark", isDark);
  const nextTheme = isDark ? "light" : "dark";
  themeToggle.setAttribute("aria-label", `Switch to ${nextTheme} theme`);
  themeToggle.setAttribute("title", `Switch to ${nextTheme} theme`);
  themeToggle.setAttribute("aria-pressed", String(isDark));
  localStorage.setItem(THEME_STORAGE_KEY, isDark ? "dark" : "light");
}

function toggleTheme() {
  const isDark = document.documentElement.classList.contains("theme-dark");
  applyTheme(isDark ? "light" : "dark");
}

function setAuthMode(mode) {
  authMode = mode;
  const isLogin = mode === "login";
  authModalTitle.textContent = isLogin ? "Login" : "Register";
  authSubmit.textContent = isLogin ? "Login" : "Register";
}

function openAuthModal(mode) {
  setAuthMode(mode);
  authModal.classList.remove("hidden");
  authModal.setAttribute("aria-hidden", "false");
  authStatus.textContent = currentUser
    ? `Logged in as ${currentUser.email}`
    : "Not logged in";
}

function closeAuthModal() {
  authModal.classList.add("hidden");
  authModal.setAttribute("aria-hidden", "true");
}

function renderAuthState() {
  if (!currentUser) {
    topUserLabel.textContent = "Guest";
    navLogin.classList.remove("hidden");
    navRegister.classList.remove("hidden");
    navLogout.classList.add("hidden");
    navProfile.classList.add("hidden");
    if (window.location.hash === "#profile") {
      window.location.hash = "#catalog";
    }
    return;
  }

  topUserLabel.textContent = currentUser.email;
  navLogin.classList.add("hidden");
  navRegister.classList.add("hidden");
  navLogout.classList.remove("hidden");
  navProfile.classList.remove("hidden");
}

function getActivePage() {
  if (window.location.hash === "#profile") {
    return "profile";
  }
  if (window.location.hash === "#generate") {
    return "generate";
  }
  return "catalog";
}

function renderPage() {
  const active = getActivePage();
  const isCatalog = active === "catalog";
  const isGenerate = active === "generate";
  const isProfile = active === "profile";
  pageCatalog.classList.toggle("active", isCatalog);
  pageGenerate.classList.toggle("active", isGenerate);
  pageProfile.classList.toggle("active", isProfile);
  navCatalog.classList.toggle("active", isCatalog);
  navGenerate.classList.toggle("active", isGenerate);
  navProfile.classList.toggle("active", isProfile);

  if (isProfile && !currentUser) {
    profileStatus.textContent =
      "You are viewing public generated images. Login is required for personal profile features.";
  } else if (isProfile && currentUser) {
    profileStatus.textContent = `Signed in as ${currentUser.email}.`;
  }
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let errorDetail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      errorDetail = body.detail || JSON.stringify(body);
    } catch {
      // keep fallback text
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

async function requestPreviewImage(templateId, payload) {
  if (previewRequestController) {
    previewRequestController.abort();
  }

  previewRequestController = new AbortController();
  const res = await fetch(`/templates/${templateId}/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: previewRequestController.signal,
  });

  if (!res.ok) {
    let errorDetail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      errorDetail = body.detail || JSON.stringify(body);
    } catch {
      // keep fallback
    }
    throw new Error(errorDetail);
  }

  return res.blob();
}

function buildGeneratePayload() {
  return {
    text_top: document.getElementById("top-text").value.trim(),
    text_bottom: document.getElementById("bottom-text").value.trim(),
    font_name: document.getElementById("font-name").value,
    font_size: Number(document.getElementById("font-size").value),
  };
}

function updatePreviewDownloadState(enabled) {
  previewDownload.classList.toggle("disabled", !enabled);
  previewDownload.setAttribute("aria-disabled", String(!enabled));
}

previewDownload.addEventListener("click", (event) => {
  if (previewDownload.getAttribute("aria-disabled") === "true") {
    event.preventDefault();
  }
});

async function refreshPreview() {
  const templateId = Number(templateSelect.value);
  if (!templateId) {
    return;
  }

  try {
    const blob = await requestPreviewImage(templateId, buildGeneratePayload());
    if (previewObjectUrl) {
      URL.revokeObjectURL(previewObjectUrl);
    }
    previewObjectUrl = URL.createObjectURL(blob);
    templatePreviewImage.src = previewObjectUrl;
    previewDownload.href = previewObjectUrl;
    previewDownload.download = `preview-template-${templateId}.jpg`;
    updatePreviewDownloadState(true);
  } catch (error) {
    if (error.name === "AbortError") {
      return;
    }
    updatePreviewDownloadState(false);
    generateStatus.textContent = `Preview failed: ${error.message}`;
  }
}

function schedulePreview(delayMs = 250) {
  if (previewDebounceTimer) {
    clearTimeout(previewDebounceTimer);
  }
  previewDebounceTimer = setTimeout(() => {
    refreshPreview();
  }, delayMs);
}

function selectTemplate(templateId) {
  templateSelect.value = String(templateId || "");

  for (const card of templatePicker.querySelectorAll(".template-card")) {
    const isSelected = card.dataset.templateId === templateSelect.value;
    card.classList.toggle("selected", isSelected);
    card.setAttribute("aria-checked", String(isSelected));
  }

  const selectedTemplate = templatesById.get(Number(templateId));
  if (!selectedTemplate) {
    templatePreviewImage.removeAttribute("src");
    templatePreviewName.textContent = "Template not selected";
    updatePreviewDownloadState(false);
    return;
  }

  templatePreviewImage.src = `/templates/${selectedTemplate.id}/image`;
  templatePreviewImage.alt = selectedTemplate.name;
  templatePreviewName.textContent = selectedTemplate.name;
  updatePreviewDownloadState(false);
  schedulePreview(0);
}

function renderTemplateOptions(templates) {
  templatePicker.innerHTML = "";
  templateSelect.value = "";
  templatesById = new Map(templates.map((template) => [template.id, template]));

  if (!templates.length) {
    const empty = document.createElement("p");
    empty.className = "template-empty";
    empty.textContent = "No templates available";
    templatePicker.append(empty);
    templatePreviewImage.removeAttribute("src");
    templatePreviewName.textContent = "No templates available";
    return;
  }

  for (const template of templates) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "template-card";
    button.dataset.templateId = String(template.id);
    button.setAttribute("role", "radio");
    button.setAttribute("aria-checked", "false");

    const image = document.createElement("img");
    image.src = `/templates/${template.id}/image`;
    image.alt = template.name;
    image.loading = "lazy";

    const title = document.createElement("span");
    title.className = "template-card__name";
    title.textContent = template.name;

    button.append(image, title);
    button.addEventListener("click", () => selectTemplate(template.id));
    templatePicker.append(button);
  }

  selectTemplate(templates[0].id);
}

function renderCatalogTemplates(templates) {
  catalogList.innerHTML = "";
  if (!templates.length) {
    const empty = document.createElement("p");
    empty.className = "template-empty";
    empty.textContent = "No templates available";
    catalogList.append(empty);
    return;
  }

  for (const template of templates) {
    const card = document.createElement("article");
    card.className = "catalog-card";

    const image = document.createElement("img");
    image.src = `/templates/${template.id}/image`;
    image.alt = template.name;
    image.loading = "lazy";

    const title = document.createElement("p");
    title.className = "catalog-card__name";
    title.textContent = template.name;

    const useButton = document.createElement("button");
    useButton.type = "button";
    useButton.className = "secondary compact";
    useButton.textContent = "Use in generator";
    useButton.addEventListener("click", () => {
      selectTemplate(template.id);
      window.location.hash = "#generate";
    });

    card.append(image, title, useButton);
    catalogList.append(card);
  }
}

async function copyShareLink(shareToken) {
  const shareUrl = `${window.location.origin}/images/${shareToken}`;
  try {
    await navigator.clipboard.writeText(shareUrl);
    showToast("Share link copied");
  } catch {
    showToast(`Share URL: ${shareUrl}`);
  }
}

function renderGeneratedImages(images) {
  generatedList.innerHTML = "";
  if (!images.length) {
    generatedList.textContent = "No generated images yet.";
    return;
  }

  for (const image of images) {
    const card = document.createElement("article");
    card.className = "image-card";

    const img = document.createElement("img");
    img.loading = "lazy";
    img.alt = image.share_token;
    img.src = `/images/${image.share_token}`;

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.innerHTML = `
      <strong>#${image.id}</strong>
      <span>Template: ${image.template_id}</span>
      <span>Token: ${image.share_token}</span>
    `;

    const actions = document.createElement("div");
    actions.className = "image-actions";

    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "secondary compact";
    copyButton.textContent = "Copy share link";
    copyButton.addEventListener("click", () =>
      copyShareLink(image.share_token),
    );

    const downloadLink = document.createElement("a");
    downloadLink.className = "download-link";
    downloadLink.href = `/images/${image.share_token}`;
    downloadLink.download = `generated-${image.id}.jpg`;
    downloadLink.textContent = "Download";

    actions.append(copyButton, downloadLink);
    card.append(img, meta, actions);
    generatedList.append(card);
  }
}

async function loadTemplates() {
  const templates = await api("/templates");
  renderCatalogTemplates(templates);
  renderTemplateOptions(templates);
  if (!templates.length) {
    generateStatus.textContent =
      "Templates are managed in admin panel. Ask admin to add one.";
  } else {
    generateStatus.textContent = "";
  }
  return templates;
}

async function loadGeneratedImages() {
  const images = await api("/generated_images");
  renderGeneratedImages(images);
}

generateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentUser) {
    showToast("Login first to generate images", true);
    openAuthModal("login");
    return;
  }

  const templateId = Number(templateSelect.value);
  if (!templateId) {
    showToast("No template available for generation", true);
    return;
  }

  const payload = buildGeneratePayload();
  const submitButton = generateForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  submitButton.textContent = "Generating...";

  try {
    const created = await api(`/templates/${templateId}/generate`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast(`Image #${created.id} generated`);
    generateStatus.textContent = `Generated image #${created.id} (token: ${created.share_token})`;
    generateForm.reset();
    document.getElementById("font-name").value = "dejavu_sans";
    document.getElementById("font-size").value = 40;
    selectTemplate(templateId);
    await loadGeneratedImages();
  } catch (error) {
    generateStatus.textContent = `Generate failed: ${error.message}`;
    showToast(`Generate failed: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Generate";
  }
});

for (const id of ["top-text", "bottom-text", "font-name", "font-size"]) {
  const field = document.getElementById(id);
  field.addEventListener("input", () => schedulePreview(220));
  field.addEventListener("change", () => schedulePreview(120));
}

window.addEventListener("hashchange", renderPage);

navLogin.addEventListener("click", () => openAuthModal("login"));
navRegister.addEventListener("click", () => openAuthModal("register"));
navLogout.addEventListener("click", () => {
  currentUser = null;
  clearStoredUser();
  renderAuthState();
  renderPage();
  showToast("Logged out");
});
themeToggle.addEventListener("click", toggleTheme);

authClose.addEventListener("click", closeAuthModal);
authModalBackdrop.addEventListener("click", closeAuthModal);

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    email: authEmail.value.trim(),
    password: authPassword.value,
  };

  authSubmit.disabled = true;
  authSubmit.textContent =
    authMode === "login" ? "Logging in..." : "Registering...";

  try {
    const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";
    const user = await api(endpoint, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    currentUser = user;
    saveStoredUser(user);
    renderAuthState();
    renderPage();
    authPassword.value = "";
    authStatus.textContent = `Logged in as ${user.email}`;
    showToast(authMode === "login" ? "Login successful" : "Account created");
    closeAuthModal();
  } catch (error) {
    authStatus.textContent = `Auth failed: ${error.message}`;
    showToast(`Auth failed: ${error.message}`, true);
  } finally {
    authSubmit.disabled = false;
    authSubmit.textContent = authMode === "login" ? "Login" : "Register";
  }
});

async function bootstrap() {
  applyTheme(loadStoredTheme());
  currentUser = loadStoredUser();
  renderAuthState();
  renderPage();

  try {
    await loadTemplates();
    await loadGeneratedImages();
  } catch (error) {
    showToast(`Load failed: ${error.message}`, true);
  }
}

bootstrap();
