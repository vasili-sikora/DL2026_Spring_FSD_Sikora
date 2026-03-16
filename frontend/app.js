const templateSelect = document.getElementById("template-select");
const templatePicker = document.getElementById("template-picker");
const templatePreviewImage = document.getElementById("template-preview-image");
const templatePreviewName = document.getElementById("template-preview-name");
const previewDownload = document.getElementById("preview-download");
const generateForm = document.getElementById("generate-form");
const generateStatus = document.getElementById("generate-status");
const generatedList = document.getElementById("generated-list");
const toast = document.getElementById("toast");
let templatesById = new Map();
let previewObjectUrl = null;
let previewDebounceTimer = null;
let previewRequestController = null;

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2600);
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
      // Keep fallback text for non-JSON responses.
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
      <a class="download-link" href="/images/${image.share_token}" download="generated-${image.id}.jpg">Download</a>
    `;
    card.append(img, meta);
    generatedList.append(card);
  }
}

async function loadTemplates() {
  const templates = await api("/templates");
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
  document
    .getElementById(id)
    .addEventListener("input", () => schedulePreview(220));
  document
    .getElementById(id)
    .addEventListener("change", () => schedulePreview(120));
}

async function bootstrap() {
  try {
    await loadTemplates();
    await loadGeneratedImages();
  } catch (error) {
    showToast(`Load failed: ${error.message}`, true);
  }
}

bootstrap();
