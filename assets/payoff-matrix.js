// Payoff-matrix editor component for the 2x2 symmetric PD.
// Usage: renderPayoffEditor(el, {T:5,R:3,P:1,S:0})
function pdChecks(v){
  const {T,R,P,S}=v;
  return [
    {label:'T &gt; R &gt; P &gt; S (ordering)', ok:T>R&&R>P&&P>S},
    {label:'2R &gt; T + S (mutual cooperation beats alternating exploitation)', ok:2*R>T+S},
    {label:'D strictly dominates C for the row player (T &gt; R and P &gt; S)', ok:T>R&&P>S},
    {label:'(D,D) is a Nash equilibrium (P ≥ S)', ok:P>=S},
    {label:'(C,C) Pareto-dominates (D,D) (R &gt; P)', ok:R>P},
  ];
}
function renderPayoffEditor(el, init){
  const v=Object.assign({T:5,R:3,P:1,S:0},init);
  el.innerHTML=`
  <div class="editor">
    <label>T (temptation: I defect, you cooperate)</label><input data-k="T" type="number" step="1" value="${v.T}">
    <label>R (reward: both cooperate)</label><input data-k="R" type="number" step="1" value="${v.R}">
    <label>P (punishment: both defect)</label><input data-k="P" type="number" step="1" value="${v.P}">
    <label>S (sucker: I cooperate, you defect)</label><input data-k="S" type="number" step="1" value="${v.S}">
  </div>
  <table class="payoff"><thead><tr><th></th><th>Col: C</th><th>Col: D</th></tr></thead>
  <tbody>
    <tr><th>Row: C</th><td data-cell="CC"></td><td data-cell="CD"></td></tr>
    <tr><th>Row: D</th><td data-cell="DC"></td><td data-cell="DD"></td></tr>
  </tbody></table>
  <ul class="check"></ul><p class="verdict"></p>`;
  const cells=el.querySelectorAll('[data-cell]'), list=el.querySelector('.check'), verdict=el.querySelector('.verdict');
  function draw(){
    const {T,R,P,S}=v;
    const m={CC:[R,R],CD:[S,T],DC:[T,S],DD:[P,P]};
    // best responses: row's best in each column, col's best in each row
    const rowBest={C: R>=T?'CC':'DC', D: S>=P?'CD':'DD'}; if(R===T) rowBest.C='both'; if(S===P) rowBest.D='both';
    const colBest={C: R>=T?'CC':'CD', D: S>=P?'DC':'DD'}; if(R===T) colBest.C='both'; if(S===P) colBest.D='both';
    cells.forEach(c=>{const k=c.dataset.cell;const [a,b]=m[k];
      const rb = rowBest[k[1]]===k||rowBest[k[1]]==='both';
      const cb = colBest[k[0]]===k||colBest[k[0]]==='both';
      c.innerHTML=`<span class="p1">${rb?'<u>'+a+'</u>':a}</span>, <span class="p2">${cb?'<u>'+b+'</u>':b}</span>`;
      c.classList.toggle('hl', rb&&cb);
    });
    const ch=pdChecks(v);
    list.innerHTML=ch.map(c=>`<li class="${c.ok?'ok':'bad'}">${c.label}</li>`).join('');
    const isPD=ch[0].ok&&ch[1].ok;
    verdict.textContent=isPD?'This is a Prisoner\'s Dilemma.':'Not a Prisoner\'s Dilemma — see which condition fails.';
    verdict.style.color=isPD?'var(--ok)':'var(--bad)';
    el.dispatchEvent(new CustomEvent('pdchange',{detail:{...v,isPD,checks:ch}}));
  }
  el.querySelectorAll('input').forEach(i=>i.oninput=()=>{const n=Number(i.value); if(!Number.isFinite(n)){return;} v[i.dataset.k]=n; draw();});
  draw();
  return {get:()=>({...v})};
}
