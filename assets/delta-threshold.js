// δ-threshold explorer. Usage:
// renderDeltaExplorer(el, {payoffs:{T,R,P,S}, threshold:(p)=>number, cooperate:(p,d)=>number, deviate:(p,d)=>number, labels:{coop, dev}})
// Shows slider for δ, both present values, and whether cooperation is sustainable.
function renderDeltaExplorer(el, cfg){
  let p=Object.assign({T:5,R:3,P:1,S:0},cfg.payoffs), d=0.5;
  el.innerHTML=`<div class="editor"><label>Discount factor δ: <b data-dv>0.50</b></label><input data-d type="range" min="0" max="0.99" step="0.01" value="0.5" style="width:14rem"></div>
  <table class="payoff"><thead><tr><th>${cfg.labels.coop}</th><th>${cfg.labels.dev}</th><th>δ*</th></tr></thead>
  <tbody><tr><td data-c></td><td data-x></td><td data-t></td></tr></tbody></table><p class="verdict" data-v></p>`;
  const f=n=>Number.isFinite(n)?n.toFixed(2):'∞';
  function draw(){
    const c=cfg.cooperate(p,d), x=cfg.deviate(p,d), t=cfg.threshold(p);
    el.querySelector('[data-dv]').textContent=d.toFixed(2);
    el.querySelector('[data-c]').textContent=f(c); el.querySelector('[data-x]').textContent=f(x);
    el.querySelector('[data-t]').textContent=f(t);
    const ok=c>=x-1e-9, v=el.querySelector('[data-v]');
    v.textContent=ok?'Cooperation sustainable: deviating does not pay.':'Deviation pays: cooperation collapses.';
    v.style.color=ok?'var(--ok)':'var(--bad)';
  }
  el.querySelector('[data-d]').oninput=e=>{d=+e.target.value;draw();};
  draw();
  return {setPayoffs:q=>{p=Object.assign(p,q);draw();}};
}
