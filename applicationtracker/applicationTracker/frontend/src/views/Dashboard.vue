<template>
  <div id="app" class="container">
    <header class="dashboard-header">
      <h1>Application Tracker</h1>
      <button @click="logout" class="brutal-btn outline-btn">Logout</button>
    </header>

    <main>
      <!-- Custom Toast Notifications -->
      <div v-if="toastMessage" :class="['toast-notification', toastType]">
        {{ toastMessage }}
        <button @click="closeToast" class="toast-close">&times;</button>
      </div>

      <section class="stats-section">
        <div class="stat-cards">
          <div class="stat-card brutal-card">
            <h3>Total Applied</h3>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
          <div class="stat-card brutal-card">
            <h3>Interview Rate</h3>
            <div class="stat-value">{{ stats.interviewRate }}%</div>
          </div>
        </div>
        <div class="heatmap-card brutal-card">
          <h3>Activity Heatmap</h3>
          <div class="heatmap-container">
            <div class="heatmap-grid">
              <div 
                v-for="day in heatmapDays" 
                :key="day.date" 
                class="heatmap-cell"
                :class="getHeatmapColor(day.count)"
                :title="day.count >= 0 ? `${day.count} applications on ${day.date}` : ''"
              ></div>
            </div>
          </div>
        </div>
      </section>

      <section class="form-section brutal-card">
        <h2>Add New Application</h2>
        <form @submit.prevent="submitApplication" class="app-form" novalidate>
          <div class="form-group">
            <label>Company *</label>
            <input v-model="newApp.company" placeholder="e.g. Google" class="brutal-input" :class="{'input-error': validationErrors.company}" />
            <span class="error-msg" v-if="validationErrors.company">{{ validationErrors.company }}</span>
          </div>
          <div class="form-group">
            <label>Position *</label>
            <input v-model="newApp.position" placeholder="e.g. Software Engineer" class="brutal-input" :class="{'input-error': validationErrors.position}" />
            <span class="error-msg" v-if="validationErrors.position">{{ validationErrors.position }}</span>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="newApp.status" class="brutal-input">
              <option value="Applied">Applied</option>
              <option value="Interviewing">Interviewing</option>
              <option value="Offer">Offer</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
          <div class="form-group">
            <label>Link (URL)</label>
            <input v-model="newApp.url" placeholder="https://..." class="brutal-input" :class="{'input-error': validationErrors.url}" type="url" />
            <span class="error-msg" v-if="validationErrors.url">{{ validationErrors.url }}</span>
          </div>
          <div class="form-group">
            <label>Screenshot</label>
            <input type="file" @change="handleFileUpload" accept="image/png, image/jpeg" class="brutal-input" />
          </div>
          <div class="form-group">
            <label>Cover Letter (PDF)</label>
            <input type="file" @change="handleCoverLetterUpload" accept="application/pdf" class="brutal-input" />
          </div>
          <div class="form-group-btn">
            <button type="submit" class="brutal-btn primary-btn">Save Application</button>
          </div>
        </form>
      </section>

      <section class="list-section brutal-card">
        <div class="list-header">
          <h2>My Applications</h2>
          <div class="filter-bar" v-if="applications.length > 0">
            <input 
              v-model="searchQuery" 
              placeholder="Search company or role..." 
              class="brutal-input search-input" 
            />
            <select v-model="statusFilter" class="brutal-input">
              <option value="">All Statuses</option>
              <option value="Applied">Applied</option>
              <option value="Interviewing">Interviewing</option>
              <option value="Offer">Offer</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
        </div>

        <div v-if="applications.length === 0" class="empty-state">
          You haven't added any applications yet.
        </div>
        <div v-else-if="filteredApplications.length === 0" class="empty-state">
          No applications match your search criteria.
        </div>
        <div v-else class="table-responsive">
          <table class="app-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Position</th>
                <th>Status</th>
                <th>Date Applied</th>
                <th>Link / Media</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody v-for="app in filteredApplications" :key="app.id">
              <tr>
                <td data-label="Company"><strong class="truncate-2-lines" :title="app.company">{{ app.company }}</strong></td>
                <td data-label="Position">
                  <div class="truncate-2-lines" :title="app.position">{{ app.position }}</div>
                </td>
                <td data-label="Status">
                  <span :class="['status-badge', app.status.toLowerCase()]">{{ app.status }}</span>
                </td>
                <td data-label="Date Applied"><strong>{{ formatDate(app.date_applied) }}</strong></td>
                <td data-label="Links / Media">
                  <div class="media-links">
                    <a v-if="app.url" :href="app.url" target="_blank" class="brutal-link">Link</a>
                    <a v-if="app.screenshot_path" :href="getMediaUrl(app.screenshot_path)" target="_blank" class="brutal-link img-link">Image</a>
                    <a v-if="app.cover_letter_path" :href="getMediaUrl(app.cover_letter_path)" target="_blank" class="brutal-link doc-link">Cover Letter</a>
                    <button v-if="app.page_content" @click="toggleContent(app.id)" class="brutal-link toggle-btn">
                      {{ expandedRow === app.id ? 'Hide Content' : 'Read Content' }}
                    </button>
                  </div>
                </td>
                <td data-label="Actions">
                  <button @click="deleteApplication(app.id)" class="brutal-btn danger-btn small-btn">Delete</button>
                </td>
              </tr>
              <tr v-if="expandedRow === app.id" class="expanded-row">
                <td colspan="6">
                  <div class="content-panel">
                    <h4>Fetched Job Description:</h4>
                    <div class="fetched-html" v-html="app.page_content"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- Custom Modal for Delete Confirmation -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-content brutal-card">
        <h3>Delete Application</h3>
        <p>Are you sure you want to delete this application? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="closeDeleteModal" class="brutal-btn outline-btn">Cancel</button>
          <button @click="confirmDeleteApplication" class="brutal-btn danger-btn">Yes, Delete</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const applications = ref([])
