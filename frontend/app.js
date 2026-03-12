const templateSelect = document.getElementById("template-select");
const generateForm = document.getElementById("generate-form");
const generateStatus = document.getElementById("generate-status");
const generatedList = document.getElementById("generated-list");
const toast = document.getElementById("toast");

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

function renderTemplateOptions(templates) {
  templateSelect.innerHTML = "";
  if (!templates.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No templates available";
    option.disabled = true;
    option.selected = true;
    templateSelect.append(option);
    return;
  }

  for (const template of templates) {
    const option = document.createElement("option");
    option.value = template.id;
    option.textContent = `${template.id}: ${template.name}`;
    templateSelect.append(option);
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

  const payload = {
    text_top: document.getElementById("top-text").value.trim(),
    text_bottom: document.getElementById("bottom-text").value.trim(),
  };

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
    await loadGeneratedImages();
  } catch (error) {
    generateStatus.textContent = `Generate failed: ${error.message}`;
    showToast(`Generate failed: ${error.message}`, true);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Generate";
  }
});

async function bootstrap() {
  try {
    await loadTemplates();
    await loadGeneratedImages();
  } catch (error) {
    showToast(`Load failed: ${error.message}`, true);
  }
}

bootstrap();
