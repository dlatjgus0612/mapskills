---
name: ui-effects-glossary
description: 웹 인터랙션·모션 효과 용어 사전. "마우스에 반응하게", "움직이는 카드", "스크롤하면 나타나게", "반짝이게" 같은 말로 된 요청을 정확한 효과 용어(custom cursor, 3D tilt, magnetic button, parallax, scroll reveal 등)와 구현 방법으로 바꾼다. 웹사이트·랜딩페이지·포트폴리오 UI를 만들거나 다듬을 때, 또는 사용자가 효과 이름을 모를 때 사용.
---

# UI Effects Glossary

사용자가 말로 설명한 효과를 **용어 → 구현**으로 바꾼다. 효과를 고른 뒤에는 아래 공통 규칙을 반드시 지킨다.

## 공통 규칙
- 포인터 효과는 `@media (hover: hover) and (pointer: fine)` 안에서만 켠다. 터치 기기에서는 끈다.
- `prefers-reduced-motion: reduce`이면 모션을 끄거나 opacity 전환으로 대체한다.
- 애니메이션은 `transform`과 `opacity`만 바꾼다. `top`, `left`, `width`는 건드리지 않는다. 마우스 추적은 `requestAnimationFrame`과 lerp로 처리한다.
- 한 화면에 시그니처 효과는 1~2개만 둔다. 효과를 쌓으면 싸구려처럼 보인다.

## 마우스 / 포인터
| 말로 하면 | 용어 | 구현 키워드 |
|---|---|---|
| 마우스 커서를 바꿔줘 | **Custom cursor** | `cursor:none` 처리 후 fixed div가 따라오게 함(lerp). 링크 위에서 커지면 *cursor morph* |
| 커서 뒤에 잔상 | **Cursor trail** | 점 N개를 이전 좌표로 지연 추적. canvas 또는 div |
| 카드가 마우스 따라 기울어짐 | **3D tilt** / parallax tilt | `perspective` + `rotateX/rotateY`(±10°). vanilla-tilt.js, `react-parallax-tilt` |
| 기울 때 빛 반사 | **Glare / sheen** | tilt 위에 radial-gradient 오버레이, 커서 위치로 이동 |
| 버튼이 커서 쪽으로 끌려옴 | **Magnetic button** | 반경 안에서 거리 비례로 `translate`, 벗어나면 spring 복귀 |
| 커서 주변만 밝아짐 | **Spotlight / cursor glow** | CSS 변수 `--x --y` + `radial-gradient` |
| 카드 테두리가 커서 쪽만 빛남 | **Border glow / glow card** | `mask` 또는 이중 레이어 gradient border + `--x --y` |
| 배경이 마우스 따라 미세 이동 | **Mouse parallax** | 레이어별 depth 계수로 translate |
| 이미지가 커서 위치에 따라 뜸 | **Hover image reveal** | 리스트 hover 시 이미지가 커서를 따라다님(GSAP quickTo) |

## 스크롤
| 말로 하면 | 용어 | 구현 키워드 |
|---|---|---|
| 스크롤 부드럽게 | **Smooth scroll** | Lenis |
| 내려가면 하나씩 나타남 | **Scroll reveal** / stagger | IntersectionObserver, GSAP ScrollTrigger, Motion `whileInView` |
| 배경과 글이 다른 속도로 | **Parallax scrolling** | ScrollTrigger `scrub`, CSS `animation-timeline: scroll()` |
| 화면 고정된 채 내용만 바뀜 | **Pinned section / scrollytelling** | ScrollTrigger `pin` |
| 세로 스크롤로 가로 이동 | **Horizontal scroll section** | pin + x translate |
| 스크롤에 따라 숫자 올라감 | **Count-up** | 진입 시 tween |
| 진행 막대 | **Scroll progress bar** | `scaleX` = 진행률 |

## 텍스트
| 말로 하면 | 용어 | 구현 키워드 |
|---|---|---|
| 글자가 하나씩 올라옴 | **Split text reveal** | SplitText / 글자·단어 span + stagger, `overflow:hidden` 마스크 |
| 글자가 깨졌다가 맞춰짐 | **Text scramble / decode** | 랜덤 문자 → 목표 문자 |
| 타자 치듯 | **Typewriter** | |
| 흐르는 글자 띠 | **Marquee / ticker** | 복제 후 무한 translate |
| 글자 안에 그라데이션이 흐름 | **Gradient text / shimmer** | `background-clip:text` + background-position 애니메이션 |
| 지직거림 | **Glitch** | 의사요소 RGB split + clip-path |

## 표면 / 배경
| 말로 하면 | 용어 | 구현 키워드 |
|---|---|---|
| 유리처럼 뿌연 카드 | **Glassmorphism** | `backdrop-filter: blur()` + 반투명 + 1px 밝은 border |
| 노이즈 질감 | **Grain / noise overlay** | SVG feTurbulence 또는 노이즈 png, `mix-blend-mode` |
| 흐르는 그라데이션 배경 | **Mesh gradient / aurora** | 블러된 blob 여러 개 이동, 또는 shader |
| 반짝이는 테두리가 돎 | **Animated border beam** | conic-gradient 회전 + mask |
| 격자/점 배경 | **Grid / dot pattern** | CSS gradient, 가장자리 radial mask로 페이드 |
| 3D 오브젝트 배경 | **WebGL hero** | Three.js / R3F (→ react-three-fiber 스킬) |

## 전환 / 마이크로 인터랙션
| 말로 하면 | 용어 | 구현 키워드 |
|---|---|---|
| 페이지 넘어갈 때 부드럽게 | **Page transition** | View Transitions API, Barba.js, Motion `AnimatePresence` |
| 같은 요소가 다른 화면으로 이어짐 | **Shared element / FLIP** | `view-transition-name`, Motion `layoutId` |
| 눌렀을 때 쫀득하게 | **Spring / squash** | spring physics (stiffness, damping) |
| 로딩 자리 반짝임 | **Skeleton shimmer** | |
| 처음 들어올 때 로딩 화면 | **Preloader / intro** | |
| 버튼 hover 시 배경이 차오름 | **Fill / slide hover** | 의사요소 `scaleX` 0→1 |
| 클릭 시 물결 | **Ripple** | |

## 라이브러리 선택
- React UI 모션: **Motion**(구 Framer Motion). 복잡한 타임라인과 스크롤 연출: **GSAP + ScrollTrigger**. 스크롤 관성: **Lenis**
- 3D: **R3F + drei**. 가벼운 효과만 필요하면 CSS로 처리한다.
- 바로 가져다 쓰는 컴포넌트: Aceternity UI, Magic UI, React Bits (shadcn 계열)
