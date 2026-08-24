import type { Step } from './types'
import { part0 } from './steps/part0'
import { part1 } from './steps/part1'
import { part2 } from './steps/part2'
import { part3 } from './steps/part3'
import { part4 } from './steps/part4'

export const steps: Step[] = [...part0, ...part1, ...part2, ...part3, ...part4]

export const parts = [...new Set(steps.map((s) => s.part))]

export function stepsOf(part: string) {
  return steps.filter((s) => s.part === part)
}

export function findStep(slug: string) {
  return steps.find((s) => s.slug === slug)
}

/** 어떤 데모가 어느 단계에 붙어 있는지 */
export function stepWithDemo(kind: string) {
  return steps.find((s) => s.demo?.kind === kind)
}

export function neighbors(slug: string) {
  const i = steps.findIndex((s) => s.slug === slug)
  return { prev: i > 0 ? steps[i - 1] : undefined, next: i < steps.length - 1 ? steps[i + 1] : undefined }
}

/** 전체 프롬프트 개수 — 홈 화면 통계용 */
export const totalPrompts = steps.reduce((n, s) => n + s.prompts.length, 0)

export type { Step, DemoKind, StepDemo } from './types'
