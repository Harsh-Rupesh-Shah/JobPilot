import { FormEvent, useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const from = (location.state as any)?.from?.pathname || '/'

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-surface min-h-screen flex items-center justify-center p-margin-mobile md:p-0 font-interface-md">
      <main className="w-full max-w-[480px]">
        <div className="card p-8">
          {/* Header Section */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="w-10 h-10 flex items-center justify-center rounded-lg bg-secondary/10 text-secondary mb-4">
              <span className="material-symbols-outlined !text-[28px]">work</span>
            </div>
            <h1 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface font-bold">
              JobCopilot
            </h1>
            <p className="font-interface-sm text-interface-sm text-on-surface-variant mt-2">
              Your AI-powered career partner
            </p>
          </div>

          <hr className="border-outline-variant mb-8" />

          {error && (
            <div className="mb-6 p-3 bg-error-container text-on-error-container rounded-lg font-interface-sm text-interface-sm">
              {error}
            </div>
          )}

          {/* Form Section */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Email Field */}
            <div className="flex flex-col gap-2">
              <label htmlFor="email" className="input-label">EMAIL</label>
              <input
                id="email"
                type="email"
                required
                className="input-field"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between items-center">
                <label htmlFor="password" className="input-label !mb-0">PASSWORD</label>
              </div>
              <div className="relative group">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  className="input-field pr-12"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface-variant transition-colors flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  <span className="material-symbols-outlined">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
              <div className="text-right mt-1">
                <a href="#" className="font-interface-sm text-interface-sm text-secondary hover:underline transition-all">
                  Forgot password?
                </a>
              </div>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="material-symbols-outlined animate-spin-slow">progress_activity</span>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-outline-variant"></span>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-surface-container-lowest font-label-caps text-label-caps text-outline uppercase">
                OR
              </span>
            </div>
          </div>

          {/* Footer Link */}
          <div className="text-center">
            <p className="font-interface-sm text-interface-sm text-on-surface-variant">
              Don't have an account?{' '}
              <Link to="/register" className="text-secondary font-bold hover:underline ml-1">
                Create one →
              </Link>
            </p>
          </div>
        </div>

        {/* Decorative Footer */}
        <div className="mt-8 text-center">
          <p className="font-label-caps text-label-caps text-outline uppercase tracking-widest">
            JobCopilot • Precise Career Intelligence
          </p>
        </div>
      </main>
    </div>
  )
}
