const API_BASE = '/api'

export const teamAPI = {
  // 获取配队列表（支持分页和筛选）
  async getTeams(params = {}) {
    const query = new URLSearchParams(params).toString()
    const res = await fetch(`${API_BASE}/teams/?${query}`)
    if (!res.ok) throw new Error('Failed to fetch teams')
    return res.json()
  },
  
  // 获取配队详情
  async getTeam(id) {
    const res = await fetch(`${API_BASE}/teams/${id}/`)
    if (!res.ok) throw new Error('Failed to fetch team')
    return res.json()
  },
  
  // 创建配队
  async createTeam(data) {
    const res = await fetch(`${API_BASE}/teams/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to create team')
    return res.json()
  },
  
  // 更新配队
  async updateTeam(id, data) {
    const res = await fetch(`${API_BASE}/teams/${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error('Failed to update team')
    return res.json()
  },
  
  // 删除配队
  async deleteTeam(id) {
    const res = await fetch(`${API_BASE}/teams/${id}/`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('Failed to delete team')
    return true
  }
}

export const videoAPI = {
  // 上传视频（支持裁剪）
  async uploadVideo(file, options = {}) {
    const formData = new FormData()
    formData.append('video', file)
    if (options.startTime) formData.append('start_time', options.startTime.toString())
    if (options.duration) formData.append('duration', options.duration.toString())
    
    const res = await fetch(`${API_BASE}/videos/upload/`, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('Failed to upload video')
    return res.json()
  }
}

export const characterAPI = {
  // 获取角色列表
  async getCharacters() {
    const res = await fetch(`${API_BASE}/characters/`)
    if (!res.ok) throw new Error('Failed to fetch characters')
    return res.json()
  },
  
  // 筛选角色
  async filterCharacters(filters) {
    const res = await fetch(`${API_BASE}/characters/filter/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters)
    })
    if (!res.ok) throw new Error('Failed to filter characters')
    return res.json()
  },
  
  // 获取筛选选项
  async getFilterOptions() {
    const res = await fetch(`${API_BASE}/filter-options/`)
    if (!res.ok) throw new Error('Failed to fetch filter options')
    return res.json()
  }
}
