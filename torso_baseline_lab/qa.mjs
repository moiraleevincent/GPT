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
  await page.locator('#range-waist').fill('120');
  await page.waitForTimeout(300);
  await page.locator('#stage').screenshot({path:out+'/delta-waist-and-measuring-rings.png'});
  const afterMetrics=await page.locator('#metricRows').innerText();
  const status=await page.locator('#status').innerText();
  if(initialMetrics===afterMetrics)problems.push('Numeric deltas did not respond to slider');
  if(!status.includes('CURRENT HIP'))problems.push('Missing model status');
  const report={status,initialMetrics,afterMetrics,problems};
  await fs.writeFile(out+'/qa.json',JSON.stringify(report,null,2)+'\n');
  console.log('TORSO_QA_REPORT '+JSON.stringify(report));
  if(problems.length)process.exitCode=1;
}catch(e){console.error('TORSO_QA_FAILED',e.message);process.exitCode=1;}
finally{if(browser)await browser.close();}
