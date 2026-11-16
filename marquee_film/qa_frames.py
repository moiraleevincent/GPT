#!/usr/bin/env python3
"""Browser smoke test and contact sheet of film frames from the real Canvas renderer."""
from pathlib import Path
import asyncio
from PIL import Image, ImageOps, ImageDraw
from playwright.async_api import async_playwright

BASE=Path(__file__).resolve().parent
OUT=BASE/"qa";OUT.mkdir(exist_ok=True)
TIMES=[4,14,23,32,44,58,71,85,98,122,136,148,163,175,190]
async def run():
    errors=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        page=await browser.new_page(viewport={"width":1200,"height":800},device_scale_factor=1)
        page.on("pageerror",lambda e:errors.append(str(e)))
        await page.goto((BASE/"index.html").as_uri())
        await page.wait_for_timeout(300)
        tiles=[]
        for sec in TIMES:
            await page.locator("#seek").evaluate("(el,t)=>{el.value=t;el.dispatchEvent(new Event('input',{bubbles:true}));}",sec)
            await page.wait_for_timeout(60)
            f=OUT/f"frame_{sec:03}.png"
            await page.locator("#screen").screenshot(path=str(f))
            shot=Image.open(f).convert("RGB").resize((440,248),Image.Resampling.LANCZOS)
            tiles.append((sec,shot))
        await browser.close()
        if errors:raise RuntimeError("Canvas page errors: "+" | ".join(errors))
        canvas=Image.new("RGB",(3*460,5*280),(18,17,24))
        draw=ImageDraw.Draw(canvas)
        for i,(sec,im) in enumerate(tiles):
            x=(i%3)*460+10;y=(i//3)*280+8
            canvas.paste(im,(x,y))
            draw.text((x+3,y+250),f"{sec//60:02}:{sec%60:02} / frame {i+1:02}",fill=(242,222,195))
        canvas.save(OUT/"review_contact_sheet.png",optimize=True)
        print("Successfully rendered",len(TIMES),"frames; contact sheet:",OUT/"review_contact_sheet.png",flush=True)
asyncio.run(run())
