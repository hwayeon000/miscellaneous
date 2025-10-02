const PDF_TEXT_NUDGE_PX = 8; // ← 지금 환경에서 맞는 값(10)
// ===============================
// jsPDF 초기화
// ===============================
function initializePDF() {
    if (typeof window.jsPDF === 'undefined') {
        if (typeof jsPDF !== 'undefined') {
            window.jsPDF = new jspdf.jsPDF();
        } else if (typeof window.jspdf !== 'undefined') {
            window.jsPDF = window.jspdf.jsPDF;
        } else {
            console.error('jsPDF 라이브러리를 찾을 수 없습니다.');
            return false;
        }
    }
    return true;
}

// ===============================
// 라이브러리 로딩 대기
// ===============================
function waitForLibraries() {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const maxAttempts = 20;

        const check = () => {
            attempts++;
            const ok =
                (typeof window.jsPDF !== 'undefined' || typeof jsPDF !== 'undefined') &&
                typeof html2canvas !== 'undefined';
            if (ok) return resolve();
            if (attempts >= maxAttempts) return reject(new Error('라이브러리 로딩 타임아웃'));
            setTimeout(check, 200);
        };
        check();
    });
}

// ===============================
// 콘텐츠 로딩 대기 (차트 캔버스 크기 체크)
// ===============================
function waitForContentToLoad() {
    return new Promise((resolve) => {
        const check = () => {
            let allLoaded = true;
            const canvases = document.querySelectorAll('.total-content canvas');
            canvases.forEach((c) => {
                if (c.width === 0 || c.height === 0) allLoaded = false;
            });
            if (allLoaded) resolve();
            else setTimeout(check, 300);
        };
        setTimeout(check, 800); // 로딩 대기 시간 증가
    });
}

// ===============================
// 그래프·미디어·코드 등은 제외하고 "텍스트 노드"만 Npx 위로 이동
// ===============================
function nudgeAllTextExceptCharts(root, px = 10) {
    const created = [];
    const EXCLUDE_SELECTOR = 'canvas, svg, img, video, input, textarea, select, pre, code, kbd, samp, script, style, [data-nudge="off"], .no-nudge, .insight-icon, .pattern-icon, .badge-circle, .round-icon';

    // 텍스트 노드 순회
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: (node) => {
            if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
            const parent = node.parentElement;
            if (!parent) return NodeFilter.FILTER_REJECT;
            // 그래프/미디어/코드/명시적 제외 영역은 스킵
            if (parent.closest(EXCLUDE_SELECTOR)) return NodeFilter.FILTER_REJECT;
            const cs = getComputedStyle(parent);
            if (cs.display === 'none' || cs.visibility === 'hidden') return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
        }
    });

    const toWrap = [];
    let n;
    while ((n = walker.nextNode())) toWrap.push(n);

    toWrap.forEach((textNode) => {
        const span = document.createElement('span');
        span.className = 'baseline-nudge';
        span.style.display = 'inline-block';
        span.style.transform = `translateY(-${px}px)`;
        span.textContent = textNode.nodeValue;
        textNode.parentNode.replaceChild(span, textNode);
        created.push(span);
    });

    return created; // 복원용
}

function restoreNudgedAll(spans = []) {
    spans.forEach((span) => {
        // 굳이 원복 안 해도 클론 통째로 지우지만, 안전하게 원복 가능
        const text = document.createTextNode(span.textContent);
        span.parentNode && span.parentNode.replaceChild(text, span);
    });
}

