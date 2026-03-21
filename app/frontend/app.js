import { api, requestPreviewImage } from "./api.js";
import { loadCurrentUser, login, logout, register } from "./auth-client.js";

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
const navAdmin = document.getElementById("nav-admin");
const pageCatalog = document.getElementById("page-catalog");
const pageGenerate = document.getElementById("page-generate");
const pageProfile = document.getElementById("page-profile");
const pageAdmin = document.getElementById("page-admin");

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
const authConfirmWrap = document.getElementById("auth-confirm-wrap");
const authConfirmPassword = document.getElementById("auth-confirm-password");
const authTogglePassword = document.getElementById("auth-toggle-password");
const authSubmit = document.getElementById("auth-submit");
const authStatus = document.getElementById("auth-status");
const adminStatus = document.getElementById("admin-status");
const adminTemplateForm = document.getElementById("admin-template-form");
const adminTemplateName = document.getElementById("admin-template-name");
const adminTemplateImageName = document.getElementById(
  "admin-template-image-name",
);
const adminSubmit = document.getElementById("admin-submit");
const adminTemplateList = document.getElementById("admin-template-list");
const adminFileStatus = document.getElementById("admin-file-status");
const adminFilePreviewImage = document.getElementById(
  "admin-file-preview-image",
);
const adminFilePreviewMeta = document.getElementById("admin-file-preview-meta");
const fontColorInput = document.getElementById("font-color");
const fontColorValue = document.getElementById("font-color-value");
const colorPresetButtons = Array.from(
  document.querySelectorAll(".color-preset"),
);
const adminLayoutTemplateSelect = document.getElementById(
  "admin-layout-template-select",
);
const layoutTopX = document.getElementById("layout-top-x");
const layoutTopY = document.getElementById("layout-top-y");
const layoutTopWidth = document.getElementById("layout-top-width");
const layoutBottomX = document.getElementById("layout-bottom-x");
const layoutBottomY = document.getElementById("layout-bottom-y");
const layoutBottomWidth = document.getElementById("layout-bottom-width");
const layoutSampleTop = document.getElementById("layout-sample-top");
const layoutSampleBottom = document.getElementById("layout-sample-bottom");
const adminLayoutPreviewButton = document.getElementById(
  "admin-layout-preview-button",
);
const adminLayoutSaveButton = document.getElementById(
  "admin-layout-save-button",
);
const adminLayoutStatus = document.getElementById("admin-layout-status");
const adminLayoutPreviewImage = document.getElementById(
  "admin-layout-preview-image",
);

let templatesById = new Map();
let previewObjectUrl = null;
let previewDebounceTimer = null;
let previewRequestController = null;
let adminLayoutPreviewDebounceTimer = null;
let adminLayoutPreviewController = null;
let authMode = "login";
let currentUser = null;
let isPasswordVisible = false;
let adminPreviewObjectUrl = null;
let adminLayoutPreviewObjectUrl = null;
let selectedAdminTemplateId = null;
const THEME_STORAGE_KEY = "meme_studio_theme_v1";

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
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
  authConfirmWrap.classList.toggle("hidden", isLogin);
  authConfirmPassword.required = !isLogin;
  authConfirmPassword.value = "";
  setPasswordVisibility(false);
}

function setPasswordVisibility(visible) {
  isPasswordVisible = visible;
  const inputType = visible ? "text" : "password";
  authPassword.type = inputType;
  authConfirmPassword.type = inputType;
  const nextAction = visible ? "Hide password" : "Show password";
  authTogglePassword.setAttribute("aria-label", nextAction);
  authTogglePassword.setAttribute("title", nextAction);
  authTogglePassword.classList.toggle("visible", visible);
}