const expandedRow = ref(null)
const searchQuery = ref('')
const statusFilter = ref('')
const showDeleteModal = ref(false)
const appToDelete = ref(null)

const toastMessage = ref('')
const toastType = ref('error') // 'error' or 'success'
let toastTimeout = null

const showToast = (message, type = 'error') => {
  toastMessage.value = message
  toastType.value = type
  
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => {
    closeToast()
  }, 5000)
}

const closeToast = () => {
  toastMessage.value = ''
}

const stats = computed(() => {
  const total = applications.value.length
  if (total === 0) return { total: 0, interviewRate: 0 }
  
  const interviews = applications.value.filter(app => app.status === 'Interviewing' || app.status === 'Offer').length
  return {
    total,
    interviewRate: Math.round((interviews / total) * 100)
  }
})

const heatmapDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0,0,0,0)
  
  const counts = {}
  applications.value.forEach(app => {
    if (!app.date_applied) return
    const d = new Date(app.date_applied)
    const dateStr = d.toISOString().split('T')[0]
    counts[dateStr] = (counts[dateStr] || 0) + 1
  })

  // Start from 25 weeks ago (175 days)
  const numDays = 175
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - numDays + 1)
  
  // Pad the beginning so the first day aligns with Sunday (0)
  const startDayOfWeek = startDate.getDay()
  for (let i = 0; i < startDayOfWeek; i++) {
    days.push({ date: `empty-${i}`, count: -1 })
  }

  for (let i = numDays - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    days.push({
      date: dateStr,
      count: counts[dateStr] || 0
    })
  }
  return days
})

const getHeatmapColor = (count) => {
  if (count < 0) return 'heatmap-empty'
  if (count === 0) return 'heatmap-level-0'
  if (count === 1) return 'heatmap-level-1'
  if (count === 2) return 'heatmap-level-2'
  if (count === 3) return 'heatmap-level-3'
  return 'heatmap-level-4'
}