// ===============================
// 아이콘들(FA)을 텍스트와 동일하게 위로 올림 - insight-icon 텍스트 처리 개선
// ===============================
function nudgeAllIcons(root, px = PDF_TEXT_NUDGE_PX) {
    const touched = [];
    
    // 더 포괄적인 아이콘 선택자
    const icons = root.querySelectorAll(`
        i.fas, i.far, i.fal, i.fab, i.fad,
        i.fa, i[class^="fa-"], i[class*=" fa-"],
        .fas, .far, .fal, .fab, .fad,
        [class^="fa-"], [class*=" fa-"],
        svg.svg-inline--fa,
        .insight-icon,
        .pattern-icon
    `);

    icons.forEach((iEl, index) => {        
        // insight-point 내부의 아이콘들은 특별 처리
        const isInsightIcon = iEl.closest('.insight-point');
        
        // 다른 예외 컨테이너는 여전히 제외 (insight-point 제외)
        if (!isInsightIcon && iEl.closest('.badge-circle, .chip, .avatar, .round-icon')) {
            return;
        }

        // insight-point 내부의 아이콘이라면 특별 처리
        if (isInsightIcon) {
            // insight-icon 컨테이너인 경우 (●가 들어있는)
            if (iEl.classList.contains('insight-icon')) {
                // 컨테이너 자체를 flex로 중앙정렬
                iEl.style.setProperty('display', 'inline-flex', 'important');
                iEl.style.setProperty('align-items', 'center', 'important');
                iEl.style.setProperty('justify-content', 'center', 'important');
                iEl.style.setProperty('vertical-align', 'middle', 'important');
                iEl.style.setProperty('text-align', 'center', 'important');
                iEl.style.setProperty('line-height', '1', 'important');
                
                // ● 텍스트는 nudge 적용하지 않음 (컨테이너가 이미 중앙정렬됨)
                // 대신 컨테이너 전체를 살짝 조정
                iEl.style.setProperty('transform', `translateY(-1px)`, 'important');
                touched.push(iEl);
                
            // pattern-icon 컨테이너인 경우 (FontAwesome 아이콘이 들어있는)
            } else if (iEl.classList.contains('pattern-icon')) {
                // 컨테이너는 flex로 중앙정렬
                iEl.style.setProperty('display', 'inline-flex', 'important');
                iEl.style.setProperty('align-items', 'center', 'important');
                iEl.style.setProperty('justify-content', 'center', 'important');
                iEl.style.setProperty('vertical-align', 'middle', 'important');
                
                // 내부의 실제 아이콘에 nudge 적용
                const innerIcon = iEl.querySelector('i, svg, .fas, .far, .fal, .fab, .fad');
                if (innerIcon) {
                    innerIcon.style.setProperty('transform', `translateY(-${px}px)`, 'important');
                    innerIcon.style.setProperty('display', 'inline-block', 'important');
                    innerIcon.style.setProperty('line-height', '1', 'important');
                    innerIcon.style.setProperty('vertical-align', 'baseline', 'important');
                    touched.push(innerIcon);
                }
                touched.push(iEl);
                
            } else {
                // 일반 아이콘인 경우
                iEl.style.setProperty('display', 'inline-block', 'important');
                iEl.style.setProperty('line-height', '1', 'important');
                iEl.style.setProperty('vertical-align', 'baseline', 'important');
                iEl.style.setProperty('transform', `translateY(-${px}px)`, 'important');
                touched.push(iEl);
            }
        } else {
            // 일반적인 아이콘 처리
            iEl.style.setProperty('display', 'inline-block', 'important');
            iEl.style.setProperty('line-height', '1', 'important');
            iEl.style.setProperty('vertical-align', 'baseline', 'important');
            iEl.style.setProperty('transform', `translateY(-${px}px)`, 'important');
            touched.push(iEl);
        }
    });

    return touched;
}

// ===============================
// 아이콘 nudge 복원 함수 - 함수명 수정
// ===============================
function restoreIconNudge(nodes = []) {
    nodes.forEach((el) => {
        if (el && el.style) {
            el.style.transform = '';
            el.style.verticalAlign = '';
            el.style.display = '';
            el.style.lineHeight = '';
            el.style.textAlign = '';
            el.style.alignItems = '';
            el.style.justifyContent = '';
        }
    });
}

