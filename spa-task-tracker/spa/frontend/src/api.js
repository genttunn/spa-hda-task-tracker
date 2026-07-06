import axios from 'axios'

// SPA talks to the Flask JSON API.
const api = axios.create({ baseURL: 'http://localhost:5001' })

// DEMO (issue 2): the auth token is read from localStorage on every request.
// Any JavaScript running on the page (incl. XSS or a compromised dependency)
// can read it the same way.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
