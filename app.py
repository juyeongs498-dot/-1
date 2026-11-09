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

st.set_page_config(page_title='빨래 끝!', page_icon='🧺', layout='centered', initial_sidebar_state='collapsed')
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
h1{font-size:27px;letter-spacing:-1px;margin:6px 0}p{margin:5px 0;color:#53647c;font-size:13px}
.card{margin:12px 0;background:white;border:1px solid #dce4f0;border-radius:22px;padding:20px;text-align:center}
.badge{display:inline-block;border-radius:20px;padding:4px 12px;background:#eaf0ff;color:#234db1;font-size:13px}
#clock{font-size:54px;font-weight:800;letter-spacing:-2px;margin:10px 0;line-height:1.1}
label{display:block;font-size:14px;font-weight:600;margin:10px 0 6px}
input{width:100%;border:1px solid #b9c7dc;border-radius:12px;padding:10px;font-size:18px;background:white;color:#17243d}
button{cursor:pointer;border:0;border-radius:12px;padding:12px;font-size:15px;font-weight:650;min-height:44px}
.primary{background:#245ae8;color:white;width:100%;margin-top:10px}.secondary{background:#e6ecf7;color:#254b92}
.row{display:flex;gap:8px;margin-top:9px}.row button{flex:1}button:disabled{opacity:.5;cursor:default}
.note{font-size:11px;line-height:1.45;color:#53647c;margin-top:12px}#feedback{font-size:12px;min-height:17px;color:#254b92}
@media(max-height:640px){.card{padding:12px;margin:8px 0}#clock{font-size:42px}h1{font-size:24px}}
</style></head><body>
<h1>🧺 빨래 끝!</h1><p>나만의 세탁 타이머 · 남은 시간을 입력하세요</p>
<div class="card" role="status"><span class="badge" id="status">준비 완료</span>
<div id="clock" aria-label="남은 시간">00:00</div><p id="end">세탁기에 표시된 시간 기준이에요</p></div>
<label for="minutes">세탁기 남은 시간 (분)</label>
<input type="number" id="minutes" min="1" max="720" step="1" value="55" inputmode="numeric">
<button id="start" class="primary">🧺 세탁 시작 · 소리 켜기</button>
<div class="row"><button id="sound" class="secondary">🔊 소리 테스트</button><button id="reset" class="secondary">타이머 취소</button></div>
<p id="feedback" aria-live="polite"></p>
<div class="note">⚠ 웹 화면을 켜 둔 상태에서 사용하세요. 휴대폰 잠금·웹 종료 시 소리 알림은 보장되지 않아요.<br>실제 세탁 완료를 감지하지 않고 입력한 시간이 지나면 알려 줘요.</div>
<script>
const $=id=>document.getElementById(id),key='laundry-personal-v1';
let deadline=0,fired=false,ctx=null,storageOK=true;
function save(){try{if(deadline)localStorage.setItem(key,String(deadline));else localStorage.removeItem(key);}catch(e){storageOK=false;}}
try{const v=Number(localStorage.getItem(key));if(Number.isFinite(v)&&v>0)deadline=v;}catch(e){storageOK=false;}
function format(s){const h=Math.floor(s/3600),m=Math.floor(s%3600/60),v=s%60;return(h?String(h).padStart(2,'0')+':':'')+String(m).padStart(2,'0')+':'+String(v).padStart(2,'0');}
async function enable(){try{ctx=ctx||new(window.AudioContext||window.webkitAudioContext)();await ctx.resume();return ctx.state==='running';}catch(e){return false;}}
function ring(){if(!ctx||ctx.state!=='running')return false;const t=ctx.currentTime;for(let i=0;i<6;i++){const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.frequency.value=i%2?880:660;g.gain.setValueAtTime(0,t+i*.32);g.gain.linearRampToValueAtTime(.12,t+i*.32+.02);g.gain.exponentialRampToValueAtTime(.001,t+i*.32+.28);o.start(t+i*.32);o.stop(t+i*.32+.3);}return true;}
function render(){
 const s=deadline?Math.max(0,Math.ceil((deadline-Date.now())/1000)):0,running=deadline>Date.now();
 $('clock').textContent=format(s);$('status').textContent=!deadline?'준비 완료':running?'세탁 중':'빨래가 끝났어요!';
 $('end').textContent=deadline?'완료 예정 '+new Date(deadline).toLocaleTimeString('ko-KR',{hour:'2-digit',minute:'2-digit'}):'세탁기에 표시된 시간 기준이에요';
 $('start').disabled=running;$('minutes').disabled=running;$('reset').disabled=!deadline;
 $('start').textContent=deadline&&!running?'🧺 다음 세탁 시작':'🧺 세탁 시작 · 소리 켜기';
 if(deadline&&!running&&!fired){if(ring()){fired=true;$('feedback').textContent='세탁물을 꺼내 주세요!';}else{$('feedback').textContent='시간이 됐어요! 소리를 내려면 소리 테스트를 눌러 주세요.';}}
}
$('start').onclick=async()=>{
 const raw=$('minutes').value.trim(),n=Number(raw);
 if(!raw||!Number.isInteger(n)||n<1||n>720){$('feedback').textContent='1~720 사이의 정수(분)를 입력해 주세요.';return;}
 const ok=await enable();deadline=Date.now()+n*60000;fired=false;save();
 $('feedback').textContent=(ok?'소리 켜짐 · 화면을 켜 두세요.':'소리를 켜지 못했어요. 화면 표시로 확인해 주세요.')+(storageOK?'':' 저장이 제한돼 새로고침하면 사라질 수 있어요.');render();
};
$('sound').onclick=async()=>{if(await enable()){ring();$('feedback').textContent='소리 테스트 중 · 휴대폰 볼륨을 확인하세요.';}else $('feedback').textContent='소리를 켤 수 없어요. 브라우저와 볼륨 설정을 확인하세요.';};
$('reset').onclick=()=>{if(!confirm('타이머를 취소할까요?'))return;deadline=0;fired=false;save();$('feedback').textContent='타이머를 취소했어요.';render();};
document.addEventListener('visibilitychange',()=>{if(!document.hidden)render();});
if(deadline)$('feedback').textContent='이전 타이머를 불러왔어요. 소리 테스트를 눌러 소리를 다시 켜 주세요.';
setInterval(render,500);render();
</script></body></html>''', height=500, scrolling=True)
