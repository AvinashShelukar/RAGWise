
import { useEffect, useState } from 'react'
import {
  Activity,
  BookOpen,
  FileText,
  FolderOpen,
  LayoutDashboard,
  MessageSquare,
  Plus,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Upload,
  Wifi,
  WifiOff,
} from 'lucide-react'

import { api } from './services/api'
import './App.css'

function App() {
  const [documents, setDocuments] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking')
  const [selectedDocument, setSelectedDocument] = useState('')
  const [loadingDocuments, setLoadingDocuments] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState('')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [asking, setAsking] = useState(false)
  const [topK, setTopK] = useState(5)

  async function loadDocuments() {
    setLoadingDocuments(true)

    try {
      const data = await api.getDocuments()
      setDocuments(data.documents || [])
    } catch (error) {
      console.error('Could not load documents:', error)
    } finally {
      setLoadingDocuments(false)
    }
  }

  async function checkBackend() {
    try {
      await api.health()
      setBackendStatus('online')
    } catch {
      setBackendStatus('offline')
    }
  }

  useEffect(() => {
    checkBackend()
    loadDocuments()
  }, [])

  async function handleUpload(event) {
    const file = event.target.files?.[0]
    event.target.value = ''

    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('Please select a PDF file.')
      return
    }

    setUploading(true)
    setUploadMessage('Uploading and indexing PDF...')

    try {
      const result = await api.uploadDocument(file)
      await loadDocuments()
      setUploadMessage(result.message || 'PDF indexed successfully.')
      setSelectedDocument(result.filename || '')
      checkBackend()
    } catch (error) {
      setUploadMessage(error.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleAsk(event) {
    event.preventDefault()

    const trimmedQuestion = question.trim()
    if (!trimmedQuestion || asking) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: trimmedQuestion,
    }

    setMessages((previous) => [...previous, userMessage])
    setQuestion('')
    setAsking(true)

    try {
      const result = await api.askQuestion({
        question: trimmedQuestion,
        top_k: topK,
        source: selectedDocument || null,
      })

      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: result.answer || 'No answer was returned.',
          citations: result.citations || [],
        },
      ])
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: Date.now() + 1,
          role: 'error',
          content: error.message,
        },
      ])
    } finally {
      setAsking(false)
    }
  }

  function askSuggestion(value) {
    setQuestion(value)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <BookOpen size={21} />
          </div>
          <div>
            <div className="brand-name">RAGWISE<span>.</span></div>
            <div className="brand-caption">RESEARCH INTELLIGENCE</div>
          </div>
        </div>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          <button className="nav-item active">
            <LayoutDashboard size={17} />
            <span>Overview</span>
          </button>
          <button className="nav-item">
            <MessageSquare size={17} />
            <span>Research chat</span>
          </button>
          <button className="nav-item">
            <FolderOpen size={17} />
            <span>Document library</span>
            <span className="nav-count">{documents.length}</span>
          </button>
        </nav>

        <div className="sidebar-section">
          <div className="sidebar-section-heading">
            <span className="sidebar-label">YOUR DOCUMENTS</span>
            <label className="icon-button" title="Upload PDF">
              <Plus size={16} />
              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleUpload}
                disabled={uploading}
                hidden
              />
            </label>
          </div>

          <div className="document-list">
            {loadingDocuments ? (
              <div className="empty-sidebar">Loading documents...</div>
            ) : documents.length === 0 ? (
              <div className="empty-sidebar">No PDFs indexed yet.</div>
            ) : (
              documents.map((document) => (
                <button
                  key={document}
                  className={`document-item ${
                    selectedDocument === document ? 'selected' : ''
                  }`}
                  onClick={() => setSelectedDocument(
                    selectedDocument === document ? '' : document
                  )}
                  title={document}
                >
                  <FileText size={16} />
                  <span>{document}</span>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="backend-card">
            <div className="backend-card-top">
              <Activity size={16} />
              <span>BACKEND STATUS</span>
            </div>
            <div className="backend-status">
              <span className={`status-dot ${backendStatus}`} />
              {backendStatus === 'online'
                ? 'API connected'
                : backendStatus === 'offline'
                  ? 'API disconnected'
                  : 'Checking connection'}
            </div>
            <div className="backend-note">
              FastAPI · localhost:8000
            </div>
          </div>

          <button className="nav-item settings-item">
            <Settings2 size={17} />
            <span>Settings</span>
          </button>

          <div className="sidebar-footer">
            <ShieldCheck size={14} />
            LOCAL DOCUMENT PROCESSING
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Overview</strong>
          </div>

          <div className="topbar-right">
            <div className="local-badge">
              <span className="status-dot online" />
              LOCAL ENVIRONMENT
            </div>
            <div className="avatar">AS</div>
          </div>
        </header>

        <div className="dashboard-content">
          <section className="welcome-section">
            <div>
              <div className="eyebrow">
                <Sparkles size={14} />
                YOUR PERSONAL RESEARCH ASSISTANT
              </div>
              <h1>Think deeper.<br /><span>Research smarter.</span></h1>
              <p>
                Explore your research papers, retrieve meaningful insights,
                and get evidence-backed answers from your documents.
              </p>
            </div>

            <div className="welcome-decoration">
              <div className="decoration-ring ring-one" />
              <div className="decoration-ring ring-two" />
              <div className="decoration-center">
                <BookOpen size={37} />
              </div>
              <span className="decoration-label">RAG / AI</span>
            </div>
          </section>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon"><FolderOpen size={19} /></div>
              <div className="stat-label">INDEXED DOCUMENTS</div>
              <div className="stat-value">{documents.length}</div>
              <div className="stat-foot">PDF files available</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon"><MessageSquare size={19} /></div>
              <div className="stat-label">CONVERSATION</div>
              <div className="stat-value">{messages.length}</div>
              <div className="stat-foot">Messages this session</div>
            </div>

            <div className="stat-card">
              <div className="stat-icon"><Activity size={19} /></div>
              <div className="stat-label">API CONNECTION</div>
              <div className="stat-value stat-value-small">
                {backendStatus === 'online'
                  ? 'Online'
                  : backendStatus === 'offline'
                    ? 'Offline'
                    : 'Checking'}
              </div>
              <div className="stat-foot">FastAPI service status</div>
            </div>
          </section>

          <section className="workspace-grid">
            <div className="chat-card">
              <div className="panel-header">
                <div>
                  <div className="panel-eyebrow">INTERACTIVE WORKSPACE</div>
                  <h2>Research assistant</h2>
                </div>
                <div className="chat-live">
                  <span className="status-dot online" />
                  READY
                </div>
              </div>

              <div className="chat-context">
                <div className="context-icon"><FileText size={16} /></div>
                <div className="context-details">
                  <span>SEARCHING IN</span>
                  <strong>
                    {selectedDocument || 'All available documents'}
                  </strong>
                </div>
                <select
                  value={selectedDocument}
                  onChange={(event) => setSelectedDocument(event.target.value)}
                  aria-label="Select document"
                >
                  <option value="">All documents</option>
                  {documents.map((document) => (
                    <option key={document} value={document}>
                      {document}
                    </option>
                  ))}
                </select>
              </div>

              <div className="messages-area">
                {messages.length === 0 ? (
                  <div className="chat-empty">
                    <div className="chat-empty-icon">
                      <Sparkles size={23} />
                    </div>
                    <h3>Your research starts here.</h3>
                    <p>
                      Ask a question about your PDFs. RAGWise will retrieve
                      relevant passages and generate an answer with citations.
                    </p>

                    <div className="suggestion-list">
                      <button onClick={() => askSuggestion(
                        'Summarize the main findings of this paper.'
                      )}>
                        <Search size={15} />
                        Summarize the main findings
                      </button>
                      <button onClick={() => askSuggestion(
                        'What research gaps are identified in this document?'
                      )}>
                        <Search size={15} />
                        Identify research gaps
                      </button>
                      <button onClick={() => askSuggestion(
                        'Explain the methodology used in this paper.'
                      )}>
                        <Search size={15} />
                        Explain the methodology
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="message-list">
                    {messages.map((message) => (
                      <article
                        className={`message ${message.role}`}
                        key={message.id}
                      >
                        <div className="message-role">
                          {message.role === 'user'
                            ? 'YOU'
                            : message.role === 'error'
                              ? 'ERROR'
                              : 'RAGWISE'}
                        </div>
                        <div className="message-content">
                          {message.content}
                        </div>

                        {message.citations?.length > 0 && (
                          <div className="citation-list">
                            <div className="citation-heading">
                              SOURCES · {message.citations.length}
                            </div>
                            {message.citations.map((citation, index) => (
                              <div
                                className="citation-card"
                                key={`${citation.source}-${citation.page}-${index}`}
                              >
                                <FileText size={15} />
                                <div className="citation-info">
                                  <strong>{citation.source}</strong>
                                  <span>Page {citation.page}</span>
                                </div>
                                <span className="citation-score">
                                  {Number.isFinite(Number(citation.score))
                                    ? `${(Number(citation.score) * 100).toFixed(1)}%`
                                    : '—'}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </article>
                    ))}

                    {asking && (
                      <div className="message assistant">
                        <div className="message-role">RAGWISE</div>
                        <div className="thinking-indicator">
                          <span />
                          <span />
                          <span />
                          <em>Searching and generating answer...</em>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <form className="composer" onSubmit={handleAsk}>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask anything about your research papers..."
                  rows={2}
                  disabled={asking}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      event.currentTarget.form.requestSubmit()
                    }
                  }}
                />
                <div className="composer-footer">
                  <div className="composer-options">
                    <label>
                      RETRIEVAL
                      <select
                        value={topK}
                        onChange={(event) => setTopK(Number(event.target.value))}
                      >
                        <option value={3}>Top 3</option>
                        <option value={5}>Top 5</option>
                        <option value={10}>Top 10</option>
                        <option value={15}>Top 15</option>
                        <option value={20}>Top 20</option>
                      </select>
                    </label>
                    <span className="composer-hint">Enter to send · Shift + Enter for new line</span>
                  </div>

                  <button
                    className="send-button"
                    type="submit"
                    disabled={!question.trim() || asking}
                  >
                    {asking ? 'Thinking...' : 'Ask RAGWise'}
                    <Sparkles size={15} />
                  </button>
                </div>
              </form>
            </div>

            <aside className="right-column">
              <div className="library-card">
                <div className="panel-header">
                  <div>
                    <div className="panel-eyebrow">KNOWLEDGE BASE</div>
                    <h2>Document library</h2>
                  </div>
                  <FolderOpen size={19} />
                </div>

                <div className="library-count">
                  <strong>{documents.length.toString().padStart(2, '0')}</strong>
                  <span>PDF DOCUMENTS<br />INDEXED LOCALLY</span>
                </div>

                <div className="library-documents">
                  {loadingDocuments ? (
                    <div className="empty-library">Loading...</div>
                  ) : documents.length === 0 ? (
                    <div className="empty-library">
                      No documents yet. Upload a PDF to begin.
                    </div>
                  ) : (
                    documents.map((document) => (
                      <button
                        className={`library-document ${
                          selectedDocument === document ? 'selected' : ''
                        }`}
                        key={document}
                        onClick={() => setSelectedDocument(
                          selectedDocument === document ? '' : document
                        )}
                      >
                        <div className="pdf-icon"><FileText size={17} /></div>
                        <span title={document}>{document}</span>
                      </button>
                    ))
                  )}
                </div>

                <label className={`upload-button ${uploading ? 'disabled' : ''}`}>
                  <Upload size={16} />
                  {uploading ? 'Indexing document...' : 'Upload a PDF'}
                  <input
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleUpload}
                    disabled={uploading}
                    hidden
                  />
                </label>

                {uploadMessage && (
                  <div className="upload-message">{uploadMessage}</div>
                )}
              </div>

              <div className="system-card">
                <div className="panel-eyebrow">SYSTEM INFORMATION</div>
                <h3>Local AI environment</h3>
                <div className="system-row">
                  <span><Wifi size={15} /> FastAPI backend</span>
                  <strong className={backendStatus}>
                    {backendStatus === 'online' ? 'Connected' : backendStatus}
                  </strong>
                </div>
                <div className="system-row">
                  <span><BookOpen size={15} /> Document retrieval</span>
                  <strong>RAG pipeline</strong>
                </div>
                <div className="system-row">
                  <span><Sparkles size={15} /> Generation model</span>
                  <strong>Qwen 2.5 · 7B</strong>
                </div>
                <p>
                  Model information reflects your configured local setup.
                  API status checks FastAPI only.
                </p>
              </div>
            </aside>
          </section>

          <footer className="dashboard-footer">
            <span>RAGWISE / RESEARCH INTELLIGENCE WORKSPACE</span>
            <span>BUILT FOR EVIDENCE-BASED RESEARCH</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App
