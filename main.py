from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from xvfbwrapper import Xvfb
from patchright.async_api import async_playwright
import asyncio

app = FastAPI()

class TurnstileRequest(BaseModel):
    site: str
    sitekey: str

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Turnstile Solver API is running"}

async def make_payload(site, key):
    return {
        "url": site,
        "payload": f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{site}</title>
                <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" async defer></script>
            </head>
            <body>
                <div class="cf-turnstile" id="result" data-sitekey="{key}"></div>
            </body>
            </html>
        """
    }

async def solver(site, sitekey):
    vdisplay = Xvfb(width=1, height=1)
    vdisplay.start()
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./custom/",
            channel="chromium",
            headless=False,
            no_viewport=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = await browser.new_page()
        payload = await make_payload(site, sitekey)
        await page.route(payload['url'], lambda route: route.fulfill(body=payload['payload'], status=200))
        await page.goto(payload['url'])

        for i in range(10):
            attrib = await page.evaluate("window.document.getElementById('result').innerHTML")
            if 'value' in attrib and '""' not in attrib:
                value = await page.evaluate("window.document.querySelector('[name=\"cf-turnstile-response\"]').value")
                await browser.close()
                vdisplay.stop()
                return {"token": value, "status": "WORKED"}
            await asyncio.sleep(0.3)
        await browser.close()
        vdisplay.stop()
        return {"token": None, "status": "ERR"}

@app.post("/solve-turnstile")
async def solve_turnstile(request: TurnstileRequest):
    try:
        result = await solver(request.site, request.sitekey)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