const filteredApplications = computed(() => {
  return applications.value.filter(app => {
    const matchesSearch = app.company.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          app.position.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = statusFilter.value === '' || app.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

const newApp = ref({
  company: '',
  position: '',
  status: 'Applied',
  url: ''
})
const validationErrors = ref({
  company: '',
  position: '',
  url: ''
})
const selectedFile = ref(null)
const selectedCoverLetter = ref(null)

const toggleContent = (id) => {
  expandedRow.value = expandedRow.value === id ? null : id
}

const logout = () => {
  localStorage.removeItem('authToken')
  router.push('/login')
}

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0]
}

const handleCoverLetterUpload = (event) => {
  selectedCoverLetter.value = event.target.files[0]
}

const getMediaUrl = (path) => {
  return `/uploads/${path}`
}

const fetchApplications = async () => {
  try {
    const res = await fetch('/api/applications/')
    applications.value = await res.json()
  } catch (error) {
    console.error("Error fetching applications:", error)
    showToast("Failed to load applications.", "error")
  }
}

const submitApplication = async (event) => {
  // Clear previous errors
  validationErrors.value = { company: '', position: '', url: '' }
  let hasErrors = false

  // Custom form validation
  if (!newApp.value.company || !newApp.value.company.trim()) {
    validationErrors.value.company = "Bitte fülle dieses Feld aus."
    hasErrors = true
  }
  if (!newApp.value.position || !newApp.value.position.trim()) {
    validationErrors.value.position = "Bitte fülle dieses Feld aus."
    hasErrors = true
  }
  
  if (newApp.value.url && !newApp.value.url.startsWith('http')) {
    validationErrors.value.url = "Bitte gib eine gültige URL ein (http/https)."
    hasErrors = true
  }

  if (hasErrors) {
    showToast("Please fix the errors in the form.", "error")
    return
  }

  try {
    const formData = new FormData()
    formData.append('company', newApp.value.company)
    formData.append('position', newApp.value.position)
    formData.append('status', newApp.value.status)
    if (newApp.value.url) formData.append('url', newApp.value.url)
    if (selectedFile.value) formData.append('screenshot', selectedFile.value)
    if (selectedCoverLetter.value) formData.append('cover_letter', selectedCoverLetter.value)

    const res = await fetch('/api/applications/', {
      method: 'POST',
      body: formData
    })
    
    if (res.ok) {
      const addedApp = await res.json()
      applications.value.unshift(addedApp)
      // Reset form
      newApp.value = { company: '', position: '', status: 'Applied', url: '' }
      selectedFile.value = null
      selectedCoverLetter.value = null
      event.target.reset() // reset file input
      
      showToast("Application added successfully!", "success")
    } else {
      const data = await res.json()
      showToast(data.error || "Failed to save application.", "error")
    }
  } catch (error) {
    console.error("Error adding application:", error)
    showToast("Server connection failed.", "error")
  }
}

const deleteApplication = (id) => {
  appToDelete.value = id
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  appToDelete.value = null
}

const confirmDeleteApplication = async () => {
  if (!appToDelete.value) return
  
  const id = appToDelete.value
  try {
    const res = await fetch(`/api/applications/${id}`, { method: 'DELETE' })
    if (res.ok) {
      applications.value = applications.value.filter(app => app.id !== id)
      closeDeleteModal()
      showToast("Application deleted.", "success")
    } else {
      showToast("Failed to delete application.", "error")
    }
  } catch (error) {
    console.error("Error deleting application:", error)
    showToast("Server connection failed.", "error")
  }
}

const formatDate = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  padding: 1rem;
  background-color: var(--card-bg);
  border: 3px solid var(--text-main);
  border-radius: 12px;
  box-shadow: 6px 6px 0px var(--text-main);
}

header h1 {
  color: var(--primary-color);
  margin-bottom: 0;
  font-size: 1.8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-shadow: 2px 2px 0px var(--secondary-color);
}

@media (max-width: 600px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  header h1 {
    font-size: 1.5rem;
  }
  .brutal-card {
    padding: 0.75rem;
  }
}

.stats-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

@media (min-width: 850px) {
  .stats-section {
    flex-direction: row;
  }
}

.stat-cards {
  display: flex;
  flex: 1;
  min-width: 250px;
  gap: 1.5rem;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 0;
  padding: 1.5rem;
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-main);
  text-transform: uppercase;
  border-bottom: none;
  padding-bottom: 0;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--primary-color);
  text-shadow: 2px 2px 0px var(--secondary-color);
}

.heatmap-card {
  flex: 1;
  min-width: 300px;
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}

.heatmap-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  text-transform: uppercase;
  border-bottom: 3px solid var(--text-main);
  padding-bottom: 0.5rem;
}

.heatmap-container {
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 1fr);
  grid-auto-flow: column;
  gap: 4px;
  width: max-content;
}

.heatmap-cell {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  border: 2px solid var(--text-main);
}

.heatmap-empty {
  border: none;
  background: transparent;
}

