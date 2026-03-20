export function extractErrorDetail(body, fallback) {
  if (!body || body.detail == null) {
    return fallback;
  }
  if (typeof body.detail === "string") {
    return body.detail;
  }
  if (Array.isArray(body.detail) && body.detail.length) {
    const first = body.detail[0];
    if (first && typeof first === "object" && typeof first.msg === "string") {
      return first.msg;
    }
  }
  return JSON.stringify(body.detail);
}

export async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const res = await fetch(path, {
    ...options,
    headers,
    credentials: "same-origin",
  });
  if (!res.ok) {
    let errorDetail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      errorDetail = extractErrorDetail(body, errorDetail);
    } catch {
      // keep fallback text
    }
    throw new Error(errorDetail);
  }
  return res.json();
}

export async function requestPreviewImage(templateId, payload, signal) {
  const res = await fetch(`/templates/${templateId}/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
    credentials: "same-origin",
  });

  if (!res.ok) {
    let errorDetail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      errorDetail = extractErrorDetail(body, errorDetail);
    } catch {
      // keep fallback
    }
    throw new Error(errorDetail);
  }

  return res.blob();
}
