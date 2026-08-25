import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCopy } from '../lib/useCopy'
import { previewHtml, saveHtml, sizeOf, type DownloadApp } from '../download'

/**
 * 결과물을 HTML 파일 하나로 받아 가는 카드.
 * 화면에서 본 데모를 그대로 파일로 받아서, AI에게 첨부해 고쳐 보는 실습에 쓴다.
 */
export function DownloadCard({ app, dense }: { app: DownloadApp; dense?: boolean }) {
  const [openId, setOpenId] = useState<number | null>(null)
  const { copied, copy } = useCopy()

  return (
    <section className="border-hair surface rounded-xl border p-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="bg-emerald-500 rounded px-1.5 py-0.5 text-[10.5px] font-semibold text-white">
          파일로 받기
        </span>
        <span className="text-[13.5px] font-semibold">{app.title}</span>
        <span className="text-muted font-mono text-[11.5px]">
          {app.filename} · {sizeOf(app)}
        </span>
      </div>

      <p className="text-muted mt-1.5 text-[13px] leading-6">{app.summary}</p>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          onClick={() => saveHtml(app)}
          className="bg-brand-500 hover:bg-brand-600 rounded-lg px-3.5 py-2 text-[12.5px] font-semibold text-white"
        >
          ↓ HTML 파일 받기
        </button>
        <button
          onClick={() => previewHtml(app)}
          className="border-hair text-muted hover:text-brand-500 rounded-lg border px-3 py-2 text-[12.5px]"
        >
          새 탭에서 열어보기
        </button>
        <Link
          to="/guides/edit-html-with-ai"
          className="border-hair text-muted hover:text-brand-500 rounded-lg border px-3 py-2 text-[12.5px]"
        >
          AI로 고치는 법 →
        </Link>
      </div>

      {!dense && (
        <>
          <p className="text-muted mt-4 mb-1.5 text-[11.5px] font-semibold">이 파일 안에 들어 있는 것</p>
          <ul className="text-muted space-y-1 text-[12.5px] leading-6">
            {app.contains.map((c) => (
              <li key={c} className="flex gap-2">
                <span className="text-emerald-500">✓</span>
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </>
      )}

      <p className="text-muted mt-4 mb-1.5 text-[11.5px] font-semibold">
        받은 파일을 AI에 첨부하고 시켜볼 것 — 누르면 문장이 나옵니다
      </p>
      <div className="flex flex-wrap gap-1.5">
        {app.exercises.map((e, i) => (
          <button
            key={e.label}
            onClick={() => setOpenId(openId === i ? null : i)}
            className={
              'rounded-lg border px-2.5 py-1.5 text-[12px] transition ' +
              (openId === i
                ? 'border-brand-500 text-brand-500 bg-brand-500/10'
                : 'border-hair text-muted hover:text-brand-500')
            }
          >
            {e.label}
          </button>
        ))}
      </div>

      {openId !== null && (
        <div className="border-hair surface-2 mt-2.5 rounded-lg border p-3">
          <pre className="overflow-x-auto text-[12px] leading-6 whitespace-pre-wrap">
            {app.exercises[openId].prompt}
          </pre>
          <button
            onClick={() => copy(app.exercises[openId].prompt)}
            className="border-hair surface hover:text-brand-500 mt-2 rounded-md border px-2.5 py-1.5 text-[11.5px]"
          >
            {copied ? '복사됨 ✓' : '프롬프트 복사'}
          </button>
        </div>
      )}
    </section>
  )
}
