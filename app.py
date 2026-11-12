"""빨래 끝 알리미 — 1인용
GitHub에 app.py, requirements.txt 업로드 → Streamlit Community Cloud 배포.
Supabase, Secrets, 회원가입이 필요 없습니다.
알림은 웹 화면을 켜 둔 상태의 소리 알림이며 백그라운드 푸시가 아닙니다.
휴대폰 잠금, 절전, 탭 종료 시 정확한 알림은 보장되지 않습니다.
예상 시간 기준이며 세탁기와 직접 연결되지 않습니다.
타이머는 브라우저 저장소에 저장을 시도합니다. 브라우저 설정/임베디드
저장소 제한/앱 주소 변경 시 유지되지 않을 수 있습니다.
다른 사용자나 기기와 타이머를 공유하지 않습니다.
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title='빨래 마무리 도우미', page_icon='🧺', layout='centered', initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp{background:#f4f7fc}
[data-testid="stHeader"]{height:0;background:transparent}
.block-container{max-width:440px;padding:.6rem .8rem}
[data-testid="stVerticalBlock"]{gap:.3rem}
</style>''', unsafe_allow_html=True)

components.html('''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,sans-serif;color:#17243d;background:#f4f7fc}
h1{font-size:25px;letter-spacing:-1px;margin:6px 0}p{margin:5px 0;color:#53647c;font-size:13px}
.card{margin:8px 0;background:white;border:1px solid #dce4f0;border-radius:22px;padding:12px;text-align:center}
.badge{display:inline-block;border-radius:20px;padding:4px 12px;background:#eaf0ff;color:#234db1;font-size:13px}
#clock{font-size:42px;font-weight:800;letter-spacing:-2px;margin:10px 0;line-height:1.1}
label{display:block;font-size:14px;font-weight:600;margin:10px 0 6px}
select,textarea,input{width:100%;border:1px solid #b9c7dc;border-radius:12px;padding:8px;font-size:16px;background:white;color:#17243d}
button{cursor:pointer;border:0;border-radius:12px;padding:12px;font-size:15px;font-weight:650;min-height:44px}
.primary{background:#245ae8;color:white;width:100%;margin-top:10px}.secondary{background:#e6ecf7;color:#254b92}
.row{display:flex;gap:8px;margin-top:9px}.row button{flex:1}button:disabled{opacity:.5;cursor:default}
.note{font-size:11px;line-height:1.45;color:#53647c;margin-top:12px}#feedback{font-size:12px;min-height:17px;color:#254b92}
@media(max-height:640px){.card{padding:12px;margin:8px 0}#clock{font-size:42px}h1{font-size:24px}}
</style></head><body>
<h1>🧺 빨래 마무리 도우미</h1><p>시간만 재지 않고, 꺼내서 정리할 때까지</p>
<label for="preset">자주 하는 빨래</label>
<select id="preset"><option>일반 빨래</option><option>수건</option><option>교복</option><option>침구</option></select>
<details id="settings"><summary>시간·마무리 메모 저장</summary>
<p>아래 시간과 메모를 바꾼 뒤 저장하세요. 예시는 세탁 지침이 아니며 의류 라벨에 맞게 수정하세요.</p>
<button id="savePreset" class="secondary">현재 시간·메모를 선택한 종류에 저장</button></details>
<div class="card" role="status"><span class="badge" id="status">준비 완료</span>
<div id="clock" aria-label="남은 시간">00:00</div><p id="end">세탁기에 표시된 시간 기준이에요</p></div>
<label for="minutes">세탁기 남은 시간 (분)</label>
<input type="number" id="minutes" min="1" max="720" step="1" value="55" inputmode="numeric">
<label for="care">끝나고 챙길 것 (직접 수정 가능)</label>
<input id="care" maxlength="160" placeholder="예: 건조기 금지 옷 먼저 꺼내기">
<div id="reminder" style="display:none;background:#fff0d8;padding:10px;border-radius:12px;font-size:14px;overflow-wrap:anywhere"></div>
<button id="done" class="primary" style="display:none;background:#16815c">✓ 빨래 꺼냈어요</button>
<button id="start" class="primary">🧺 세탁 시작 · 소리 켜기</button>
<div class="row"><button id="sound" class="secondary">🔊 소리 테스트</button><button id="reset" class="secondary">타이머 취소</button></div>
<p id="feedback" aria-live="polite"></p>
<div class="note">⚠ 웹 화면을 켜 둔 상태에서 사용하세요. 휴대폰 잠금·웹 종료 시 소리 알림은 보장되지 않아요.<br>실제 세탁 완료를 감지하지 않고 입력한 시간이 지나면 알려 줘요.</div>
<script>
const $=id=>document.getElementById(id),key='laundry-personal-v1';
let deadline=0,fired=false,ctx=null,storageOK=true,completed=false,activeCare='',activeName='';
const stateKey='laundry-finish-state-v2',presetKey='laundry-presets-v2';
let presets={'일반 빨래':{minutes:55,care:'세탁물을 꺼내 널거나 건조 준비하기'},'수건':{minutes:60,care:'수건을 꺼내 펼쳐 널기 · 라벨 확인'},'교복':{minutes:40,care:'옷 라벨 확인 · 건조기 금지 품목 따로 꺼내기'},'침구':{minutes:90,care:'뭉친 곳을 펴서 충분히 말리기 · 라벨 확인'}};
try{const v=JSON.parse(localStorage.getItem(presetKey));if(v&&typeof v==='object')for(const k of Object.keys(presets)){const x=v[k];if(x&&Number.isInteger(x.minutes)&&x.minutes>=1&&x.minutes<=720&&typeof x.care==='string')presets[k]={minutes:x.minutes,care:x.care.slice(0,160)};}}catch(e){storageOK=false;}
function saveState(){try{localStorage.setItem(stateKey,JSON.stringify({deadline,completed,activeCare,activeName}));}catch(e){storageOK=false;}}
try{const v=JSON.parse(localStorage.getItem(stateKey));if(v&&Number.isFinite(v.deadline)&&v.deadline>=0){deadline=v.deadline;completed=v.completed===true;activeCare=typeof v.activeCare==='string'?v.activeCare.slice(0,160):'';activeName=typeof v.activeName==='string'?v.activeName:'';}}catch(e){storageOK=false;}
function loadPreset(){const p=presets[$('preset').value];$('minutes').value=p.minutes;$('care').value=p.care;}
$('preset').onchange=loadPreset;
$('savePreset').onclick=()=>{const n=Number($('minutes').value);if(!Number.isInteger(n)||n<1||n>720){$('feedback').textContent='시간은 1~720분으로 입력하세요.';return;}presets[$('preset').value]={minutes:n,care:$('care').value};try{localStorage.setItem(presetKey,JSON.stringify(presets));$('feedback').textContent='이 브라우저에 시간과 메모를 저장했어요.';}catch(e){$('feedback').textContent='저장이 제한된 브라우저예요.';} };
function save(){saveState();}

function format(s){const h=Math.floor(s/3600),m=Math.floor(s%3600/60),v=s%60;return(h?String(h).padStart(2,'0')+':':'')+String(m).padStart(2,'0')+':'+String(v).padStart(2,'0');}
async function enable(){try{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();await ctx.resume();return ctx.state==='running';}catch(e){return false;}}
function ring(){if(!ctx||ctx.state!=='running')return false;const t=ctx.currentTime;for(let i=0;i<6;i++){const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.frequency.value=i%2?880:660;g.gain.setValueAtTime(0,t+i*.32);g.gain.linearRampToValueAtTime(.12,t+i*.32+.02);g.gain.exponentialRampToValueAtTime(.001,t+i*.32+.28);o.start(t+i*.32);o.stop(t+i*.32+.3);}return true;}
function render(){
 const s=deadline?Math.max(0,Math.ceil((deadline-Date.now())/1000)):0,running=deadline>Date.now();
 $('clock').textContent=format(s);$('status').textContent=!deadline?'준비 완료':running?'세탁 중':(completed?'마무리 완료 ✓':'빨래를 꺼내 주세요!');
 $('end').textContent=deadline?'완료 예정 '+new Date(deadline).toLocaleTimeString('ko-KR',{hour:'2-digit',minute:'2-digit'}):'세탁기에 표시된 시간 기준이에요';
 const pending=deadline>0&&!running&&!completed;
 $('start').disabled=running||pending;$('minutes').disabled=running||pending;$('preset').disabled=running||pending;$('care').disabled=running||pending;$('savePreset').disabled=running||pending;$('reset').disabled=!deadline;
 $('done').style.display=pending?'block':'none';$('reminder').style.display=deadline?'block':'none';
 $('reminder').textContent=(completed?'✓ 처리 완료 · ':running?'끝나면 챙겨요 · ':'아직 꺼내지 않았어요 · ')+activeName+': '+(activeCare||'세탁물을 꺼내 주세요.');
 $('start').textContent=deadline&&!running?'🧺 다음 세탁 시작':'🧺 세탁 시작 · 소리 켜기';
 if(deadline&&!running&&!completed&&!fired){if(ring()){fired=true;$('feedback').textContent='세탁물을 꺼내 주세요!';}else{$('feedback').textContent='시간이 됐어요! 소리를 내려면 소리 테스트를 눌러 주세요.';}}
}
$('start').onclick=async()=>{
 const raw=$('minutes').value.trim(),n=Number(raw);
 if(!raw||!Number.isInteger(n)||n<1||n>720){$('feedback').textContent='1~720 사이의 정수(분)를 입력해 주세요.';return;}
 const ok=await enable();deadline=Date.now()+n*60000;fired=false;completed=false;activeCare=$('care').value;activeName=$('preset').value;save();saveState();
 $('feedback').textContent=(ok?'소리 켜짐 · 화면을 켜 두세요.':'소리를 켜지 못했어요. 화면 표시로 확인해 주세요.')+(storageOK?'':' 저장이 제한돼 새로고침하면 사라질 수 있어요.');render();
};
$('sound').onclick=async()=>{if(await enable()){ring();$('feedback').textContent='소리 테스트 중 · 휴대폰 볼륨을 확인하세요.';}else $('feedback').textContent='소리를 켤 수 없어요. 브라우저와 볼륨 설정을 확인하세요.';};
$('reset').onclick=()=>{if(!confirm('타이머를 취소할까요?'))return;deadline=0;fired=false;completed=false;activeCare=$('care').value;activeName=$('preset').value;save();saveState();$('feedback').textContent='타이머를 취소했어요.';render();};
$('done').onclick=()=>{completed=true;fired=true;saveState();$('feedback').textContent='빨래 꺼내기 완료! 메모에 적은 나머지 마무리도 챙겨 주세요.';render();};
loadPreset();
document.addEventListener('visibilitychange',()=>{if(!document.hidden)render();});
if(deadline)$('feedback').textContent='이전 타이머를 불러왔어요. 소리 테스트를 눌러 소리를 다시 켜 주세요.';
setInterval(render,500);render();
</script></body></html>''', height=650, scrolling=True)
