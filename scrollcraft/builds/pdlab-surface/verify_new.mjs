import { chromium } from "playwright-core";
const OUT = process.argv[2];
const b = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
for (const [w,h,theme] of [[1440,900,""],[390,844,"?theme=dark"]]) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const errs = [];
  p.on("console", m => { if (m.type() === "error" || m.type() === "warning") errs.push(m.type()+": "+m.text()); });
  p.on("pageerror", e => errs.push("pageerror: " + e.message));
  await p.goto("http://127.0.0.1:4511/app/index.html" + theme, { waitUntil: "networkidle" });
  for (let y = 0; y <= 1; y += 0.05) { await p.evaluate(f => scrollTo(0, f * (document.documentElement.scrollHeight - innerHeight)), y); await p.waitForTimeout(80); }
  const frame = await p.evaluate(() => document.querySelector(".frame").innerText.slice(0,80));
  // derivation: scroll horizon act to its end
  await p.evaluate(() => { const s = document.getElementById("bench-horizon"); scrollTo(0, s.offsetTop + 0.92*(s.offsetHeight - innerHeight)); });
  await p.waitForTimeout(1500);
  const pos = await p.evaluate(() => { const s = document.getElementById("bench-horizon"); return [scrollY, s.offsetTop, s.offsetHeight, s.getBoundingClientRect().top, s.style.getPropertyValue("--sc-p")].join(","); });
  console.log("horizon pos:", pos);
  const derive = await p.evaluate(() => document.getElementById("derive").innerText);
  await p.screenshot({ path: `${OUT}/${w}-derive.png` });
  // simplex mu
  await p.evaluate(() => document.getElementById("bench-population").scrollIntoView());
  await p.waitForTimeout(400);
  const basin0 = await p.evaluate(() => document.getElementById("sim-basin").innerText);
  await p.evaluate(() => { const s = document.getElementById("sim-mu"); s.value = "0.1"; s.dispatchEvent(new Event("input")); });
  await p.waitForTimeout(200);
  const basin1 = await p.evaluate(() => document.getElementById("sim-basin").innerText);
  await p.screenshot({ path: `${OUT}/${w}-simplex.png` });
  // noise chain
  await p.evaluate(() => { const s = document.getElementById("bench-noise"); scrollTo(0, s.offsetTop + s.offsetHeight*0.5); });
  await p.waitForTimeout(500);
  const chain = await p.evaluate(() => document.getElementById("chain-table").innerText + "\n" + document.getElementById("chain-note").innerText);
  await p.screenshot({ path: `${OUT}/${w}-chain.png` });
  await p.evaluate(() => { const s = document.getElementById("chain-strat"); s.value = "WSLS"; s.dispatchEvent(new Event("change")); });
  const chainW = await p.evaluate(() => document.getElementById("chain-note").innerText);
  // lattice async
  await p.evaluate(() => { const s = document.getElementById("bench-lattice"); scrollTo(0, s.offsetTop + s.offsetHeight*0.6); });
  await p.waitForTimeout(400);
  const t0 = Date.now();
  await p.evaluate(() => { const s = document.getElementById("lat-update"); s.value = "async"; s.dispatchEvent(new Event("change")); });
  const dt = Date.now() - t0;
  await p.waitForTimeout(600);
  const state = await p.evaluate(() => document.getElementById("ground").getAttribute("data-sc-verify-state") + " | " + document.getElementById("lat-py-async").innerText + " | " + document.getElementById("lat-rule").innerText.slice(0,60));
  await p.screenshot({ path: `${OUT}/${w}-async.png` });
  console.log(`== ${w}x${h}${theme}\nframe: ${frame}\nderive:\n${derive}\nbasin: ${basin0} -> ${basin1}\nchain:\n${chain}\nWSLS note: ${chainW}\nasync compute ms: ${dt}\nlattice: ${state}\nerrors: ${errs.length} ${errs.slice(0,6).join(" | ")}`);
  await p.close();
}
await b.close();
