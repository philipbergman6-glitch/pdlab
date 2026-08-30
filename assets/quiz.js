// Quiz component. Usage:
// <div class="quiz" data-quiz></div>
// <script>renderQuiz(el, [{stem, options:[..], answer:index, why}])</script>
// Options are shuffled. Feedback is immediate. Same word-count rule enforced by author.
function renderQuiz(el, questions){
  let score=0, answered=0;
  const summary=document.createElement('p');
  summary.className='fb';
  questions.forEach((q,i)=>{
    const box=document.createElement('div'); box.className='q';
    const stem=document.createElement('p'); stem.className='stem'; stem.innerHTML=(i+1)+'. '+q.stem; box.appendChild(stem);
    const fb=document.createElement('p'); fb.className='fb';
    const idx=q.options.map((_,k)=>k);
    for(let k=idx.length-1;k>0;k--){const j=Math.floor(Math.random()*(k+1));[idx[k],idx[j]]=[idx[j],idx[k]];}
    const btns=[];
    idx.forEach(k=>{
      const b=document.createElement('button'); b.innerHTML=q.options[k]; btns.push(b);
      b.onclick=()=>{
        if(box.dataset.done) return; box.dataset.done=1; answered++;
        if(k===q.answer){b.classList.add('ok');score++;fb.innerHTML='Correct. '+q.why;}
        else{b.classList.add('bad');btns[idx.indexOf(q.answer)].classList.add('ok');fb.innerHTML='Not quite. '+q.why;}
        if(answered===questions.length) summary.textContent=`Score: ${score}/${questions.length}. `+(score===questions.length?'Solid — move on.':'Re-read the sections for what you missed, then refresh and retry.');
      };
      box.appendChild(b);
    });
    box.appendChild(fb); el.appendChild(box);
  });
  el.appendChild(summary);
}
