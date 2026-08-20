export interface Positioned<T> {
  item: T
  left: number
  width: number
}

/**
 * 시간이 겹치는 일정들을 나란히 배치한다. (캘린더 주 뷰의 핵심 로직)
 *
 *  1) 시작 시각 순 정렬
 *  2) 그룹 최대 종료시각보다 늦게 시작하면 새 그룹 (= 겹치지 않는 묶음의 경계)
 *  3) 그룹 안에서 열을 배정한다. 앞 일정이 끝난 뒤 시작하면 그 열을 재사용
 *  4) 그룹의 열 개수로 폭을 나눈다
 */
export function layoutOverlaps<T extends { start: Date; end: Date }>(items: T[]): Positioned<T>[] {
  const sorted = [...items].sort(
    (a, b) => a.start.getTime() - b.start.getTime() || b.end.getTime() - a.end.getTime(),
  )

  const result: Positioned<T>[] = []
  let group: T[] = []
  let groupEnd = -Infinity

  const flush = () => {
    if (group.length === 0) return
    const columns: T[][] = []
    const startIndex = result.length

    for (const it of group) {
      let col = columns.findIndex((c) => c[c.length - 1].end.getTime() <= it.start.getTime())
      if (col === -1) {
        columns.push([it])
        col = columns.length - 1
      } else {
        columns[col].push(it)
      }
      result.push({ item: it, left: col, width: 1 })
    }

    const n = columns.length
    for (let i = startIndex; i < result.length; i++) {
      result[i].width = 1 / n
      result[i].left = result[i].left / n
    }
    group = []
    groupEnd = -Infinity
  }

  for (const it of sorted) {
    if (it.start.getTime() >= groupEnd) flush()
    group.push(it)
    groupEnd = Math.max(groupEnd, it.end.getTime())
  }
  flush()
  return result
}
