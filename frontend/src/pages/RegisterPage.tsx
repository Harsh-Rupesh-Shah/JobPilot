import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (password !== confirmPassword) {
      setError("Passwords don't match")
      return
    }
    
    setIsLoading(true)
    setError(null)
    try {
      await register(fullName, email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const getPasswordStrength = () => {
    let strength = 0
    if (password.length > 0) strength = 1
    if (password.length > 5) strength = 2
    if (password.length > 8 && /[A-Z]/.test(password)) strength = 3
    if (password.length > 10 && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) strength = 4
    return strength
  }

  const strength = getPasswordStrength()

  return (
    <div className="bg-surface-bright min-h-screen font-interface-md text-on-surface flex flex-col items-center">
      {/* Top Branding */}
      <header className="w-full max-w-container px-margin-mobile md:px-margin-desktop py-8 flex justify-start">
        <div className="flex items-center gap-2">
          <span className="font-headline-lg text-headline-lg font-bold text-primary">JobCopilot</span>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center w-full px-6 py-12">
        <div className="w-full max-w-[520px] bg-surface-container-lowest border border-outline-variant rounded-xl p-8 md:p-12 shadow-overlay">
          
          <div className="mb-10 text-center">
            <h1 className="font-headline-lg text-headline-lg text-primary mb-3">Create your account</h1>
            <p className="font-interface-md text-on-surface-variant">Start your journey with institutional-grade intelligence.</p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-error-container text-on-error-container rounded-lg font-interface-sm text-interface-sm">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Name Field */}
            <div className="space-y-2">
              <label htmlFor="full-name" className="input-label !mb-0">Full Name</label>
              <input
                id="full-name"
                type="text"
                required
                placeholder="Alex Johnson"
                className="input-field"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            {/* Email Field */}
            <div className="space-y-2">
              <label htmlFor="email" className="input-label !mb-0">Email Address</label>
              <input
                id="email"
                type="email"
                required
                placeholder="alex@example.com"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2 relative">
              <label htmlFor="password" className="input-label !mb-0">Password</label>
              <input
                id="password"
                type="password"
                required
                placeholder="••••••••"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {/* Strength Indicator */}
              <div className="flex gap-1.5 mt-3">
                <div className={`strength-segment ${strength >= 1 ? 'strength-1' : ''}`} />
                <div className={`strength-segment ${strength >= 2 ? 'strength-2' : ''}`} />
                <div className={`strength-segment ${strength >= 3 ? 'strength-3' : ''}`} />
                <div className={`strength-segment ${strength >= 4 ? 'strength-4' : ''}`} />
              </div>
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-2">
              <label htmlFor="confirm-password" className="input-label !mb-0">Confirm Password</label>
              <input
                id="confirm-password"
                type="password"
                required
                placeholder="••••••••"
                className="input-field"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            {/* CTA Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-4 mt-8"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined animate-spin-slow">progress_activity</span>
                  Processing...
                </span>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="mt-10 pt-8 border-t border-outline-variant text-center space-y-6">
            <p className="font-interface-sm text-on-surface-variant">
              Already have an account?{' '}
              <Link to="/login" className="text-secondary font-semibold hover:underline">Sign In</Link>
            </p>
            <div className="flex items-center justify-center gap-2 py-2 px-4 bg-surface-container-low rounded-full w-fit mx-auto">
              <span className="material-symbols-outlined text-[14px] text-outline">lock</span>
              <span className="text-[10px] font-label-caps text-outline uppercase tracking-widest">Your data is private and never shared</span>
            </div>
          </div>
        </div>
      </main>

      {/* Simple Footer */}
      <footer className="w-full py-8 text-center">
        <p className="font-label-caps text-label-caps text-outline">© 2024 JobCopilot Intelligence Systems</p>
      </footer>
    </div>
  )
}
