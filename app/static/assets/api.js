/* API client: same-origin fetch, CSRF header, normalized errors. */

let csrfToken = null;

export function setCsrf(token) {
  csrfToken = token || null;
}

export function getCsrf() {
  return csrfToken;
}

export class ApiError extends Error {
  constructor(message, status, code, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function parse(response) {
  const type = response.headers.get("content-type") || "";
  if (type.includes("application/json")) return response.json();
  return response.text();
}

export async function api(path, options = {}) {
  const { method = "GET", body, form, headers = {} } = options;
  const init = { method, headers: { ...headers }, credentials: "same-origin" };
  if (method !== "GET" && method !== "HEAD" && csrfToken) {
    init.headers["X-CSRF-Token"] = csrfToken;
  }
  if (form) {
    init.body = form;
  } else if (body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  const response = await fetch(path, init);
  if (response.status === 204) return null;
  const payload = await parse(response);
  if (!response.ok) {
    const error = payload && payload.error ? payload.error : {};
    throw new ApiError(
      error.message || response.statusText || "Request failed",
      response.status,
      error.code || "request_failed",
      error.details,
    );
  }
  return payload;
}

export async function apiBlob(path) {
  const response = await fetch(path, { credentials: "same-origin" });
  if (!response.ok) {
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }
    const detail = payload && payload.error ? payload.error : {};
    throw new ApiError(
      detail.message || response.statusText || "Download failed",
      response.status,
      detail.code || "download_failed",
    );
  }
  return response.blob();
}
