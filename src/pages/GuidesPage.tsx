import { Link } from 'react-router-dom'
import { guides } from '../content/guides'

export function GuidesPage() {
  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-8">
      <h1 className="text-2xl leading-tight font-bold tracking-tight">안내서</h1>
      <p className="text-muted mt-2 text-[14px] leading-7">
        교육 중에 "어디 들어가서 뭘 눌러요?" 로 막히는 부분만 모았습니다. 설명이 아니라{' '}
        <strong>링크 · 누를 버튼 · 넣을 값 · 성공 기준</strong>을 칸마다 적어 뒀습니다. 필요할 때만 펼쳐 보세요.
      </p>

      <ul className="mt-6 space-y-2.5">
        {guides.map((g) => (
          <li key={g.id}>
            <Link
              to={`/guides/${g.id}`}
              className="border-hair surface hover:border-brand-500/60 block rounded-xl border p-4 transition"
            >
              <div className="text-muted flex flex-wrap items-center gap-2 text-[11px] font-semibold tracking-wide">
                <span
                  className={
                    'rounded px-1.5 py-0.5 ' +
                    (g.who === 'dX팀'
                      ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                      : 'bg-brand-500/15 text-brand-500')
                  }
                >
                  {g.who}
                </span>
                <span>{g.minutes}</span>
                <span>· {g.steps.length}칸</span>
              </div>
              <p className="mt-1.5 text-[15px] font-semibold">{g.title}</p>
              <p className="text-muted mt-1 text-[13px] leading-6">{g.why}</p>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