function togglePasswordVisibility() {
  setPasswordVisibility(!isPasswordVisible);
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

function isAdminUser() {
  return Boolean(currentUser?.is_admin);
}

function renderAuthState() {
  if (!currentUser) {
    topUserLabel.textContent = "Guest";
    navLogin.classList.remove("hidden");
    navRegister.classList.remove("hidden");
    navLogout.classList.add("hidden");
    navProfile.classList.add("hidden");
    navAdmin.classList.add("hidden");
    if (
      window.location.hash === "#profile" ||
      window.location.hash === "#admin"
    ) {
      window.location.hash = "#catalog";
    }
    return;
  }

  topUserLabel.textContent = currentUser.email;
  navLogin.classList.add("hidden");
  navRegister.classList.add("hidden");
  navLogout.classList.remove("hidden");
  navProfile.classList.remove("hidden");
  navAdmin.classList.toggle("hidden", !isAdminUser());

  if (window.location.hash === "#admin" && !isAdminUser()) {
    window.location.hash = "#catalog";
  }
}

function getActivePage() {
  if (window.location.hash === "#profile") {
    return "profile";
  }
  if (window.location.hash === "#admin") {
    return "admin";
  }
  if (window.location.hash === "#generate") {
    return "generate";
  }
  return "catalog";
}

function renderPage() {
  const active = getActivePage();
  if (active === "admin" && !currentUser) {
    window.location.hash = "#catalog";
    return;
  }
  if (active === "admin" && !isAdminUser()) {
    showToast("Admin access required", true);
    window.location.hash = "#catalog";
    return;
  }

  const isCatalog = active === "catalog";
  const isGenerate = active === "generate";
  const isProfile = active === "profile";
  const isAdmin = active === "admin";
  pageCatalog.classList.toggle("active", isCatalog);
  pageGenerate.classList.toggle("active", isGenerate);
  pageProfile.classList.toggle("active", isProfile);
  pageAdmin.classList.toggle("active", isAdmin);
  navCatalog.classList.toggle("active", isCatalog);
  navGenerate.classList.toggle("active", isGenerate);
  navProfile.classList.toggle("active", isProfile);
  navAdmin.classList.toggle("active", isAdmin);

  if (isProfile && !currentUser) {
    profileStatus.textContent =
      "You are viewing public generated images. Login is required for personal profile features.";
  } else if (isProfile && currentUser) {
    profileStatus.textContent = `Signed in as ${currentUser.email}.`;
  }

  if (isAdmin && !currentUser) {
    adminStatus.textContent = "Login is required to open admin tools.";
  } else if (isAdmin && !isAdminUser()) {
    adminStatus.textContent = "Admin access required.";
  } else if (isAdmin) {
    adminStatus.textContent =
      "Create template records for images already placed in data/templates.";
  }

  const adminEnabled = isAdminUser();
  adminTemplateName.disabled = !adminEnabled;
  adminTemplateImageName.disabled = !adminEnabled;
  adminSubmit.disabled = !adminEnabled;
  adminLayoutTemplateSelect.disabled = !adminEnabled;
  adminLayoutPreviewButton.disabled = !adminEnabled;
  adminLayoutSaveButton.disabled = !adminEnabled;
  for (const field of [
    layoutTopX,
    layoutTopY,
    layoutTopWidth,
    layoutBottomX,
    layoutBottomY,
    layoutBottomWidth,
    layoutSampleTop,
    layoutSampleBottom,
  ]) {
    field.disabled = !adminEnabled;
  }
}

async function loadPreviewImage(templateId, payload) {
  if (previewRequestController) {
    previewRequestController.abort();
  }

  previewRequestController = new AbortController();
  return requestPreviewImage(
    templateId,
    payload,
    previewRequestController.signal,
  );
}

function buildGeneratePayload() {
  return {
    text_top: document.getElementById("top-text").value.trim(),
    text_bottom: document.getElementById("bottom-text").value.trim(),
    font_name: document.getElementById("font-name").value,
    font_size: Number(document.getElementById("font-size").value),
    font_color: fontColorInput.value,
  };
}

function syncFontColorUi() {
  const currentColor = fontColorInput.value.toUpperCase();
  fontColorValue.textContent = currentColor;

  for (const button of colorPresetButtons) {
    const isActive = button.dataset.color?.toUpperCase() === currentColor;
    button.classList.toggle("is-active", Boolean(isActive));
  }
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
    const blob = await loadPreviewImage(templateId, buildGeneratePayload());
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

function buildTemplateLayoutPayload() {
  return {
    top_text_x: Number(layoutTopX.value),
    top_text_y: Number(layoutTopY.value),
    top_text_width: Number(layoutTopWidth.value),
    bottom_text_x: Number(layoutBottomX.value),
    bottom_text_y: Number(layoutBottomY.value),
    bottom_text_width: Number(layoutBottomWidth.value),
  };
}

function populateAdminLayoutForm(template) {
  selectedAdminTemplateId = template?.id ?? null;
  adminLayoutTemplateSelect.value = template ? String(template.id) : "";
  layoutTopX.value = template?.top_text_x ?? "";
  layoutTopY.value = template?.top_text_y ?? "";
  layoutTopWidth.value = template?.top_text_width ?? "";
  layoutBottomX.value = template?.bottom_text_x ?? "";
  layoutBottomY.value = template?.bottom_text_y ?? "";
  layoutBottomWidth.value = template?.bottom_text_width ?? "";
}

function revokeAdminLayoutPreview() {
  if (adminLayoutPreviewObjectUrl) {
    URL.revokeObjectURL(adminLayoutPreviewObjectUrl);
    adminLayoutPreviewObjectUrl = null;
  }
}

function cancelAdminLayoutPreviewRequest() {
  if (adminLayoutPreviewDebounceTimer) {
    clearTimeout(adminLayoutPreviewDebounceTimer);
    adminLayoutPreviewDebounceTimer = null;
  }
  if (adminLayoutPreviewController) {
    adminLayoutPreviewController.abort();
    adminLayoutPreviewController = null;
  }
}

function renderAdminLayoutOptions(templates) {
  const previousTemplateId = selectedAdminTemplateId;
  adminLayoutTemplateSelect.innerHTML = "";

  if (!templates.length) {
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "No templates available";
    adminLayoutTemplateSelect.append(emptyOption);
    populateAdminLayoutForm(null);
    revokeAdminLayoutPreview();
    adminLayoutPreviewImage.removeAttribute("src");
    adminLayoutStatus.textContent =
      "Create a template first to edit text zones.";
    return;
  }

  for (const template of templates) {
    const option = document.createElement("option");
    option.value = String(template.id);
    option.textContent = `${template.name} (#${template.id})`;
    adminLayoutTemplateSelect.append(option);
  }

  const currentTemplate =
    templates.find((template) => template.id === previousTemplateId) ??
    templates[0];
  populateAdminLayoutForm(currentTemplate);
}

function renderAdminTemplates(templates) {
  adminTemplateList.innerHTML = "";
  if (!templates.length) {
    const empty = document.createElement("p");
    empty.className = "template-empty";
    empty.textContent = "No template records yet.";
    adminTemplateList.append(empty);
    return;
  }

  for (const template of templates) {
    const card = document.createElement("article");
    card.className = "admin-template-card";
    if (template.id === selectedAdminTemplateId) {
      card.classList.add("selected");
    }

    const image = document.createElement("img");
    image.src = `/templates/${template.id}/image`;
    image.alt = template.name;
    image.loading = "lazy";

    const meta = document.createElement("div");
    meta.className = "admin-template-meta";
    meta.innerHTML = `
      <p class="admin-template-title">${template.name}</p>
      <span>ID: ${template.id}</span>
      <code>${template.image_path}</code>
    `;

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "secondary compact";
    editButton.textContent = "Edit layout";
    editButton.addEventListener("click", () => {
      selectedAdminTemplateId = template.id;
      adminLayoutTemplateSelect.value = String(template.id);
      populateAdminLayoutForm(template);
      renderAdminTemplates(Array.from(templatesById.values()));
      adminLayoutStatus.textContent = `Editing layout for ${template.name}.`;
      scheduleAdminLayoutPreview(0);
    });

    meta.append(editButton);
    card.append(image, meta);
    adminTemplateList.append(card);
  }
}

function renderAdminFilePreview() {
  const selectedFile = adminTemplateImageName.files?.[0];
  if (!selectedFile) {
    if (adminPreviewObjectUrl) {
      URL.revokeObjectURL(adminPreviewObjectUrl);
      adminPreviewObjectUrl = null;
    }
    adminFilePreviewImage.removeAttribute("src");
    adminFilePreviewMeta.innerHTML =
      '<p class="template-empty">No file selected.</p>';
    adminFileStatus.innerHTML = "Choose a JPG or PNG file from your computer.";
    return;
  }

  if (adminPreviewObjectUrl) {
    URL.revokeObjectURL(adminPreviewObjectUrl);
  }
  adminPreviewObjectUrl = URL.createObjectURL(selectedFile);
  adminFilePreviewImage.src = adminPreviewObjectUrl;
  adminFilePreviewImage.alt = selectedFile.name;

  adminFilePreviewMeta.innerHTML = `
    <span class="admin-file-badge available">Ready to upload</span>
    <code>${selectedFile.name}</code>
    <span>${Math.max(1, Math.round(selectedFile.size / 1024))} KB</span>
    <span>${selectedFile.type || "Unknown type"}</span>
  `;

  adminFileStatus.innerHTML =
    "The file will be uploaded to <code>data/templates</code> and registered automatically.";
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
    img.alt = "Generated image";
    img.src = `/images/${image.share_token}`;

    const templateName =
      templatesById.get(Number(image.template_id))?.name || "Custom template";
    const createdAt = image.created_at
      ? new Date(image.created_at).toLocaleString()
      : "";

    const meta = document.createElement("div");
    meta.className = "meta";
    meta.innerHTML = `
      <strong>${templateName}</strong>
      ${createdAt ? `<span>${createdAt}</span>` : ""}
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
  renderAdminLayoutOptions(templates);
  renderAdminTemplates(templates);
  if (!templates.length) {
    generateStatus.textContent =
      "Templates are managed in admin panel. Ask admin to add one.";
  } else {
    generateStatus.textContent = "";
  }
  return templates;
}

async function previewAdminLayout() {
  if (!selectedAdminTemplateId) {
    adminLayoutStatus.textContent = "Select a template first.";
    return;
  }

  const payload = {
    ...buildTemplateLayoutPayload(),
    sample_text_top: layoutSampleTop.value.trim() || "TOP TEXT",
    sample_text_bottom: layoutSampleBottom.value.trim() || "BOTTOM TEXT",
    font_name: document.getElementById("font-name").value,
    font_size: Number(document.getElementById("font-size").value),
    font_color: fontColorInput.value,
  };

  if (adminLayoutPreviewController) {
    adminLayoutPreviewController.abort();
  }
  adminLayoutPreviewController = new AbortController();

  const res = await fetch(
    `/admin/templates/${selectedAdminTemplateId}/layout-preview`,
    {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: adminLayoutPreviewController.signal,
    },
  );
  if (!res.ok) {
    let errorDetail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      errorDetail = body?.detail ?? errorDetail;
    } catch {
      // keep fallback
    }
    throw new Error(errorDetail);
  }

  const blob = await res.blob();
  adminLayoutPreviewController = null;
  revokeAdminLayoutPreview();
  adminLayoutPreviewObjectUrl = URL.createObjectURL(blob);
  adminLayoutPreviewImage.src = adminLayoutPreviewObjectUrl;
  adminLayoutStatus.textContent = "Preview updated.";
}

function scheduleAdminLayoutPreview(delayMs = 220) {
  if (!isAdminUser() || !selectedAdminTemplateId) {
    return;
  }

  if (adminLayoutPreviewDebounceTimer) {
    clearTimeout(adminLayoutPreviewDebounceTimer);
  }

  adminLayoutPreviewDebounceTimer = setTimeout(async () => {
    try {
      await previewAdminLayout();
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      adminLayoutStatus.textContent = `Preview failed: ${error.message}`;
    }
  }, delayMs);
}

async function saveAdminLayout() {
  if (!selectedAdminTemplateId) {
    adminLayoutStatus.textContent = "Select a template first.";
    return;
  }

  const updated = await api(
    `/admin/templates/${selectedAdminTemplateId}/layout`,
    {
      method: "PATCH",
      body: JSON.stringify(buildTemplateLayoutPayload()),
    },
  );

  adminLayoutStatus.textContent = `Layout saved for ${updated.name}.`;
  await loadTemplates();
}

async function loadGeneratedImages() {
  if (!currentUser) {
    renderGeneratedImages([]);
    return;
  }

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
    fontColorInput.value = "#ffffff";
    syncFontColorUi();
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

for (const id of [
  "top-text",
  "bottom-text",
  "font-name",
  "font-size",
  "font-color",
]) {
  const field = document.getElementById(id);
  field.addEventListener("input", () => schedulePreview(220));
  field.addEventListener("change", () => schedulePreview(120));
}

fontColorInput.addEventListener("input", syncFontColorUi);

for (const button of colorPresetButtons) {
  button.addEventListener("click", () => {
    const nextColor = button.dataset.color;
    if (!nextColor) {
      return;
    }
    fontColorInput.value = nextColor;
    syncFontColorUi();
    schedulePreview(0);
  });
}

window.addEventListener("hashchange", renderPage);

navLogin.addEventListener("click", () => openAuthModal("login"));
navRegister.addEventListener("click", () => openAuthModal("register"));
navLogout.addEventListener("click", async () => {
  await logout();
  currentUser = null;
  cancelAdminLayoutPreviewRequest();
  renderGeneratedImages([]);
  renderAuthState();
  renderPage();
  renderAdminFilePreview();
  revokeAdminLayoutPreview();
  adminLayoutPreviewImage.removeAttribute("src");
  showToast("Logged out");
});
themeToggle.addEventListener("click", toggleTheme);

authClose.addEventListener("click", closeAuthModal);
authModalBackdrop.addEventListener("click", closeAuthModal);

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (
    authMode === "register" &&
    authPassword.value !== authConfirmPassword.value
  ) {
    authStatus.textContent = "Passwords do not match";
    showToast("Passwords do not match", true);
    return;
  }

  const payload = {
    email: authEmail.value.trim(),
    password: authPassword.value,
  };

  authSubmit.disabled = true;
  authSubmit.textContent =
    authMode === "login" ? "Logging in..." : "Registering...";

  try {
    const user =
      authMode === "login" ? await login(payload) : await register(payload);
    currentUser = user;
    renderAuthState();
    renderPage();
    await loadGeneratedImages();
    authPassword.value = "";
    authConfirmPassword.value = "";
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

adminTemplateForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!currentUser) {
    showToast("Login first to access admin tools", true);
    openAuthModal("login");
    return;
  }

  if (!isAdminUser()) {
    showToast("Admin access required", true);
    window.location.hash = "#catalog";
    return;
  }

  const payload = {
    name: adminTemplateName.value.trim(),
    image: adminTemplateImageName.files?.[0] ?? null,
  };

  if (!payload.image) {
    adminStatus.textContent = "Template creation failed: image file required";
    showToast("Choose an image file first", true);
    return;
  }

  adminSubmit.disabled = true;
  adminSubmit.textContent = "Creating...";

  try {
    const formData = new FormData();
    formData.append("name", payload.name);
    formData.append("image", payload.image);

    const res = await fetch("/admin/templates/upload", {
      method: "POST",
      body: formData,
      credentials: "same-origin",
    });
    if (!res.ok) {
      let errorDetail = `${res.status} ${res.statusText}`;
      try {
        const body = await res.json();
        errorDetail = body?.detail ?? errorDetail;
      } catch {
        // keep fallback text
      }
      throw new Error(errorDetail);
    }
    const created = await res.json();
    adminStatus.textContent = `Created template #${created.id}: ${created.name}`;
    adminTemplateForm.reset();
    await loadTemplates();
    populateAdminLayoutForm(created);
    adminLayoutStatus.textContent = `Template ${created.name} created. Adjust text zones below.`;
    renderAdminFilePreview();
    if (!templateSelect.value) {
      selectTemplate(created.id);
    }
    showToast(`Template "${created.name}" created`);
  } catch (error) {
    adminStatus.textContent = `Template creation failed: ${error.message}`;
    showToast(`Template creation failed: ${error.message}`, true);
  } finally {
    adminSubmit.disabled = false;
    adminSubmit.textContent = "Create template";
  }
});

