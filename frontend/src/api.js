const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(formatApiError(data))
  }

  return data
}

function formatApiError(data) {
  if (typeof data.detail === 'string') {
    return data.detail
  }

  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail.map((error) => error.msg).join(', ')
  }

  return 'request failed'
}

export function loginUser(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function registerUser(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getAccountSummary(token) {
  return request('/account/summary', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

export function getPortfolio(token) {
  return request('/portfolio', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

export function getCurrentUser(token) {
  return request('/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}

export function getQuote(symbol) {
  return request(`/market/quote/${encodeURIComponent(symbol)}`)
}

export function buyOrder(token, payload) {
  return request('/orders/buy', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })
}

export function sellOrder(token, payload) {
  return request('/orders/sell', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })
}
