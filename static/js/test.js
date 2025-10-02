// const dataEl = document.getElementById("chat-data");
// window.myUuid = dataEl.dataset.myUuid;
// window.currentChatPartnerUuid = dataEl.dataset.partnerUuid;

// console.log("내 UUID:", window.myUuid);
// console.log("상대 UUID:", window.currentChatPartnerUuid);
// 이런 식으로 값 가져올 수 있음

// 요소 가져오기
const modal = document.getElementById("myModal");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");

// 모달 열기
openModalBtn.onclick = function() {
    modal.style.display = "flex";
};

// 모달 닫기 (닫기 버튼 클릭 시)
closeModalBtn.onclick = function() {
    modal.style.display = "none";
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}


const CHO_HANGUL = [
'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ',
'ㄹ', 'ㅁ', 'ㅂ','ㅃ', 'ㅅ',
'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ',
'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
];

const HANGUL_START_CHARCODE = "가".charCodeAt();

const CHO_PERIOD = Math.floor("까".charCodeAt() - "가".charCodeAt());
const JUNG_PERIOD = Math.floor("개".charCodeAt() - "가".charCodeAt());

function combine(cho, jung, jong) {
return String.fromCharCode(
    HANGUL_START_CHARCODE + cho * CHO_PERIOD + jung * JUNG_PERIOD + jong
);
}

// 초성검색
function makeRegexByCho(search = "") {
const regex = CHO_HANGUL.reduce(
    (acc, cho, index) =>
    acc.replace(
        new RegExp(cho, "g"),
        `[${combine(index, 0, 0)}-${combine(index + 1, 0, -1)}]`
    ),
    search
);

return new RegExp(`(${regex})`, "g");
}

function includeByCho(search, targetWord) {
return makeRegexByCho(search).test(targetWord);
}

// --------------------------------------

const list = ["사과", "수박", "멜론", "파인애플", "산딸기", "딸기", "망고"];

function _events(target) {
const search = target.value.trim();
const regex = makeRegexByCho(search);

let htmlDummy = "";

list.forEach((item) => {
    if (regex.test(item)) {
    htmlDummy += item.replace(regex, "<mark>$1</mark>") + ', ';
    }
});

document.querySelector(".docs span").innerHTML = search ? htmlDummy : "";
}