adminTemplateImageName.addEventListener("change", renderAdminFilePreview);
adminLayoutTemplateSelect.addEventListener("change", () => {
  const template = templatesById.get(Number(adminLayoutTemplateSelect.value));
  populateAdminLayoutForm(template ?? null);
  renderAdminTemplates(Array.from(templatesById.values()));
  adminLayoutStatus.textContent = template
    ? `Editing layout for ${template.name}.`
    : "Select a template first.";
  if (template) {
    scheduleAdminLayoutPreview(0);
  }
});

adminLayoutPreviewButton.addEventListener("click", async () => {
  try {
    adminLayoutPreviewButton.disabled = true;
    adminLayoutPreviewButton.textContent = "Previewing...";
    await previewAdminLayout();
  } catch (error) {
    adminLayoutStatus.textContent = `Preview failed: ${error.message}`;
    showToast(`Layout preview failed: ${error.message}`, true);
  } finally {
    adminLayoutPreviewButton.disabled = false;
    adminLayoutPreviewButton.textContent = "Preview layout";
  }
});

adminLayoutSaveButton.addEventListener("click", async () => {
  try {
    adminLayoutSaveButton.disabled = true;
    adminLayoutSaveButton.textContent = "Saving...";
    await saveAdminLayout();
    showToast("Template layout saved");
  } catch (error) {
    adminLayoutStatus.textContent = `Save failed: ${error.message}`;
    showToast(`Layout save failed: ${error.message}`, true);
  } finally {
    adminLayoutSaveButton.disabled = false;
    adminLayoutSaveButton.textContent = "Save layout";
  }
});

for (const field of [
  layoutTopX,
  layoutTopY,
  layoutTopWidth,
  layoutBottomX,
  layoutBottomY,
  layoutBottomWidth,
  layoutSampleTop,
  layoutSampleBottom,
]) {
  field.addEventListener("input", () => scheduleAdminLayoutPreview(220));
  field.addEventListener("change", () => scheduleAdminLayoutPreview(80));
}

authTogglePassword.addEventListener("click", togglePasswordVisibility);

async function bootstrap() {
  applyTheme(loadStoredTheme());
  currentUser = await loadCurrentUser();
  syncFontColorUi();

  renderAuthState();
  renderPage();

  try {
    await loadTemplates();
    renderAdminFilePreview();
    await loadGeneratedImages();
  } catch (error) {
    showToast(`Load failed: ${error.message}`, true);
  }
}

bootstrap();
