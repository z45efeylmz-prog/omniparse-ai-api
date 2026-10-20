import time
from typing import Optional, Literal
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field
import httpx
import trafilatura
from cachetools import TTLCache

# In-memory TTL Cache: 2000 URLs cached for 1 hour for ultra-low latency (<2ms)
cache = TTLCache(maxsize=2000, ttl=3600)

app = FastAPI(
    title="OmniParse AI - Ultra Fast Web-to-Markdown & Reader API",
    description="Blazing fast web content extraction optimized for LLMs, RAG pipelines, and AI agents. Strips clutter, ads, navigation, and returns clean Markdown in milliseconds.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent Async HTTP Client with HTTP/2 & Connection Pooling
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

client = httpx.AsyncClient(
    http2=True,
    follow_redirects=True,
    timeout=httpx.Timeout(10.0, connect=4.0),
    headers={
        "User-Agent": BROWSER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
    },
    limits=httpx.Limits(max_keepalive_connections=50, max_connections=200)
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

class ExtractRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target webpage URL to extract")
    format: Literal["markdown", "text", "xml"] = Field(default="markdown", description="Output content format")
    include_images: bool = Field(default=True, description="Include Markdown image tags")
    include_links: bool = Field(default=True, description="Preserve hyperlinks in output")
    favor_recall: bool = Field(default=False, description="Extract more text even if it might include non-core sections")

class ExtractResponse(BaseModel):
    success: bool
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    site_name: Optional[str] = None
    content: str
    word_count: int
    estimated_reading_time_min: float
    cached: bool
    latency_ms: float

def parse_html_content(html: str, url: str, output_format: str, include_images: bool, include_links: bool, favor_recall: bool):
    # Trafilatura C-optimized extraction
    extracted = trafilatura.extract(
        html,
        url=url,
        output_format="xml" if output_format == "xml" else ("txt" if output_format == "text" else "markdown"),
        include_images=include_images,
        include_links=include_links,
        favor_recall=favor_recall,
        include_tables=True,
        include_formatting=True
    )
    
    metadata = trafilatura.extract_metadata(html, default_url=url)
    
    title = metadata.title if metadata else None
    author = metadata.author if metadata else None
    date = metadata.date if metadata else None
    site_name = metadata.sitename if metadata else (urlparse(url).netloc if url else None)

    content_str = extracted or ""
    words = len(content_str.split())
    reading_time = round(words / 200, 1)  # average 200 wpm
    
    return {
        "title": title,
        "author": author,
        "date": date,
        "site_name": site_name,
        "content": content_str,
        "word_count": words,
        "estimated_reading_time_min": reading_time
    }

async def fetch_and_extract(url: str, format: str, include_images: bool, include_links: bool, favor_recall: bool):
    cache_key = f"{url}:{format}:{include_images}:{include_links}:{favor_recall}"
    start_time = time.perf_counter()

    if cache_key in cache:
        result = cache[cache_key].copy()
        result["cached"] = True
        result["latency_ms"] = round((time.perf_counter() - start_time) * 1000, 2)
        return result

    try:
        resp = await client.get(url)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Target webpage returned status {e.response.status_code}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach target webpage: {str(e)}")

    parsed = parse_html_content(resp.text, url, format, include_images, include_links, favor_recall)
    
    latency = round((time.perf_counter() - start_time) * 1000, 2)
    response_data = {
        "success": True,
        "url": url,
        "cached": False,
        "latency_ms": latency,
        **parsed
    }

    cache[cache_key] = response_data
    return response_data

@app.get("/", tags=["Info"])
async def root():
    return {
        "api": "OmniParse AI Web-to-Markdown API",
        "status": "online",
        "docs_url": "/docs",
        "description": "Ultra low-latency article and webpage extractor for AI LLMs & RAG applications."
    }

@app.get("/api/v1/extract", response_model=ExtractResponse, tags=["Extract"])
async def extract_get(
    url: str = Query(..., description="Target webpage URL"),
    format: Literal["markdown", "text", "xml"] = Query("markdown"),
    include_images: bool = Query(True),
    include_links: bool = Query(True),
    favor_recall: bool = Query(False)
):
    return await fetch_and_extract(url, format, include_images, include_links, favor_recall)

@app.post("/api/v1/extract", response_model=ExtractResponse, tags=["Extract"])
async def extract_post(req: ExtractRequest):
    return await fetch_and_extract(
        str(req.url), req.format, req.include_images, req.include_links, req.favor_recall
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
