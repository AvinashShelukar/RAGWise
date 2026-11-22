
const API_BASE = '/api'

async function request(endpoint, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE}${endpoint}`, options)
  } catch {
    throw new Error(
      'Cannot connect to RAGWise backend. Make sure FastAPI is running on port 8000.'
    )
  }

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : null

  if (!response.ok) {
    throw new Error(
      data?.detail || `Request failed with status ${response.status}`
    )
  }

  return data
}

export const api = {
  // Check FastAPI availability
  health: () => request('/health'),

  // Retrieve indexed PDF filenames
  getDocuments: () => request('/documents'),

  // Upload and index a PDF
  uploadDocument: (file) => {
    const formData = new FormData()
    formData.append('file', file)

    return request('/upload', {
      method: 'POST',
      body: formData,
    })
  },

  // Ask a question about the selected PDF
  askQuestion: ({ question, top_k = 5, source = null }) =>
    request('/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        top_k,
        source,
      }),
    }),
}