.heatmap-level-0 { background-color: #f1f5f9; }
.heatmap-level-1 { background-color: #bbf7d0; } 
.heatmap-level-2 { background-color: #4ade80; } 
.heatmap-level-3 { background-color: #16a34a; } 
.heatmap-level-4 { background-color: #14532d; } 

@media (max-width: 600px) {
  .stat-cards {
    flex-direction: column;
  }
}

.brutal-card {
  background-color: var(--card-bg);
  border: 3px solid var(--text-main);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 8px 8px 0px var(--primary-color);
  margin-bottom: 2.5rem;
}

h2 {
  margin-top: 0;
  font-size: 1.4rem;
  color: var(--text-main);
  font-weight: 800;
  text-transform: uppercase;
  border-bottom: 3px solid var(--text-main);
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
}

.list-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.list-header h2 {
  margin-bottom: 0;
}

@media (min-width: 600px) {
  .list-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: flex-end;
  }
}

.filter-bar {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.app-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  align-items: flex-end;
}

.form-group {
  flex: 1;
  min-width: 220px;
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.brutal-input {
  padding: 0.8rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
  border: 3px solid var(--text-main);
  border-radius: 8px;
  background-color: #fff;
  transition: all 0.2s ease-in-out;
  outline: none;
}

.brutal-input:focus {
  border-color: var(--primary-color);
  box-shadow: 4px 4px 0px var(--secondary-color);
  transform: translate(-2px, -2px);
}

.brutal-input.input-error {
  border-color: #ef4444; /* red */
  background-color: #fef2f2;
}

.brutal-input.input-error:focus {
  box-shadow: 4px 4px 0px #ef4444;
}

.error-msg {
  display: block;
  color: #ef4444;
  font-size: 0.8rem;
  font-weight: 800;
  margin-top: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}

.form-group-btn {
  display: flex;
}

.brutal-btn {
  cursor: pointer;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 3px solid var(--text-main);
  border-radius: 8px;
  transition: all 0.1s ease-in-out;
  box-shadow: 4px 4px 0px var(--text-main);
}

.brutal-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px var(--text-main);
}

.brutal-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px var(--text-main);
}

.primary-btn {
  background-color: var(--primary-color);
  color: #fff;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
}

.primary-btn:hover {
  background-color: var(--primary-hover);
}

.danger-btn {
  background-color: #ff4757;
  color: #fff;
}

.danger-btn:hover {
  background-color: #ff6b81;
}

.outline-btn {
  background-color: transparent;
  color: var(--text-main);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.outline-btn:hover {
  background-color: #ff4757;
  color: #fff;
}

.small-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  box-shadow: 3px 3px 0px var(--text-main);
}

.small-btn:hover {
  box-shadow: 5px 5px 0px var(--text-main);
}

.small-btn:active {
  box-shadow: 1px 1px 0px var(--text-main);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-weight: 700;
  border: 3px dashed var(--text-main);
  border-radius: 8px;
}

.app-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border: 3px solid var(--text-main);
  border-radius: 8px;
  overflow: hidden;
  table-layout: fixed;
}

@media (max-width: 850px) {
  .app-table {
    border: none;
    border-radius: 0;
    background: transparent;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
    align-items: start;
    overflow: visible; /* Prevent box-shadows from being clipped */
  }
  
  .app-table thead {
    display: none;
  }

  .app-table tbody {
    /* The tbody is now the Card wrapper so both main fields and expanded content stay together */
    border: 3px solid var(--text-main) !important;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 6px 6px 0px var(--text-main) !important;
    display: flex;
    flex-direction: column;
    width: 100% !important;
    box-sizing: border-box;
    overflow: hidden;
  }

  .app-table tr {
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    display: flex;
    flex-direction: column;
    width: 100% !important;
    box-sizing: border-box;
    margin: 0 !important;
  }

  .app-table td {
    padding: 0.6rem 1rem;
    text-align: left;
    position: relative;
    border: none !important;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    min-height: auto;
    width: 100% !important;
    box-sizing: border-box;
  }

  .app-table td::before {
    content: attr(data-label);
    position: static;
    font-weight: 800;
    text-transform: uppercase;
    font-size: 0.75rem;
    color: var(--text-main);
    opacity: 0.7;
    margin-bottom: 0.4rem;
    text-shadow: none;
    letter-spacing: 0.05em;
  }

  /* Specific styles for the expanded content row in mobile */
  .app-table tr.expanded-row td {
    border-top: 3px solid var(--text-main) !important;
    background-color: #f8fafc;
    padding: 1rem;
  }
  
  /* Hide the pseudo-label for the expanded content td */
  .app-table tr.expanded-row td::before {
    display: none;
  }

  .app-table td:last-child {
    border-bottom: none;
    background-color: transparent;
    padding-top: 1rem;
    padding-bottom: 1.2rem;
  }
}

.table-responsive {
  width: 100%;
  overflow-x: visible; /* Hide horizontal scroll if grid items wrap */
  padding-bottom: 1rem; /* Add padding so shadows on the bottom aren't clipped by the container */
  padding-right: 1rem;
}

.app-table th, .app-table td {
  padding: 0.75rem;
  text-align: left;
  vertical-align: top;
  border-bottom: 3px solid var(--text-main);
  border-right: 3px solid var(--text-main);
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  hyphens: auto;
  box-sizing: border-box;
}

.app-table th:nth-child(1) { width: 16%; }
.app-table th:nth-child(2) { width: 18%; }
.app-table th:nth-child(3) { width: 14%; }
.app-table th:nth-child(4) { width: 14%; }
.app-table th:nth-child(5) { width: 24%; }
.app-table th:nth-child(6) { width: 14%; }

@media (max-width: 850px) {
  .media-links {
    justify-content: flex-start;
    gap: 0.5rem;
  }

  .truncate-2-lines {
    text-align: left;
  }
  
  .app-table tr:last-child td {
    border-bottom: none !important;
  }
}

.truncate-2-lines {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  max-width: 100%;
}

.media-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.app-table th:last-child, .app-table td:last-child {
  border-right: none;
}

.app-table tr:last-child td {
  border-bottom: 3px solid var(--text-main);
}
.app-table tr:last-child td:last-child {
  border-bottom: none;
}

.app-table th {
  font-weight: 800;
  color: var(--text-main);
  background-color: var(--secondary-color);
  text-transform: uppercase;
}

.app-table td {
  background-color: #fff;
  color: var(--text-main);
}

.status-badge {
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  border: 2px solid var(--text-main);
  display: inline-block;
  box-shadow: 2px 2px 0px var(--text-main);
}

.status-badge.applied { background-color: #e0e7ff; color: #3730a3; }
.status-badge.interviewing { background-color: #fef08a; color: #854d0e; }
.status-badge.offer { background-color: #bbf7d0; color: #166534; }
.status-badge.rejected { background-color: #fecaca; color: #991b1b; }

.brutal-link {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  margin-right: 0.5rem;
  background-color: #fff;
  border: 2px solid var(--text-main);
  border-radius: 4px;
  color: var(--text-main);
  font-weight: 800;
  text-decoration: none;
  font-size: 0.8rem;
  text-transform: uppercase;
  box-shadow: 2px 2px 0px var(--text-main);
  transition: all 0.1s ease;
}
.brutal-link:hover {
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0px var(--text-main);
  background-color: var(--primary-color);
  color: #fff;
}
.img-link:hover {
  background-color: #f59e0b; /* yellow */
}
.doc-link:hover {
  background-color: #3b82f6; /* blue */
  color: #fff;
}
.toggle-btn {
  cursor: pointer;
  background-color: var(--secondary-color);
  color: var(--text-main);
  border: 2px solid var(--text-main);
  outline: none;
  font-family: inherit;
}
.toggle-btn:hover {
  background-color: var(--text-main);
  color: #fff;
}
.notes-preview small {
  color: #64748b;
}
.expanded-row td {
  background-color: #f8fafc;
  border-top: none;
}
.content-panel {
  padding: 1rem;
  background-color: #fff;
  border: 3px solid var(--text-main);
  border-radius: 8px;
  box-shadow: 4px 4px 0px var(--text-main);
}
@media (max-width: 850px) {
  .content-panel {
    border: none;
    box-shadow: none;
    padding: 0;
    background-color: transparent;
  }
}
.content-panel h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--primary-color);
}
.fetched-html {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-main);
  max-height: 500px;
  overflow-y: auto;
  margin: 0;
  padding: 1rem;
  background-color: #f8fafc;
  border: 2px solid var(--text-main);
  border-radius: 4px;
}
.fetched-html :deep(h1),
.fetched-html :deep(h2),
.fetched-html :deep(h3),
.fetched-html :deep(h4) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}
.fetched-html :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}
.fetched-html :deep(ul),
.fetched-html :deep(ol) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}
.fetched-html :deep(p) {
  margin-bottom: 1rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--bg-color);
  width: 90%;
  max-width: 400px;
  text-align: center;
}

.modal-content h3 {
  margin-top: 0;
  color: var(--primary-color);
  font-weight: 800;
  text-transform: uppercase;
}

.modal-content p {
  color: var(--text-main);
  margin-bottom: 2rem;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.modal-actions .brutal-btn {
  flex: 1;
}

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1100;
  padding: 1rem 3rem 1rem 1.5rem;
  border-radius: 8px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 3px solid var(--text-main);
  box-shadow: 6px 6px 0px var(--text-main);
  animation: slide-down 0.3s ease-out forwards;
  max-width: 90%;
  text-align: center;
}

.toast-notification.error {
  background-color: #fee2e2;
  color: #b91c1c;
}

.toast-notification.success {
  background-color: #dcfce3;
  color: #166534;
}

.toast-close {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  font-size: 1.5rem;
  font-weight: bold;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
}

.toast-close:hover {
  opacity: 1;
}

@keyframes slide-down {
  0% { top: -100px; opacity: 0; }
  100% { top: 20px; opacity: 1; }
}

</style>
