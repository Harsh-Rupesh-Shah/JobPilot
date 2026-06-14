import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ResumeUpload from './components/ResumeUpload'
import JobInput from './components/JobInput'
import StreamOutput from './components/StreamOutput'
import ApprovalPanel from './components/ApprovalPanel'
import ApplicationTracker from './components/ApplicationTracker'
import InterviewVault from './pages/InterviewVault'
import MasterProfile from './pages/MasterProfile'
import { useApplication } from './hooks/useApplication'
import { useSSE } from './hooks/useSSE'
import { useState, useEffect } from 'react'
import { resumeApi } from './api/client'

// ── Protected Route Wrapper ────────────────────────────────────────────────
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><span className="material-symbols-outlined animate-spin-slow text-4xl text-secondary">progress_activity</span></div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

// ── Main Layout ────────────────────────────────────────────────────────────
const MainLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [profileOpen, setProfileOpen] = useState(false)

  const isWorkspace = location.pathname === '/'
  const isTracker = location.pathname === '/tracker'

  return (
    <div className="bg-surface text-on-surface antialiased min-h-screen">
      {/* SideNavBar */}
      <nav className="fixed left-0 top-0 h-full flex flex-col py-8 px-4 bg-surface w-64 border-r border-outline-variant z-50">
        <div className="mb-12 px-4">
          <h1 className="font-headline-lg text-headline-lg font-bold text-primary tracking-tight">JobCopilot</h1>
          <p className="font-interface-sm text-interface-sm text-on-surface-variant mt-1">AI Career Advisor</p>
        </div>
        
        <Link to="/" className="mb-8 mx-4 bg-primary text-on-primary py-3 px-4 rounded-lg font-interface-md text-interface-md flex items-center justify-center gap-2 hover:opacity-80 transition-opacity">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>add</span>
          New Application
        </Link>
        
        <ul className="flex flex-col gap-2 flex-grow">
          <div className="text-xs font-label-caps text-on-surface-variant uppercase tracking-widest px-4 mt-2 mb-1">Copilot</div>
          <li>
            <Link to="/" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${isWorkspace ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">clinical_notes</span>
              <span className="font-interface-md text-interface-md">Workspace</span>
            </Link>
          </li>
          <li>
            <Link to="/tracker" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${isTracker ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">dashboard_customize</span>
              <span className="font-interface-md text-interface-md">Applications</span>
            </Link>
          </li>

          <div className="text-xs font-label-caps text-on-surface-variant uppercase tracking-widest px-4 mt-6 mb-1">Library & CRM</div>
          <li>
            <Link to="/profile" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${location.pathname === '/profile' ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">person</span>
              <span className="font-interface-md text-interface-md">Master Profile</span>
            </Link>
          </li>
          <li>
            <Link to="/vault" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${location.pathname === '/vault' ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">menu_book</span>
              <span className="font-interface-md text-interface-md">Interview Vault</span>
            </Link>
          </li>
          <li>
            <Link to="/contacts" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${location.pathname === '/contacts' ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">contacts</span>
              <span className="font-interface-md text-interface-md">Contacts CRM</span>
            </Link>
          </li>
          <li>
            <Link to="/analytics" className={`flex items-center gap-3 px-4 py-3 font-medium transition-colors rounded-lg ${location.pathname === '/analytics' ? 'text-primary bg-surface-container-low font-bold' : 'text-on-surface-variant hover:bg-surface-container-high'}`}>
              <span className="material-symbols-outlined">bar_chart</span>
              <span className="font-interface-md text-interface-md">Analytics</span>
            </Link>
          </li>
        </ul>
        
        <div className="mt-auto pt-4 border-t border-outline-variant">
          <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-3 text-on-surface-variant font-medium hover:bg-surface-container-high transition-colors">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-interface-md text-interface-md">Log Out</span>
          </button>
        </div>
      </nav>

      {/* TopAppBar */}
      <header className="sticky top-0 z-40 w-full flex justify-between items-center px-8 h-16 ml-64 max-w-[calc(100%-16rem)] bg-surface/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm">
        <div className="flex items-center gap-6 flex-1">
          {/* Global Search Bar Placeholder */}
          <div className="relative w-full max-w-md hidden md:block">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
            <input type="text" placeholder="Search applications, resumes..." className="w-full bg-surface-container-high border border-outline-variant rounded-full py-2 pl-10 pr-4 text-interface-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all" />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center w-10 h-10 rounded-full hover:bg-surface-container">
            <span className="material-symbols-outlined">light_mode</span>
          </button>
          <button className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center w-10 h-10 rounded-full hover:bg-surface-container relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full"></span>
          </button>
          <div className="relative">
            <div 
              className="flex items-center gap-2 cursor-pointer hover:bg-surface-container-low px-2 py-1 rounded-lg transition-colors border border-transparent hover:border-outline-variant"
              onClick={() => setProfileOpen(!profileOpen)}
            >
               <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold">
                 {user?.email?.charAt(0).toUpperCase() || 'U'}
               </div>
               <span className="font-interface-sm text-on-surface-variant hidden md:block">{user?.email}</span>
               <span className="material-symbols-outlined text-on-surface-variant text-[18px]">expand_more</span>
            </div>
            
            {profileOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-lg py-2 z-50 animate-fade-in">
                <div className="px-4 py-3 border-b border-outline-variant mb-2 bg-surface-container-low/50">
                  <p className="text-[11px] text-on-surface-variant font-label-caps uppercase tracking-wider mb-0.5">Signed in as</p>
                  <p className="font-interface-sm font-bold text-primary truncate">{user?.email}</p>
                </div>
                <Link to="/profile" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-on-surface hover:bg-surface-container transition-colors">
                  <span className="material-symbols-outlined text-[18px] text-secondary">person</span>
                  <span className="font-interface-sm font-medium">Master Profile</span>
                </Link>
                <div className="h-px bg-outline-variant my-1 mx-4"></div>
                <button onClick={() => { setProfileOpen(false); logout(); }} className="w-full flex items-center gap-3 px-4 py-2.5 text-error hover:bg-error-container/20 transition-colors text-left">
                  <span className="material-symbols-outlined text-[18px]">logout</span>
                  <span className="font-interface-sm font-medium">Log Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Canvas */}
      <main className="ml-64 p-8 max-w-7xl mx-auto">
        {children}
      </main>
    </div>
  )
}

// ── Application Flow Orchestrator ──────────────────────────────────────────
const ApplicationFlow = () => {
  const [step, setStep] = useState<'upload' | 'job' | 'running' | 'approval'>('upload')
  const [resumeId, setResumeId] = useState<string | null>(null)
  const [hasMasterResume, setHasMasterResume] = useState(false)
  const navigate = useNavigate()
  
  const app = useApplication()
  const sse = useSSE(app.runId)

  useEffect(() => {
    resumeApi.getLatest().then(res => {
      if (res) {
        setResumeId(res.resume_id)
        setHasMasterResume(true)
        setStep('job')
      }
    }).catch(err => {
      // Ignored: 404 just means no resume
    })
  }, [])

  // Move to approval when interrupt received
  if (sse.interruptPayload && step === 'running') {
    setStep('approval')
  }

  const handleStart = async (jobUrl: string, jobDesc: string) => {
    if (!resumeId) return
    await app.startRun(jobUrl, jobDesc, resumeId)
    setStep('running')
  }

  const handleApprove = async (edited: any) => {
    await app.approve(edited)
    navigate('/tracker')
  }

  return (
    <div className="flex flex-col gap-8 w-full max-w-6xl mx-auto">
      {/* 3-Step Progress Indicator */}
      <div className="flex items-center gap-4 mb-4 pb-4 border-b border-outline-variant">
        <div className={`flex items-center gap-2 ${step === 'upload' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step === 'upload' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>1</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Upload Context</span>
        </div>
        <div className="w-12 h-[1px] bg-outline-variant"></div>
        <div className={`flex items-center gap-2 ${step === 'job' ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step === 'job' ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>2</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Target Job</span>
        </div>
        <div className="w-12 h-[1px] bg-outline-variant"></div>
        <div className={`flex items-center gap-2 ${['running', 'approval'].includes(step) ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${['running', 'approval'].includes(step) ? 'bg-primary text-on-primary' : 'bg-surface-container-high'}`}>3</div>
          <span className="font-label-caps uppercase tracking-wider text-xs">Co-Pilot Run</span>
        </div>
      </div>

      {step === 'upload' && (
        <div className="animate-fade-in">
          <div className="mb-8">
            <h1 className="font-display-lg text-primary mb-2">Upload your Context</h1>
            <p className="font-interface-md text-on-surface-variant">Provide your current resume to act as the ground truth for your experience.</p>
          </div>
          <ResumeUpload onNext={(id) => { setResumeId(id); setStep('job') }} />
        </div>
      )}
      
      {step === 'job' && (
        <div className="animate-fade-in flex flex-col gap-6 w-full">
          {hasMasterResume && (
            <div className="bg-surface-container-low border border-primary/30 text-primary px-4 py-3 rounded-lg flex items-center gap-3 animate-fade-in">
              <span className="material-symbols-outlined text-secondary">verified</span>
              <span className="font-interface-md font-medium text-on-surface">Using your saved Master Profile. You can safely skip the upload step!</span>
            </div>
          )}
          <JobInput onStart={handleStart} isStarting={app.isPolling && step === 'job'} />
        </div>
      )}
      
      {step === 'running' && (
        <div className="flex flex-col gap-8 w-full animate-fade-in">
          <div className="text-center">
            <h2 className="font-display-lg text-primary mb-2">Co-Pilot is Running</h2>
            <p className="font-interface-md text-on-surface-variant flex items-center justify-center gap-2">
              <span className="material-symbols-outlined animate-spin-slow text-secondary">sync</span>
              Generating institutional-grade application materials...
            </p>
          </div>
          <StreamOutput tokens={sse.agentTokens} currentAgent={app.status?.current_agent} />
        </div>
      )}

      {step === 'approval' && sse.interruptPayload?.outputs && (
        <ApprovalPanel 
          outputs={sse.interruptPayload.outputs as any} 
          onApprove={handleApprove} 
        />
      )}
    </div>
  )
}

// ── App Root ───────────────────────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <ApplicationFlow />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/tracker" element={
            <ProtectedRoute>
              <MainLayout>
                <ApplicationTracker />
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/vault" element={
            <ProtectedRoute>
              <MainLayout>
                <InterviewVault />
              </MainLayout>
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <MainLayout>
                <MasterProfile />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