// ===============================
// 폰트어썸 중앙정렬 스타일 - 수정됨
// ===============================
function injectIconContainerStyle(rootDocument = document) {
    const style = rootDocument.createElement('style');
    style.setAttribute('data-pdf-icon-container', '1');
    style.textContent = `
        /* insight-point 전용 스타일 */
        .pdf-clone .insight-point {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            margin-bottom: 4px !important;
        }
        
        /* 아이콘 컨테이너들 */
        .pdf-clone .insight-icon,
        .pdf-clone .pattern-icon {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 1 !important;
            vertical-align: middle !important;
            flex-shrink: 0 !important;
        }
        
        /* 다른 원/배지 컨테이너는 기존대로 */
        .pdf-clone .badge-circle,
        .pdf-clone .round-icon {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 1 !important;
            vertical-align: middle !important;
        }
        
        /* 제외 컨테이너 안의 아이콘은 nudge 제거 */
        .pdf-clone .badge-circle i,
        .pdf-clone .round-icon i {
            display: inline-block !important;
            line-height: 1 !important;
            vertical-align: middle !important;
            transform: translateY(0) !important;
        }
        
        /* PDF 최적화 스타일 추가 */
        .pdf-clone * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
        }
        
        /* 색상과 선명도 개선 */
        .pdf-clone {
            background: #ffffff !important;
        }
        
        .pdf-clone canvas,
        .pdf-clone img {
            image-rendering: -webkit-optimize-contrast !important;
            image-rendering: crisp-edges !important;
        }
    `;
    rootDocument.head.appendChild(style);
    return style;
}

// ===============================
// insight-point 수동 정렬 (원본 DOM에서 직접 처리) - 수정!
// ===============================
function alignInsightPointsInOriginal() {
    const touched = [];
    const insightPoints = document.querySelectorAll('.insight-point');
    
    insightPoints.forEach((point, index) => {
        // 원본 스타일 백업
        const originalStyle = point.getAttribute('style') || '';
        
        // insight-point를 flex로 변경
        point.style.setProperty('display', 'flex', 'important');
        point.style.setProperty('align-items', 'center', 'important');
        point.style.setProperty('gap', '8px', 'important');
        point.style.setProperty('margin-bottom', '4px', 'important');
        touched.push({ element: point, originalStyles: originalStyle });
        
        // 내부 아이콘 컨테이너 조정
        const iconContainer = point.querySelector('.pattern-icon, .insight-icon');
        if (iconContainer) {
            const iconOriginalStyle = iconContainer.getAttribute('style') || '';
            
            iconContainer.style.setProperty('flex-shrink', '0', 'important');
            iconContainer.style.setProperty('display', 'inline-flex', 'important');
            iconContainer.style.setProperty('align-items', 'center', 'important');
            iconContainer.style.setProperty('justify-content', 'center', 'important');
            iconContainer.style.setProperty('vertical-align', 'middle', 'important');
            touched.push({ element: iconContainer, originalStyles: iconOriginalStyle });
            
            // 아이콘 자체 조정
            const icon = iconContainer.querySelector('i, svg');
            if (icon) {
                const iconElementOriginalStyle = icon.getAttribute('style') || '';
                
                icon.style.setProperty('transform', 'translateY(0px)', 'important');
                icon.style.setProperty('vertical-align', 'middle', 'important');
                icon.style.setProperty('line-height', '1', 'important');
                touched.push({ element: icon, originalStyles: iconElementOriginalStyle });
            }
        }
        
        // 텍스트 부분 조정
        const textElement = point.querySelector('.text-sm, p, div:not(.pattern-icon):not(.insight-icon)');
        if (textElement) {
            const textOriginalStyle = textElement.getAttribute('style') || '';
            
            textElement.style.setProperty('margin', '0', 'important');
            textElement.style.setProperty('line-height', '1.4', 'important');
            textElement.style.setProperty('display', 'flex', 'important');
            textElement.style.setProperty('align-items', 'center', 'important');
            touched.push({ element: textElement, originalStyles: textOriginalStyle });
        }
    });
    
    return touched;
}

function restoreInsightPointsInOriginal(touched = []) {
    console.log(`🔄 Restoring ${touched.length} elements`);
    touched.forEach(({ element, originalStyles }) => {
        if (element && element.parentNode) {
            element.setAttribute('style', originalStyles);
        }
    });
}

