import { Link, Navigate, useParams } from 'react-router-dom'
import { GuideView } from '../components/GuideView'
import { findGuide, guides } from '../content/guides'

export function GuidePage() {
  const { id = '' } = useParams()
  const guide = findGuide(id)
  if (!guide) return <Navigate to="/guides" replace />

  const i = guides.findIndex((g) => g.id === id)
  const next = guides[i + 1]

  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-8">
      <Link to="/guides" className="text-muted hover:text-brand-500 text-[12.5px]">
        ← 안내서 목록
      </Link>
      <div className="mt-4">
        <GuideView guide={guide} />
      </div>

      {next && (
        <Link
          to={`/guides/${next.id}`}
          className="border-hair surface hover:border-brand-500/60 mt-6 flex items-center justify-between gap-3 rounded-xl border p-4 transition"
        >
          <span className="min-w-0">
            <span className="text-muted block text-[11.5px] font-semibold tracking-wide">다음 안내서</span>
            <span className="mt-0.5 block truncate text-[14px] font-semibold">{next.title}</span>
          </span>
          <span className="text-brand-500 shrink-0 text-[14px]">→</span>
        </Link>
      )}
    </div>
  )
}
