import os
import time
import requests
import urllib.parse
from pathlib import Path

BING_URL = "https://www.bing.com"

class Config:
    bing_image_cookie = "1tnQzIApJCG3U15bf8nJgrdZgrK07Xk2Ml25zlVWSNXR0wtv4fhD_b-2Sh30F4E25b3jla-AjCherCTAzrKfeHWi7QmQ4HC804zhCl39FbVaOm2kghAqygX7J_is7VTlrB7PUrDH4CvVUu2xmA-6ktQzX6tVZs23HbrmvBv-SA0ZDdXoDeBwCrEBvZQV6LiYxn3fmUp2QAn-_FZ2pYq4qWxx6kZv075oBxZuXbOEy1j0"  # Replace with your Bing auth cookie
    temp_dir = "./temp"  # Temporary directory to save images

async def create_session(auth_cookie: str):
    session = requests.Session()
    session.headers.update({
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "referrer": "https://www.bing.com/images/create/",
        "origin": "https://www.bing.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "cookie": f"_U={auth_cookie}",
    })
    return session

async def get_images(session: requests.Session, prompt: str):
    print("Sending request...")
    url_encoded_prompt = urllib.parse.quote(prompt)
    url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=3&FORM=GENCRE"

    response = session.post(
        url,
        allow_redirects=False,  # Expecting a redirect
        timeout=200
    )
    
    if response.status_code == 200:
        print("Response headers:", response.headers)
        print("Response body (truncated):", response.text[:1000])
        raise Exception("Unexpected response: 200")


    if response.status_code == 302:
        redirect_url = response.headers["Location"].replace("&nfy=1", "")
        print("Redirected to", redirect_url)

        request_id = redirect_url.split("id=")[-1]
        polling_url = f"{BING_URL}/images/create/async/results/{request_id}?q={url_encoded_prompt}"
        
        print("Waiting for results...")
        start_wait = time.perf_counter()

        while True:
            if time.perf_counter() - start_wait > 300:
                raise TimeoutError("Timeout error")
            
            print(".", end="", flush=True)
            images_response = session.get(polling_url)
            if images_response.status_code != 200 or not images_response.text.strip():
                time.sleep(1)
                continue

            if "Pending" in images_response.text:
                raise ValueError("This prompt is flagged or blocked by Bing.")
            
            image_links = [
                src.split('"')[0] for src in images_response.text.split('src="')[1:]
            ]
            normal_image_links = list(set(link.split("?w=")[0] for link in image_links))

            bad_images = [
                "https://r.bing.com/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png",
                "https://r.bing.com/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg",
            ]

            return [link for link in normal_image_links if link not in bad_images]

    raise ValueError(f"Unexpected response: {response.status_code}")

async def save_images(session: requests.Session, links: list, output_dir: str):
    print("\nDownloading images...")
    os.makedirs(output_dir, exist_ok=True)

    for idx, link in enumerate(links):
        try:
            response = session.get(link, stream=True)
            output_path = os.path.join(output_dir, f"{idx}.jpeg")

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        except Exception as e:
            print(f"Failed to download image {link}: {e}")

async def generate_images_links(prompt: str):
    auth_cookie = Config.bing_image_cookie
    if not auth_cookie or not prompt:
        raise ValueError("Missing parameters")

    session = await create_session(auth_cookie)
    return await get_images(session, prompt)

async def generate_image_files(prompt: str):
    auth_cookie = Config.bing_image_cookie
    output_dir = os.path.join(Config.temp_dir, prompt)

    if not auth_cookie or not prompt:
        raise ValueError("Missing parameters")

    session = await create_session(auth_cookie)
    image_links = await get_images(session, prompt)
    save_images(session, image_links, output_dir)

    images = []
    for file in Path(output_dir).glob("*.jpeg"):
        with open(file, "rb") as f:
            images.append({
                "filename": file.name,
                "data": f.read().encode("base64"),
            })
    return images