// ===============================
// 출결 테이블 최적화/복원 (클론에서만 사용)
// ===============================
function optimizeAttendanceTable(root) {
    const attendanceContainer = root.querySelector('.card .overflow-auto');
    if (attendanceContainer) {
        attendanceContainer.style.overflow = 'visible';
        attendanceContainer.style.maxHeight = 'none';
        const table = attendanceContainer.querySelector('table');
        if (table) {
            table.style.width = '100%';
            table.style.tableLayout = 'auto';
            const cells = table.querySelectorAll('td, th');
            cells.forEach((cell) => {
                cell.style.whiteSpace = 'nowrap';
                cell.style.overflow = 'visible';
            });
        }
    }
}

function restoreAttendanceTable(root) {
    const attendanceContainer = root.querySelector('.card .overflow-auto');
    if (attendanceContainer) {
        attendanceContainer.style.overflow = 'auto';
        attendanceContainer.style.maxHeight = '200px';
        const table = attendanceContainer.querySelector('table');
        if (table) {
            const cells = table.querySelectorAll('td, th');
            cells.forEach((cell) => {
                cell.style.whiteSpace = '';
                cell.style.overflow = '';
            });
        }
    }
}

// ===============================
// 회원/파일명 정보
// ===============================
function getMemberInfo() {
    const urlParams = new URLSearchParams(window.location.search);
    const memberInfo = document.getElementById('member-info');
    const memberID = memberInfo?.dataset.memberId;
    return {
        memberID: memberID || 'unknown',
        memberUuid:
            urlParams.get('member_uuid') || document.getElementById('member_uuid')?.value,
        date: // 리포트 시작 일자(없으면 오늘)
            urlParams.get('date') ||
            document.getElementById('date')?.value ||
            document.getElementById('hidden-date')?.getAttribute('value'),
    };
}

