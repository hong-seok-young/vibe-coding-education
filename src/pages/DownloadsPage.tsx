import { Link } from 'react-router-dom'
import { DownloadCard } from '../components/DownloadCard'
import { DOWNLOADS } from '../download'

/** 결과물을 HTML 파일로 받아 가는 곳 */
export function DownloadsPage() {
  return (
    <div className="mx-auto w-full max-w-[860px] px-5 py-8">
      <p className="text-muted text-[11.5px] font-semibold tracking-wider">결과물 내려받기</p>
      <h1 className="mt-1.5 text-[22px] font-semibold tracking-tight">
        화면으로 보고, 파일로 받아서, AI에게 고치게 하기
      </h1>
      <p className="text-muted mt-2.5 text-[14px] leading-7">
        각 단계에서 만져 본 결과물을 <strong className="text-[color:var(--text)]">HTML 파일 하나</strong>로 받을 수
        있습니다. 설치도 서버도 필요 없어서 더블클릭하면 바로 열리고, 그 파일을 AI 채팅창에 첨부해서 “여기에 이 기능
        넣어줘”라고 시키면 기능 수정 실습이 됩니다.
      </p>

      <ol className="border-hair surface mt-5 space-y-2 rounded-xl border p-4 text-[13px] leading-7">
        <li>
          <strong>1.</strong> 아래에서 <span className="text-brand-500">[↓ HTML 파일 받기]</span> 를 누릅니다. 다운로드
          폴더에 파일이 하나 생깁니다.
        </li>
        <li>
          <strong>2.</strong> AI 채팅창(웍스 AI · ChatGPT · Claude 등)에 그 파일을 <strong>첨부</strong>합니다.
        </li>
        <li>
          <strong>3.</strong> 아래 “시켜볼 것” 중 하나를 눌러 문장을 복사해서 같이 보냅니다.
        </li>
        <li>
          <strong>4.</strong> AI가 준 파일을 받아서 <strong>더블클릭</strong>해 열어 보고, 원하는 대로 바뀌었는지
          확인합니다.
        </li>
      </ol>

      <p className="text-muted mt-2.5 text-[12.5px] leading-6">
        어디를 눌러야 하는지 모르겠다면{' '}
        <Link to="/guides/edit-html-with-ai" className="text-brand-500 font-medium">
          클릭 단위 안내서
        </Link>
        를 먼저 보세요.
      </p>

      <div className="mt-7 space-y-5">
        {DOWNLOADS.map((app) => (
          <DownloadCard key={app.id} app={app} />
        ))}
      </div>

      <div className="border-hair text-muted mt-8 rounded-xl border border-dashed p-4 text-[12.5px] leading-6">
        <p className="mb-1.5 font-semibold">알아 두면 좋은 것</p>
        <p className="mb-2">
          네 파일의 코드는 사실 같습니다. 맨 위 <code className="font-mono">ENABLED_TABS</code> 한 줄이 어떤 화면을 켤지
          정할 뿐입니다. 캘린더만 받아도 그 줄에 <code className="font-mono">'weekly'</code> 를 추가하면 주간보고 화면이
          바로 켜집니다.
        </p>
        <p className="mb-1.5 font-semibold">이 파일들은 “교육용 축소판”입니다</p>
        <p>
          로그인(RADIUS), 서버 저장, 팀원 간 공유, 실제 구글 캘린더 연동은 들어 있지 않습니다. 데이터는 그 브라우저 안에만
          남습니다. 실제 사내 서비스로 만드는 부분은 dX팀이 맡습니다 — 여기서는 <strong>화면과 규칙을 내 손으로 바꿔 보는
          것</strong>이 목적입니다.
        </p>
      </div>
    </div>
  )
}
