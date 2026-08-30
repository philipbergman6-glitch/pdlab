import { chromium } from "playwright-core";
const b = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto("http://localhost:4500/", { waitUntil: "networkidle" });
const bad = []; let last = "";
for (let i = 0; i < 90; i++) {
  await p.keyboard.press("Tab"); await p.waitForTimeout(900);
  const r = await p.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null;
    const cs = getComputedStyle(e); let op = 1, n = e; while (n && n !== document.body) { op *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
    const rc = e.getBoundingClientRect(); return { id: e.id || e.tagName + ":" + (e.textContent || "").trim().slice(0, 18), op: +op.toFixed(2), onscreen: rc.bottom > 0 && rc.top < innerHeight && rc.width > 0, vis: cs.visibility }; });
  if (!r) continue; if (r.id === last) continue; last = r.id;
  if (r.op < 0.85 || !r.onscreen || r.vis === "hidden") bad.push(r);
}
console.log("focus stops with a problem:", bad.length, bad.slice(0, 12));
await b.close();
