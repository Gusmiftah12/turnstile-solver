from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from xvfbwrapper import Xvfb
from patchright.async_api import async_playwright
import asyncio
import requests  # Untuk melakukan request pada testing

app = FastAPI()

class TurnstileRequest(BaseModel):
    site: str = "https://d000d.com/e/b0pckrukog0h"  # Default site
    sitekey: str = "0x4AAAAAAALn0BYsCrtFUbm_"       # Default sitekey

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

# Bagian utama untuk menjalankan API
if __name__ == "__main__":
    import uvicorn
    from multiprocessing import Process
    import time

    def run_server():
        """Fungsi untuk menjalankan API."""
        uvicorn.run(app, host="127.0.0.1", port=8000)

    def run_tests():
        """Fungsi untuk mengetes API setelah server berjalan."""
        print("\n[INFO] Menjalankan health check...")
        try:
            response = requests.get("http://127.0.0.1:8000/")
            print("[TEST] Health Check:", response.json())
        except Exception as e:
            print("[ERROR] Health check gagal:", e)

        print("\n[INFO] Menjalankan test solve-turnstile...")
        try:
            response = requests.post(
                "http://127.0.0.1:8000/solve-turnstile",
                json={"site": "https://d000d.com/e/b0pckrukog0h", "sitekey": "0x4AAAAAAALn0BYsCrtFUbm_"}
            )
            print("[TEST] Solve Turnstile:", response.json())
        except Exception as e:
            print("[ERROR] Test solve-turnstile gagal:", e)

    # Jalankan server API di proses terpisah
    server_process = Process(target=run_server)
    server_process.start()

    # Beri waktu untuk server API berjalan
    time.sleep(2)

    # Jalankan testing
    run_tests()

    # Hentikan server setelah testing selesai
    server_process.terminate()
    server_process.join()
