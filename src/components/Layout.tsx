import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { parts, steps, stepsOf } from '../content'
import { useProgress } from '../lib/progress'
import { useTheme } from '../lib/theme'

export function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const { isDone } = useProgress()
  const { theme, toggle } = useTheme()

  const doneCount = steps.filter((s) => isDone(s.id)).length
  const percent = Math.round((doneCount / steps.length) * 100)

  return (
    <div className="flex h-full flex-col">
      <header className="border-hair surface sticky top-0 z-30 flex items-center gap-3 border-b px-4 py-2.5">
        <button
          onClick={() => setOpen((v) => !v)}
          className="border-hair text-muted rounded-md border px-2 py-1.5 text-xs lg:hidden"
          aria-label="목차"
        >
          ☰
        </button>

        <Link to="/" className="flex min-w-0 items-center gap-2.5">
          <span className="bg-brand-500 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-[13px] font-bold text-white">
            V
          </span>
          <span className="min-w-0">
            <span className="block truncate text-[13.5px] leading-tight font-semibold tracking-tight">
              바이브 코딩 교육 프로그램
            </span>
            <span className="text-muted block truncate text-[11px] leading-tight">
              업무 캘린더 · 주간보고 · 인수인계 웹앱 만들기
            </span>
          </span>
        </Link>

        <nav className="ml-auto flex items-center gap-1">
          <TopLink to="/" label="개요" exact />
          <TopLink to="/prompts" label="프롬프트 모음" />
        </nav>

        <div className="text-muted hidden items-center gap-2 text-[11.5px] md:flex">
          <div className="surface-2 h-1.5 w-20 overflow-hidden rounded-full">
            <div className="bg-brand-500 h-full transition-all" style={{ width: percent + '%' }} />
          </div>
          {doneCount}/{steps.length}
        </div>

        <button
          onClick={toggle}
          className="border-hair text-muted hover:text-brand-500 rounded-md border px-2 py-1.5 text-xs"
          aria-label="테마 전환"
        >
          {theme === 'dark' ? '☀' : '☾'}
        </button>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside
          className={
            'border-hair surface fixed inset-y-0 top-[53px] left-0 z-20 w-[280px] overflow-y-auto border-r px-3 py-4 transition-transform lg:sticky lg:translate-x-0 ' +
            (open ? 'translate-x-0' : '-translate-x-full')
          }
        >
          <Curriculum onNavigate={() => setOpen(false)} currentPath={location.pathname} />
        </aside>

        {open && (
          <div
            className="fixed inset-0 top-[53px] z-10 bg-black/40 lg:hidden"
            onClick={() => setOpen(false)}
          />
        )}

        <main className="flex min-h-0 min-w-0 flex-1 flex-col">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function TopLink({ to, label, exact, match }: { to: string; label: string; exact?: boolean; match?: string }) {
  const location = useLocation()
  const active = exact
    ? location.pathname === to
    : location.pathname.startsWith(match ?? to)
  return (
    <Link
      to={to}
      className={
        'rounded-md px-2.5 py-1.5 text-[12.5px] font-medium transition ' +
        (active ? 'bg-brand-500/15 text-brand-500' : 'text-muted hover:text-brand-500')
      }
    >
      {label}
    </Link>
  )
}

function Curriculum({ onNavigate, currentPath }: { onNavigate: () => void; currentPath: string }) {
  const { isDone } = useProgress()

  return (
    <nav className="space-y-5">
      {parts.map((part) => (
        <div key={part}>
          <div className="text-muted mb-2 px-2 text-[10.5px] font-semibold tracking-wider">{part}</div>
          <ul className="space-y-0.5">
            {stepsOf(part).map((s) => {
              const active = currentPath === `/steps/${s.slug}`
              const done = isDone(s.id)
              return (
                <li key={s.id}>
                  <NavLink
                    to={`/steps/${s.slug}`}
                    onClick={onNavigate}
                    className={
                      'flex items-start gap-2 rounded-md px-2 py-1.5 text-[12.5px] leading-5 transition ' +
                      (active ? 'bg-brand-500/15 text-brand-500 font-medium' : 'hover:surface-2')
                    }
                  >
                    <span
                      className={
                        'mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded font-mono text-[9px] ' +
                        (done
                          ? 'bg-emerald-500 text-white'
                          : active
                            ? 'bg-brand-500 text-white'
                            : 'surface-2 text-muted')
                      }
                    >
                      {done ? '✓' : s.id}
                    </span>
                    <span className={'min-w-0 flex-1 ' + (done && !active ? 'text-muted' : '')}>
                      {s.title}
                    </span>
                    {/* 만져볼 수 있는 단계 표시 — 데모는 1번 탭 안에 있다 */}
                    {s.demo && (
                      <span
                        title="직접 만져보는 데모가 있는 단계"
                        className={'mt-0.5 shrink-0 text-[9px] ' + (active ? 'text-brand-500' : 'text-muted')}
                      >
                        ▶
                      </span>
                    )}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </nav>
  )
}
