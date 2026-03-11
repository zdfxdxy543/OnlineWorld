const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail || JSON.stringify(body)
    } catch {
      detail = `HTTP ${response.status}`
    }
    throw new Error(`Netdisk API request failed: ${detail}`)
  }
  return response.json()
}

export function uploadGeneratedFile(payload) {
  return request('/netdisk/upload-generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function createShareLink(payload) {
  return request('/netdisk/shares', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getShareInfo(shareId, accessCode) {
  const query = new URLSearchParams({ access_code: accessCode })
  return request(`/netdisk/shares/${encodeURIComponent(shareId)}?${query.toString()}`)
}

export function listFiles(limit = 100) {
  return request(`/netdisk/files?limit=${limit}`)
}

export function getFileContent(resourceId, accessCode) {
  const query = new URLSearchParams({ access_code: accessCode })
  return request(`/netdisk/files/${encodeURIComponent(resourceId)}?${query.toString()}`)
}

export function getFileDownloadUrl(resourceId, accessCode) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
  const query = new URLSearchParams({ access_code: accessCode })
  return `${base}/netdisk/files/${encodeURIComponent(resourceId)}/download?${query.toString()}`
}
