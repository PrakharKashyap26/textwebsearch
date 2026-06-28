import sys
import shutil
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
from browser.renderer import HTMLRenderer, PageRenderer, BLOCK_TAGS
from utils.http import get_http_headers

class NavigationController:
    """Manages browsing state, page retrieval, and interactive navigation loop."""

    def __init__(self):
        self.history_stack: List[str] = []
        self.forward_stack: List[str] = []
        self.current_url: str = None
        self.current_links: List[Dict[str, str]] = [] # list of {"text": str, "url": str}
        self.current_rendered_text: str = ""
        self.renderer = PageRenderer()

    def is_js_heavy_html(self, html_text: str) -> bool:
        """Inspect HTML heuristics to detect if a website is client-side JS rendered."""
        if not html_text:
            return False
        
        try:
            soup = BeautifulSoup(html_text, "html.parser")
            
            # 1. SPA framework markers / hydration scripts
            if soup.find(id="__NEXT_DATA__") or soup.find(id="__nuxt") or soup.find(id="___gatsby"):
                return True
            
            # 2. Empty React / Vue / Next root mount containers
            for root_id in ("root", "app", "mount", "react-root", "__next"):
                root_div = soup.find(id=root_id)
                if root_div and len(root_div.get_text(strip=True)) < 50:
                    return True
            
            # 3. Empty body element with scripts
            body = soup.find("body")
            if body:
                body_text = body.get_text(strip=True)
                if len(body_text) < 150 and len(soup.find_all("script")) > 3:
                    return True
            
            # 4. High ratio of script content to total length with low text count
            scripts = soup.find_all("script")
            total_len = len(html_text)
            if scripts and total_len > 0:
                script_char_count = sum(len(str(s)) for s in scripts)
                if script_char_count / total_len > 0.6 and len(soup.get_text(strip=True)) < 500:
                    return True
        except Exception:
            pass

        return False

    def fetch_page_html(self, url: str) -> str:
        """Retrieve HTML source from URL with JS-heavy detection and Playwright fallback."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # 1. Initial lightweight HTTP GET request
        raw_html = ""
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            raw_html = response.text
        except Exception as e:
            print(f"[WARNING] Lightweight requests fetch failed: {e}")

        # 2. Check if JavaScript hydration/rendering is required
        if raw_html and not self.is_js_heavy_html(raw_html):
            return raw_html

        # 3. Launch Playwright Chromium fallback for JS-heavy sites
        print("[INFO] Website appears to be JavaScript-heavy. Launching Playwright Chromium fallback...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                # Set dynamic page wait
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(3000) # wait for React/Vue client-side rendering
                html = page.content()
                browser.close()
                print("[INFO] Content extracted successfully using Playwright Renderer")
                return html
        except Exception as pe:
            print(f"[WARNING] Playwright fallback failed or not installed: {pe}")
            return raw_html

    def load_page(self, url: str, history_manager, title: str = None) -> bool:
        """Fetch content, determine extraction mode, and run rendering."""
        self.current_url = url
        
        # 1. Fetch content
        html = self.fetch_page_html(url)
        if not html:
            print(f"[ERROR] Failed to retrieve content from {url}.")
            return False

        # 2. Extract or infer title and log history
        if not title:
            try:
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string.strip() if soup.title else url
            except Exception:
                title = url
        history_manager.add_entry(url=url, title=title)

        # 3. Run Renderer (Trafilatura article extraction vs standard BeautifulSoup)
        soup = BeautifulSoup(html, "html.parser")
        rendered_text = ""
        used_trafilatura = False

        is_article = any(x in url.lower() for x in ["wikipedia.org", "wiki", "blog", "news", "docs", "documentation"])
        
        if is_article and not self.is_js_heavy_html(html):
            try:
                import trafilatura
                xml_content = trafilatura.extract(html, output_format="xml")
                if xml_content:
                    xml_soup = BeautifulSoup(xml_content, "html.parser")
                    width = 80
                    try:
                        width = shutil.get_terminal_size((80, 20)).columns
                    except Exception:
                        pass
                    renderer = HTMLRenderer(url, width=width)
                    rendered_text = renderer.render(xml_soup)
                    self.current_links = renderer.links
                    used_trafilatura = True
                    print("[INFO] Content extracted using Trafilatura Fast Renderer")
            except Exception:
                pass

        if not used_trafilatura:
            width = 80
            try:
                width = shutil.get_terminal_size((80, 20)).columns
            except Exception:
                pass
            renderer = HTMLRenderer(url, width=width)
            rendered_text = renderer.render(soup)
            self.current_links = renderer.links
            print("[INFO] Content extracted using BeautifulSoup Fast Renderer")

        self.current_rendered_text = rendered_text
        self.redisplay_current_page()
        return True

    def redisplay_current_page(self):
        """Clean screen and display current page rendering."""
        width = 80
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            pass
        border = "=" * width
        print(f"\n{border}\n")
        
        text_to_print = self.current_rendered_text if self.current_rendered_text else "No content."
        try:
            print(text_to_print)
        except UnicodeEncodeError:
            enc = sys.stdout.encoding or 'utf-8'
            print(text_to_print.encode(enc, errors='replace').decode(enc))

        print(f"\n{border}")

    def enter_browser_loop(self, initial_url: str, history_manager):
        """Start interactive page navigation sub-loop."""
        current_url = initial_url
        success = self.load_page(current_url, history_manager)
        if not success:
            input("\nPress Enter to return to results...")
            return

        while True:
            print("\n---")
            print("## COMMANDS")
            print("[number] Open Link")
            print("b        Back")
            print("f        Forward")
            print("h        History")
            print("s        Search (Exit Browser)")
            print("q        Quit")
            print()

            try:
                cmd = input("Browser > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                sys.exit(0)

            if not cmd:
                continue

            cmd_lower = cmd.lower()

            if cmd_lower == "q":
                print("Goodbye!")
                sys.exit(0)
            elif cmd_lower == "s":
                break
            elif cmd_lower == "b":
                self.go_back(history_manager)
            elif cmd_lower == "f":
                self.go_forward(history_manager)
            elif cmd_lower == "h":
                print("\n--- History Log ---")
                history_entries = history_manager.get_history()
                for entry in history_entries[-15:]:
                    ts = entry.get("timestamp", "")
                    time_str = ts.split("T")[-1][:5] if "T" in ts else ts[:10]
                    query = entry.get("query")
                    url = entry.get("url")
                    title = entry.get("title") or "No Title"
                    if query:
                        print(f"[{time_str}] Search: '{query}'")
                    else:
                        print(f"[{time_str}] Visit: {title} ({url})")
                print("-------------------")
                input("\nPress Enter to return to page...")
                self.redisplay_current_page()
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(self.current_links):
                    next_link = self.current_links[idx]
                    next_url = next_link["url"]
                    next_title = next_link["text"]

                    if self.current_url:
                        self.history_stack.append(self.current_url)
                        self.forward_stack.clear()

                    self.load_page(next_url, history_manager, title=next_title)
                else:
                    print(f"Error: Link number must be between 1 and {len(self.current_links)}.")
                    input("\nPress Enter to continue...")
                    self.redisplay_current_page()
            else:
                print(f"Unknown command: '{cmd}'. Enter a link number, 'b', 'f', 'h', 's', or 'q'.")
                input("\nPress Enter to continue...")
                self.redisplay_current_page()

    def go_back(self, history_manager) -> bool:
        """Pop and navigate to previous URL in back stack."""
        if not self.history_stack:
            print("[WARNING] No back history.")
            input("\nPress Enter to continue...")
            self.redisplay_current_page()
            return False

        if self.current_url:
            self.forward_stack.append(self.current_url)

        prev_url = self.history_stack.pop()
        return self.load_page(prev_url, history_manager)

    def go_forward(self, history_manager) -> bool:
        """Pop and navigate to next URL in forward stack."""
        if not self.forward_stack:
            print("[WARNING] No forward history.")
            input("\nPress Enter to continue...")
            self.redisplay_current_page()
            return False

        if self.current_url:
            self.history_stack.append(self.current_url)

        next_url = self.forward_stack.pop()
        return self.load_page(next_url, history_manager)

    def open_url(self, url: str) -> bool:
        """Legacy open_url wrapper used for backward compatibility."""
        # This resolves to loading page but doesn't enter the loop.
        # We will map it to standard load_page without interactive loop
        class DummyHistoryManager:
            def add_entry(self, **kwargs):
                pass
        return self.load_page(url, DummyHistoryManager())

    def extract_links(self, html: str, base_url: str) -> List[Tuple[str, str]]:
        """Legacy extract_links method."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            text = tag.get_text(strip=True) or "[Link]"
            absolute_url = urljoin(base_url, href)
            if urlparse(absolute_url).scheme in ("http", "https"):
                links.append((text, absolute_url))
        return links
