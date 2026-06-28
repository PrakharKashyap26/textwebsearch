import re
import textwrap
import shutil
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag

BLOCK_TAGS = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
    "blockquote", "pre", "table", "tr", "hr", "br", "section", "article",
    "aside", "header", "footer", "main", "list", "item", "row", "cell", "head",
    "doc", "body", "html", "xml", "document"
}

class HTMLRenderer:
    """Recursively formats HTML DOM into clean, terminal-width, markdown-like text."""

    def __init__(self, base_url: str, width: int = 80):
        self.base_url = base_url
        self.width = width
        self.links = []       # list of dicts: {"text": str, "url": str}
        self.output_lines = []

    def get_inline_text(self, node_or_nodes) -> str:
        parts = []
        nodes = node_or_nodes if isinstance(node_or_nodes, (list, tuple)) else getattr(node_or_nodes, "children", [])
        for child in nodes:
            if isinstance(child, str):
                parts.append(child)
            elif isinstance(child, Tag):
                if child.name in ("a", "ref"):
                    link_text = self.get_inline_text(child).strip()
                    href = child.get("href") or child.get("target")
                    if href:
                        absolute_url = urljoin(self.base_url, href)
                        parsed = urlparse(absolute_url)
                        if parsed.scheme in ("http", "https"):
                            num = None
                            for i, item in enumerate(self.links, 1):
                                if item["url"] == absolute_url:
                                    num = i
                                    if not item["text"] and link_text:
                                        item["text"] = link_text
                                    break
                            if num is None:
                                self.links.append({"text": link_text or "Link", "url": absolute_url})
                                num = len(self.links)
                            parts.append(f" {link_text} [{num}] ")
                        else:
                            parts.append(f" {link_text} ")
                    else:
                        parts.append(f" {link_text} ")
                elif child.name in ("strong", "b", "em", "i", "code", "span"):
                    inline_fmt = self.get_inline_text(child).strip()
                    if child.name in ("strong", "b"):
                        parts.append(f" {inline_fmt} ")
                    elif child.name in ("em", "i"):
                        parts.append(f" {inline_fmt} ")
                    elif child.name == "code":
                        parts.append(f" `{inline_fmt}` ")
                    else:
                        parts.append(f" {inline_fmt} ")
                elif child.name == "img":
                    alt = child.get("alt", "")
                    if alt:
                        parts.append(f" [Image: {alt}] ")
                    else:
                        parts.append(" [Image] ")
                elif child.name not in BLOCK_TAGS:
                    parts.append(self.get_inline_text(child))
        
        text = "".join(parts)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def process_node(self, node):
        if not isinstance(node, Tag):
            return

        if node.name in ("h1", "h2", "h3", "h4", "h5", "h6") or node.name == "head":
            text = self.get_inline_text(node)
            if text:
                level = 2
                if node.name.startswith("h") and len(node.name) == 2 and node.name[1].isdigit():
                    level = int(node.name[1])
                elif node.get("rend"):
                    rend = node.get("rend")
                    if rend.startswith("h") and len(rend) == 2 and rend[1].isdigit():
                        level = int(rend[1])
                prefix = "#" * level + " "
                wrapped = textwrap.fill(text, width=self.width, initial_indent=prefix, subsequent_indent=" " * len(prefix))
                self.output_lines.append("")
                self.output_lines.append(wrapped)
                self.output_lines.append("")
        elif node.name == "p":
            text = self.get_inline_text(node)
            if text:
                wrapped = textwrap.fill(text, width=self.width)
                self.output_lines.append(wrapped)
                self.output_lines.append("")
        elif node.name == "blockquote":
            text = self.get_inline_text(node)
            if text:
                wrapped = textwrap.fill(text, width=self.width - 4)
                quoted = "\n".join("> " + line for line in wrapped.splitlines())
                self.output_lines.append("")
                self.output_lines.append(quoted)
                self.output_lines.append("")
        elif node.name == "pre":
            code_text = node.get_text()
            self.output_lines.append("")
            self.output_lines.append("-" * self.width)
            for line in code_text.splitlines():
                if len(line) > self.width - 4:
                    self.output_lines.append("  " + line[:self.width - 7] + "...")
                else:
                    self.output_lines.append("  " + line)
            self.output_lines.append("-" * self.width)
            self.output_lines.append("")
        elif node.name in ("ul", "ol", "list"):
            self.output_lines.append("")
            self.process_list(node)
            self.output_lines.append("")
        elif node.name == "table":
            self.output_lines.append("")
            self.process_table(node)
            self.output_lines.append("")
        elif node.name == "hr":
            self.output_lines.append("-" * self.width)
            self.output_lines.append("")
        elif node.name == "br":
            self.output_lines.append("")
        else:
            self.process_container(node)

    def process_list(self, list_node):
        is_ordered = (list_node.name == "ol")
        counter = 1
        for child in list_node.children:
            if isinstance(child, Tag) and child.name in ("li", "item"):
                text = self.get_inline_text(child)
                if not text:
                    continue
                prefix = f"{counter}. " if is_ordered else "• "
                indent = " " * len(prefix)
                wrapped = textwrap.fill(text, width=self.width - len(prefix), initial_indent="", subsequent_indent=indent)
                self.output_lines.append(prefix + wrapped)
                counter += 1

    def process_table(self, table_node):
        rows = []
        for tr in table_node.find_all(["tr", "row"]):
            row = []
            for cell in tr.find_all(["td", "th", "cell"]):
                row.append(self.get_inline_text(cell))
            if row:
                rows.append(row)
        
        if not rows:
            return

        num_cols = max(len(row) for row in rows)
        for row in rows:
            while len(row) < num_cols:
                row.append("")

        col_widths = [0] * num_cols
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(val))

        total_border_width = num_cols + 1 + (num_cols * 2)
        total_width = sum(col_widths) + total_border_width
        
        if total_width > self.width:
            max_col_width = max(5, (self.width - total_border_width) // num_cols)
            col_widths = [max_col_width] * num_cols

        row_border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
        
        self.output_lines.append(row_border)
        for row in rows:
            wrapped_cells = []
            for cell_text, w in zip(row, col_widths):
                wrapped_cells.append(textwrap.wrap(cell_text, width=w))
            
            max_lines = max((len(lines) for lines in wrapped_cells), default=1)
            for lines in wrapped_cells:
                while len(lines) < max_lines:
                    lines.append("")
            
            for line_idx in range(max_lines):
                line_parts = []
                for col_idx in range(num_cols):
                    val = wrapped_cells[col_idx][line_idx]
                    padded = val.ljust(col_widths[col_idx])
                    line_parts.append(padded)
                self.output_lines.append("| " + " | ".join(line_parts) + " |")
            self.output_lines.append(row_border)

    def process_container(self, node):
        inline_run = []
        for child in node.children:
            if isinstance(child, str):
                if child.strip():
                    inline_run.append(child)
            elif isinstance(child, Tag):
                if child.name not in BLOCK_TAGS:
                    inline_run.append(child)
                else:
                    if inline_run:
                        text = self.get_inline_text(inline_run)
                        if text:
                            wrapped = textwrap.fill(text, width=self.width)
                            self.output_lines.append(wrapped)
                            self.output_lines.append("")
                        inline_run = []
                    self.process_node(child)
        if inline_run:
            text = self.get_inline_text(inline_run)
            if text:
                wrapped = textwrap.fill(text, width=self.width)
                self.output_lines.append(wrapped)
                self.output_lines.append("")

    def render(self, soup) -> str:
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            tag.decompose()
        
        self.process_node(soup)
        
        # Append numbered links section at the bottom
        if self.links:
            self.output_lines.append("")
            self.output_lines.append("## Links")
            self.output_lines.append("")
            for idx, item in enumerate(self.links, 1):
                self.output_lines.append(f"[{idx}] {item['text']} ({item['url']})")
        
        raw_text = "\n".join(self.output_lines)
        # Compress excessive blank lines (more than 2 consecutive blank lines)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', raw_text)
        return cleaned_text.strip()


class PageRenderer:
    """Wrapper class preserving legacy interface while driving HTMLRenderer."""

    def clean_html(self, html_text: str) -> str:
        soup = BeautifulSoup(html_text, "html.parser")
        width = 80
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            pass
        renderer = HTMLRenderer("", width=width)
        return renderer.render(soup)

    def render_page(self, text: str, max_chars: int = 10000) -> str:
        preview = text[:max_chars].rstrip()
        width = 80
        try:
            width = shutil.get_terminal_size((80, 20)).columns
        except Exception:
            pass
        border = "=" * width
        output = f"\n{border}\n\n{preview}\n"
        if len(text) > max_chars:
            output += f"\n...content truncated to {max_chars} characters...\n"
        output += f"\n{border}"
        return output