// ===============================
// 토스트 알림
// ===============================
function showNotification(message, type = 'info') {
    const existing = document.querySelector('.pdf-notification');
    if (existing) existing.remove();

    const el = document.createElement('div');
    el.className = 'pdf-notification';
    el.style.cssText = `
    position: fixed; top: 20px; right: 20px; padding: 16px; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; color: white; font-weight: 500;
    max-width: 300px; animation: slideIn 0.3s ease;
    ${type === 'success' ? 'background:#10b981' : type === 'error' ? 'background:#ef4444' : 'background:#3b82f6'}
  `;
    el.innerHTML = `
    <div style="display:flex;align-items:center;">
      <span style="margin-right:8px;">${type === 'success' ? '✅' : type === 'error' ? '⚠️' : 'ℹ️'}</span>
      <span>${message}</span>
    </div>
  `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// ===============================
/** 캔버스 ID 스탬프 (원본 DOM의 canvas에 data-canvas-id 부여, 매칭용) */
// ===============================
function stampCanvasIds(root = document) {
    const canvases = root.querySelectorAll('canvas');
    let seq = 0;
    const now = Date.now();
    canvases.forEach((c) => {
        if (!c.dataset.canvasId) c.dataset.canvasId = `cv-${now}-${seq++}`;
    });
}

// ===============================
// 오프스크린 클론 생성 (원본 DOM 비파괴) - 용량 최적화
// ===============================
function buildPrintableClone(section, sectionWidth = 1400, includeTopContent = false) { // 1400px로 축소
    const container = document.createElement('div');
    container.style.cssText = `
    position:absolute; left:-9999px; top:0; width:${sectionWidth}px;
    background:#fff; overflow:visible; z-index:0;
  `;

    const wrapper = document.createElement('div');
    wrapper.style.cssText = `width:${sectionWidth}px; display: flow-root; overflow:auto; box-sizing: border-box;`;
    wrapper.className = 'pdf-clone';

    if (includeTopContent) {
        const top = document.querySelector('.top-content-container');
        if (top) {
            const topClone = top.cloneNode(true);
            topClone.style.marginBottom = '16px';
            // 인쇄에서 잘리거나 숨김 방지
            topClone.style.breakInside = 'avoid';
            topClone.style.pageBreakInside = 'avoid';
            wrapper.appendChild(topClone);
        }
    }

    const sectionClone = section.cloneNode(true);
    wrapper.appendChild(sectionClone);

    container.appendChild(wrapper);
    document.body.appendChild(container);

    const originalRoot = section.__sourceRoot || section;
    return { container, cloneRoot: wrapper, originalRoot };
}

// ===============================
// 클론 내부의 canvas를 원본 canvas 이미지로 치환 - 용량 최적화
// ===============================
function replaceCloneCanvasesWithOriginalImages(cloneRoot, originalRoot) {
    const cloneCanvases = cloneRoot.querySelectorAll('canvas');
    cloneCanvases.forEach((cloneCanvas) => {
        const id = cloneCanvas.dataset.canvasId;
        if (!id) return;
        const originalCanvas = originalRoot.querySelector(`canvas[data-canvas-id="${id}"]`);
        if (!originalCanvas) return;
        if (originalCanvas.width === 0 || originalCanvas.height === 0) return;

        const img = document.createElement('img');
        // JPEG로 변환하여 용량 대폭 절약 (차트는 JPEG로도 충분히 선명)
        img.src = originalCanvas.toDataURL('image/jpeg', 0.85);
        
        // 스타일/크기 보존
        const style = cloneCanvas.getAttribute('style');
        if (style) img.setAttribute('style', style);
        if (!img.style.width) img.style.width = cloneCanvas.style.width || `${originalCanvas.width}px`;
        if (!img.style.height) img.style.height = cloneCanvas.style.height || `${originalCanvas.height}px`;

        cloneCanvas.replaceWith(img);
    });
}

// ===============================
// 테이블 안전 중앙정렬용 스타일 주입
// ===============================
function injectTableCenteringStyle(rootDocument = document) {
    const style = rootDocument.createElement('style');
    style.setAttribute('data-pdf-centering', '1');
    style.textContent = `
    .pdf-clone table { border-collapse: separate; border-spacing: 0; }
    .pdf-clone th, .pdf-clone td { vertical-align: middle !important; line-height: normal !important; }
    .pdf-clone th > *, .pdf-clone td > * { vertical-align: middle !important; }
  `;
    rootDocument.head.appendChild(style);
    return style;
}

// ===============================
// 섹션 캔버스 생성 (클론 기반 캡처) - 용량 최적화 버전
// ===============================
async function createSectionCanvas(section, sectionWidth = 1600, includeTopContent = false) { // 1800→1600으로 축소
    const { container, cloneRoot, originalRoot } =
        buildPrintableClone(section, sectionWidth, includeTopContent);

    // 1) 웹폰트 로딩 완료까지 대기 (베이스라인 문제 방지)
    if (document.fonts && document.fonts.ready) {
        try { 
            await document.fonts.ready; 
            // 적당한 대기 시간으로 폰트 완전 적용 보장
            await new Promise(resolve => setTimeout(resolve, 300));
        } catch { }
    }

    // 중앙 정렬용 스타일 (클론 범위에만)
    const styleEl = injectTableCenteringStyle(document);
    const iconContainerStyleEl = injectIconContainerStyle(document);

    optimizeAttendanceTable(cloneRoot);
    replaceCloneCanvasesWithOriginalImages(cloneRoot, originalRoot);

    // 전역 텍스트 보정: 그래프 제외 전체 텍스트를 -10px
    const globalNudged = nudgeAllTextExceptCharts(cloneRoot, PDF_TEXT_NUDGE_PX);
    
    // DOM이 완전히 안정화될 때까지 대기
    await new Promise(resolve => {
        const observer = new MutationObserver(() => {
            observer.disconnect();
            resolve();
        });
        observer.observe(cloneRoot, { childList: true, subtree: true });
        setTimeout(() => {
            observer.disconnect();
            resolve(); // fallback
        }, 300);
    });
    
    const iconNudged = nudgeAllIcons(cloneRoot, PDF_TEXT_NUDGE_PX);

    await waitForContentToLoad();

    // 용량 최적화된 html2canvas 옵션
    const canvas = await html2canvas(cloneRoot, {
        scale: 1.8,              // 2.0→1.8로 약간 축소 (용량 30% 절약)
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        width: sectionWidth,
        height: cloneRoot.scrollHeight,
        windowWidth: sectionWidth,
        windowHeight: cloneRoot.scrollHeight,
        logging: false,
        ignoreElements: (el) =>
            el.tagName === 'SCRIPT' ||
            el.classList?.contains('non-printable') ||
            el.style.display === 'none' ||
            el.style.visibility === 'hidden'
    });

    restoreAttendanceTable(cloneRoot);
    restoreNudgedAll(globalNudged);
    restoreIconNudge(iconNudged);

    container.remove();
    if (styleEl && styleEl.parentNode) styleEl.parentNode.removeChild(styleEl);
    if (iconContainerStyleEl && iconContainerStyleEl.parentNode) iconContainerStyleEl.parentNode.removeChild(iconContainerStyleEl);

    return canvas;
}

// ===============================
// 캔버스를 PDF에 추가 (자동 분할) - 용량 최적화
// ===============================
function addCanvasToPDF(pdf, canvas, margin = 3) {
    const pdfW = pdf.internal.pageSize.getWidth();
    const pdfH = pdf.internal.pageSize.getHeight();
    const availW = pdfW - margin * 2;
    const availH = pdfH - margin * 2;

    const imgW = availW;
    const imgH = (canvas.height * imgW) / canvas.width;
    
    // JPEG로 변환하여 용량 대폭 절약 (품질은 유지)
    const imgData = canvas.toDataURL('image/jpeg', 0.82); // 0.82 품질로 최적화

    if (imgH <= availH) {
        pdf.addImage(imgData, 'JPEG', margin, margin, imgW, imgH);
        return false;
    }

    // 여러 페이지 분할
    let y = 0;
    let first = true;
    const sliceHeight = (availH * canvas.width) / imgW;

    while (y < canvas.height) {
        if (!first) pdf.addPage();
        const srcH = Math.min(sliceHeight, canvas.height - y);

        const temp = document.createElement('canvas');
        const ctx = temp.getContext('2d');
        temp.width = canvas.width;
        temp.height = srcH;

        ctx.drawImage(canvas, 0, y, canvas.width, srcH, 0, 0, canvas.width, srcH);
        const part = temp.toDataURL('image/jpeg', 0.82); // JPEG 0.82 품질
        const partH = (srcH * imgW) / canvas.width;

        pdf.addImage(part, 'JPEG', margin, margin, imgW, partH);

        y += srcH;
        first = false;
    }
    return true;
}

// =============================== 
// forth-body를 과목 2개씩 분할 (원본 참조 연결)
// =============================== 
function splitForthBodyBySubjects(forthBody) {
    // 캔버스 매칭용 ID 스탬프 (forthBody 범위에 대해서 한 번)
    stampCanvasIds(forthBody); 

    const subjectContainers = forthBody.querySelectorAll('.subject-container');
    const header = forthBody.querySelector('.header');
    const slideContainer = forthBody.querySelector('.slide-container');

    if (subjectContainers.length <= 1) return [forthBody];

    const pages = [];
    for (let i = 0; i < subjectContainers.length; i += 2) {
        const tempContainer = document.createElement('div');
        tempContainer.className = 'forth-body';

        const newSlideContainer = slideContainer?.cloneNode(false) || document.createElement('div');
        newSlideContainer.className = 'slide-container p-5';

        if (header) newSlideContainer.appendChild(header.cloneNode(true));

        const count = Math.min(2, subjectContainers.length - i);
        const grid = document.createElement('div');
        grid.className = subjectContainers.length === 1 ? 'grid grid-cols-1' : 'grid grid-cols-2';
        if (subjectContainers.length === 1) grid.style.padding = '0 30px';

        for (let j = i; j < i + count; j++) {
            grid.appendChild(subjectContainers[j].cloneNode(true));
        }

        newSlideContainer.appendChild(grid);
        tempContainer.appendChild(newSlideContainer);

        // 원본 forthBody 참조 저장 (클론에서 원본 캔버스 픽셀을 가져올 때 사용)
        tempContainer.__sourceRoot = forthBody;

        pages.push(tempContainer);
    }
    return pages;
}

// ===============================
// 콘솔 경고 억제 (선택사항)
// ===============================
function suppressBlobWarnings() {
    const originalWarn = console.warn;
    console.warn = function(message, ...args) {
        // blob 관련 HTTPS 경고 필터링
        if (typeof message === 'string' && 
            (message.includes('blob') && message.includes('insecure connection'))) {
            return; // 경고 숨김
        }
        originalWarn.apply(console, [message, ...args]);
    };
}

// ===============================
// 브라우저 호환성 체크
// ===============================
function checkDownloadSupport() {
    const features = {
        blob: typeof Blob !== 'undefined',
        fileReader: typeof FileReader !== 'undefined',
        download: 'download' in document.createElement('a'),
        https: location.protocol === 'https:'
    };
    
    console.log('다운로드 지원 상태:', features);
    return features;
}

// ===============================
// 메인: 섹션별 PDF 생성 - 최적화된 버전
// ===============================
async function downloadSectionBasedPDF() {
    // 브라우저 지원 상태 체크
    const support = checkDownloadSupport();
    
    if (!support.blob || !support.fileReader) {
        showNotification('브라우저가 파일 다운로드를 지원하지 않습니다.', 'error');
        return;
    }

    if (!support.https) {
        console.warn('HTTPS가 아닌 환경에서 실행 중입니다. Blob URL 경고가 발생할 수 있습니다.');
        // 선택적으로 경고 억제
        suppressBlobWarnings();
    }

    if (!initializePDF()) {
        showNotification('PDF 라이브러리를 로드할 수 없습니다.', 'error');
        return;
    }

    const btn = document.getElementById('download-landscape') || document.getElementById('download');
    if (!btn) {
        showNotification('다운로드 버튼을 찾을 수 없습니다.', 'error');
        return;
    }
    const originalText = btn.innerHTML;

    // 전역 insight-point 정렬 (원본 DOM에서)
    let globalInsightTouched = [];

    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>PDF 생성 중...';

        await waitForLibraries();

        // 전체 문서에 대해 한 번 스탬프 (안전)
        stampCanvasIds();

        // 원본 DOM에서 insight-point들 정렬
        globalInsightTouched = alignInsightPointsInOriginal();

        const all = [];
        const firstBody = document.querySelector('.first-body');
        const secondBody = document.querySelector('.second-body');
        const thirdBody = document.querySelector('.third-body');
        if (firstBody) all.push(firstBody);
        if (secondBody) all.push(secondBody);
        if (thirdBody) all.push(thirdBody);

        const forthBody = document.querySelector('.forth-body');
        if (forthBody) all.push(...splitForthBodyBySubjects(forthBody));

        const fifthBodies = document.querySelectorAll('.fifth-body');
        if (fifthBodies.length > 0) all.push(fifthBodies[0]);

        if (!all.length) {
            showNotification('처리할 섹션을 찾을 수 없습니다.', 'error');
            return;
        }

        // 용량 최적화된 PDF 설정
        const pdf = new window.jsPDF({ 
            orientation: 'landscape', 
            unit: 'mm', 
            format: 'a4',
            compress: true  // PDF 압축 활성화
        });

        for (let i = 0; i < all.length; i++) {
            const includeTop = (i === 0); // 첫 페이지에만 상단 정보 포함
            showNotification(`페이지 ${i + 1}/${all.length} 처리 중...`, 'info');

            // 용량 최적화된 캔버스 크기 (1600px)
            const canvas = await createSectionCanvas(all[i], 1600, includeTop);
            if (i !== 0) pdf.addPage();
            
            // 여백을 3mm로 줄여서 이미지를 약간 더 크게 표시
            addCanvasToPDF(pdf, canvas, 3);
        }

        const currentDate = new Date().toISOString().split('T')[0];
        const { memberID, date } = getMemberInfo();
        console.log(memberID);
        const filename = `Report_${memberID}_${date || currentDate}.pdf`;

        // PDF 저장
        pdf.save(filename);

        showNotification('PDF 다운로드가 완료되었습니다!', 'success');
    } catch (err) {
        console.error('PDF 생성 오류:', err);
        // 구체적인 오류 메시지 제공
        let errorMessage = 'PDF 생성 중 오류가 발생했습니다.';
        if (err.message.includes('팝업')) {
            errorMessage = '팝업이 차단되었습니다. 브라우저 설정에서 팝업을 허용해주세요.';
        } else if (err.message.includes('blob') || err.message.includes('insecure')) {
            errorMessage = 'HTTPS 환경에서 다시 시도해주세요.';
        } else if (err.message.includes('html2canvas')) {
            errorMessage = '페이지 렌더링 중 오류가 발생했습니다. 페이지를 새로고침 후 다시 시도해주세요.';
        } else if (err.message.includes('font')) {
            errorMessage = '폰트 로딩 오류입니다. 잠시 후 다시 시도해주세요.';
        }
        showNotification(errorMessage, 'error');
    } finally {
        // 원본 DOM 복원
        restoreInsightPointsInOriginal(globalInsightTouched);
        
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// 안전한 PDF 다운로드 - 개선된 버전
async function safeDownloadPDF(pdf, filename) {
    try {
        // HTTPS 환경에서는 기본 save() 사용
        if (location.protocol === 'https:') {
            pdf.save(filename);
            return;
        }

        // HTTP 환경에서는 대안 방법 사용
        const pdfBlob = pdf.output('blob');
        const reader = new FileReader();
        
        return new Promise((resolve, reject) => {
            reader.onload = function() {
                const link = document.createElement('a');
                link.href = reader.result;
                link.download = filename;
                link.style.display = 'none';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Blob URL 정리
                setTimeout(() => {
                    if (link.href.startsWith('blob:')) {
                        URL.revokeObjectURL(link.href);
                    }
                }, 1000);
                
                resolve();
            };
            reader.onerror = reject;
            reader.readAsDataURL(pdfBlob);
        });
    } catch (error) {
        console.warn('기본 다운로드 실패, 대체 방법 시도:', error);
        
        // 최후 대안: 새 창에서 PDF 열기
        const pdfDataUri = pdf.output('datauristring');
        const newWindow = window.open();
        if (newWindow) {
            newWindow.document.write(`
                <iframe width="100%" height="100%" src="${pdfDataUri}"></iframe>
            `);
            newWindow.document.title = filename;
        } else {
            throw new Error('팝업이 차단되어 다운로드할 수 없습니다. 팝업을 허용해주세요.');
        }
    }
}

// ===============================
// 이벤트 바인딩 & 스타일 - 개선된 버전
// ===============================
document.addEventListener('DOMContentLoaded', function () {
    // 라이브러리 로딩 확인을 좀 더 늦게 체크
    setTimeout(() => {
        if (initializePDF()) {
            console.log('jsPDF 라이브러리 로드 확인');
        } else {
            console.error('jsPDF 라이브러리 로드 실패');
        }
    }, 1500); // 1초 → 1.5초로 증가

    const downloadBtn = document.getElementById('download-landscape') || document.getElementById('download');
    if (downloadBtn) {
        downloadBtn.removeEventListener('click', downloadSectionBasedPDF);
        downloadBtn.addEventListener('click', downloadSectionBasedPDF);
    }
});

// 프린트/버튼 스타일 - 개선된 버전
const style = document.createElement('style');
style.textContent = `
    @media print {
        body {
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important;
            color-adjust: exact !important;
        }
        .pdf-download-btn, .calendar-btn, .non-printable {
            display:none !important;
        }
        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    .pdf-download-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff; border:0; padding:12px 24px; border-radius:8px; font-weight:600;
        cursor:pointer; transition: all .3s ease; display:inline-flex; align-items:center; gap:8px;
    }
    .pdf-download-btn:hover { 
        transform: translateY(-2px); 
        box-shadow:0 8px 25px rgba(0,0,0,.15); 
    }
    .pdf-download-btn:disabled { 
        opacity:.7; 
        cursor:not-allowed; 
        transform:none; 
    }
    .pdf-notification { 
        animation: slideIn .3s ease; 
    }
    @keyframes slideIn { 
        from {transform:translateX(100%);opacity:0;} 
        to {transform:translateX(0);opacity:1;} 
    }
    
    /* 추가: PDF 최적화를 위한 전역 스타일 */
    * {
        box-sizing: border-box;
    }
    
    canvas, img {
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
        image-rendering: pixelated;
    }
`;
document.head.appendChild(style);