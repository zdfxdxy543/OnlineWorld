const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

export async function getMainPage(slug) {
  const response = await fetch(`${API_BASE_URL}/main-pages/pages/${encodeURIComponent(slug)}`)
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('PAGE_NOT_FOUND')
    }
    throw new Error(`API request failed: ${response.status}`)
  }
  return response.json()
}

export function buildPageSrcDoc(page) {
  const html = String(page?.html_content || '').trim()
  const assets = Array.isArray(page?.assets) ? page.assets : []

  if (!html) {
    return '<!doctype html><html><body><h1>Empty page</h1></body></html>'
  }

  const headAssets = assets
    .filter((asset) => asset && typeof asset === 'object')
    .map((asset) => {
      const path = String(asset.path || '').toLowerCase()
      const content = String(asset.content || '')
      const contentType = String(asset.content_type || 'text/plain').toLowerCase()

      if (!content) {
        return ''
      }
      if (contentType.includes('css') || path.endsWith('.css')) {
        return `<style data-path="${escapeHtmlAttribute(path)}">${content}</style>`
      }
      return ''
    })
    .join('')

  const bodyAssets = assets
    .filter((asset) => asset && typeof asset === 'object')
    .map((asset) => {
      const path = String(asset.path || '').toLowerCase()
      const content = String(asset.content || '')
      const contentType = String(asset.content_type || 'text/plain').toLowerCase()

      if (!content) {
        return ''
      }
      if (contentType.includes('javascript') || path.endsWith('.js')) {
        return `<script data-path="${escapeHtmlAttribute(path)}">${content}</script>`
      }
      return ''
    })
    .join('')

  const baseTag = '<base href="/" />'
  const hasHead = /<head[\s>]/i.test(html)
  const hasBody = /<body[\s>]/i.test(html)

  let output = html
  if (hasHead) {
    output = output.replace(/<head(.*?)>/i, `<head$1>${baseTag}${headAssets}`)
  } else {
    output = output.replace(/<html(.*?)>/i, `<html$1><head>${baseTag}${headAssets}</head>`)
  }

  if (bodyAssets) {
    if (hasBody) {
      output = output.replace(/<\/body>/i, `${bodyAssets}</body>`)
    } else {
      output += `<body>${bodyAssets}</body>`
    }
  }

  return output
}

function escapeHtmlAttribute(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
