const API_BASE = '/api'

const getAuthHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const handleResponse = async (res) => {
  if (res.status === 401) {
    const data = await res.json().catch(() => ({}))
    if (data.code === 'token_not_valid' || data.detail === 'Token is invalid or expired') {
      throw new Error('Token expired')
    }
    throw new Error('未授权')
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || data.message || '请求失败')
  }
  return res.json()
}

const fetchWithAuth = async (url, options = {}) => {
  const headers = {
    ...options.headers,
    ...getAuthHeader()
  }
  const res = await fetch(url, { ...options, headers })
  return handleResponse(res)
}

export const authAPI = {
  async login(username, password) {
    const res = await fetch(`${API_BASE}/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || '登录失败')
    }
    return res.json()
  },

  async register(username, password, passwordConfirm) {
    const res = await fetch(`${API_BASE}/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, password_confirm: passwordConfirm })
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(typeof data === 'object' 
        ? Object.values(data).flat().join(', ') 
        : '注册失败')
    }
    return res.json()
  },

  async refreshToken(refresh) {
    const res = await fetch(`${API_BASE}/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    })
    if (!res.ok) {
      throw new Error('Token 刷新失败')
    }
    return res.json()
  },

  async getCurrentUser() {
    return fetchWithAuth(`${API_BASE}/me/`)
  }
}

export const teamAPI = {
  async getTeams(params = {}) {
    const query = new URLSearchParams(params).toString()
    return fetchWithAuth(`${API_BASE}/teams/?${query}`)
  },
  
  async getTeam(id) {
    return fetchWithAuth(`${API_BASE}/teams/${id}/`)
  },
  
  async createTeam(data) {
    const res = await fetch(`${API_BASE}/teams/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    })
    return handleResponse(res)
  },
  
  async updateTeam(id, data) {
    const res = await fetch(`${API_BASE}/teams/${id}/`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        ...getAuthHeader()
      },
      body: JSON.stringify(data)
    })
    return handleResponse(res)
  },
  
  async deleteTeam(id) {
    const res = await fetch(`${API_BASE}/teams/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeader()
    })
    return handleResponse(res)
  }
}

export const videoAPI = {
  async uploadVideo(file, options = {}) {
    const formData = new FormData()
    formData.append('video', file)
    if (options.startTime) formData.append('start_time', options.startTime.toString())
    if (options.duration) formData.append('duration', options.duration.toString())
    
    const res = await fetch(`${API_BASE}/videos/upload/`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: formData
    })
    return handleResponse(res)
  }
}

export const characterAPI = {
  async getCharacters() {
    const res = await fetch(`${API_BASE}/characters/`)
    if (!res.ok) throw new Error('Failed to fetch characters')
    return res.json()
  },
  
  async filterCharacters(filters) {
    const res = await fetch(`${API_BASE}/characters/filter/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters)
    })
    if (!res.ok) throw new Error('Failed to filter characters')
    return res.json()
  },
  
  async getFilterOptions() {
    const res = await fetch(`${API_BASE}/filter-options/`)
    if (!res.ok) throw new Error('Failed to fetch filter options')
    return res.json()
  }
}
