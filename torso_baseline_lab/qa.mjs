import { chromium } from 'playwright-core';
import fs from 'node:fs/promises';
const out='torso_baseline_lab/qa-output';
await fs.mkdir(out,{recursive:true});
const problems=[];
let browser;
try{
  browser=await chromium.launch({
    channel:'chrome',headless:true,
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-gpu-sandbox']
  });
  const page=await browser.newPage({viewport:{width:1130,height:900},deviceScaleFactor:1});
  page.on('pageerror',e=>problems.push('PAGE '+e.message));
  page.on('console',m=>{if(m.type()==='error')problems.push('CONSOLE '+m.text());});
  await page.goto('http://127.0.0.1:8000/torso_baseline_lab/',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>{
    const el=document.getElementById('status'),fatal=document.getElementById('fatal');
    return !!(el&&el.textContent.includes('CURRENT HIP'))||
      !!(fatal&&fatal.style.display==='block');
  },{timeout:45000});
  const fatal=await page.locator('#fatal').evaluate(el=>el.style.display==='block'?el.textContent:'');
  if(fatal)throw new Error('Viewer fatal: '+fatal);
  const initialMetrics=await page.locator('#metricRows').innerText();
  const labels=['Front','Side','Back','¾'],viewNames=['front','side','back','three'];
  for(let i=0;i<labels.length;i++){
    await page.getByRole('button',{name:labels[i],exact:true}).click();
    await page.waitForTimeout(400);
    await page.locator('#stage').screenshot({path:out+'/'+viewNames[i]+'.png'});
  }
  await page.getByRole('button',{name:'Front',exact:true}).click();
  await page.locator('#showRings').click();
  await page.locator('#showGhost').click();
  await page.locator('#range-waist').evaluate(el=>{el.value='120';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/delta-waist-and-measuring-rings.png'});
  const afterMetrics=await page.locator('#metricRows').innerText();
  const status=await page.locator('#status').innerText();
  await page.locator('#showGhost').click();
  await page.locator('#showRings').click();
  await page.locator('#from2D').click();
  await page.locator('#range-hip').evaluate(el=>el.dispatchEvent(new Event('input',{bubbles:true})));
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/approved-2D-ratios-front.png'});
  const bRatioStatus=await page.locator('#status').innerText();
  const bRatioMetrics=await page.locator('#metricRows').innerText();
  await page.getByRole('button',{name:'Side',exact:true}).click();
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/approved-2D-ratios-side.png'});
  await page.locator('#range-hem').evaluate(el=>{el.value='100';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/hem-experiment-side.png'});
  await page.getByRole('button',{name:'Front',exact:true}).click();
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/hem-experiment-front.png'});
  // Hem deformation is a vertical contour experiment: it should not
  // change any measured station width above the bottom 1.66 body level.
  // Front-view width ratio should match the approved 2D hip/waist value
  // within a small interpolation/rounding tolerance.
  const m=bRatioStatus.match(/WIDTH ([\d.]+):1/);
  if(!m||Math.abs(Number(m[1])-1.84)>.065)problems.push('2D ratio preset failed: '+bRatioStatus);
  if(!bRatioMetrics.includes('Waist'))problems.push('Preset lost measurement table');
  if(initialMetrics===afterMetrics)problems.push('Numeric deltas did not respond to slider');
  if(!status.includes('CURRENT HIP'))problems.push('Missing model status');
  // Structural-envelope test: the envelope stays fixed while skin shrinks.
  await page.locator('#toBaseline').click();
  await page.locator('#showBones').click();
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/skeleton-overlay-front.png'});
  const envelopeBaseline=await page.locator('#boneStatus').innerText();
  if(!envelopeBaseline.includes('No intersection'))problems.push('Bone envelope unexpectedly intersects baseline: '+envelopeBaseline);
  await page.getByRole('button',{name:'Side',exact:true}).click();
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/skeleton-overlay-side.png'});
  await page.getByRole('button',{name:'Front',exact:true}).click();
  await page.locator('#range-waist').evaluate(el=>{el.value='65';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await page.waitForTimeout(300);
  const envelopeNarrowWaist=await page.locator('#boneStatus').innerText();
  await page.locator('#stage').screenshot({path:out+'/skeleton-intersection-waist65.png'});
  if(!envelopeNarrowWaist.includes('PROXY INTERSECTION'))problems.push('Bone test failed to flag extreme waist deformation: '+envelopeNarrowWaist);
  const report={status,initialMetrics,afterMetrics,bRatioStatus,bRatioMetrics,envelopeBaseline,envelopeNarrowWaist,problems};
  await fs.writeFile(out+'/qa.json',JSON.stringify(report,null,2)+'\n');
  console.log('TORSO_QA_REPORT '+JSON.stringify(report));
  if(problems.length)process.exitCode=1;
}catch(e){console.error('TORSO_QA_FAILED',e.message);process.exitCode=1;}
finally{if(browser)await browser.close();}
