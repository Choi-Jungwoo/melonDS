"""检查 docs 的本地链接、入口可达性及源码路由；仅使用标准库。"""

from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit


def links(text: str) -> list[str]:
    # ponytail: 仅支持本目录使用的行内链接；引入引用式链接时再扩展解析。
    text = re.sub(r"^```[^\n]*\n.*?^```[ \t]*$", "", text, flags=re.M | re.S)
    return re.findall(r"\[[^\]\n]+\]\(([^\s)]+)\)", text)


def anchors(text: str) -> set[str]:
    result = set()
    for heading in re.findall(r"^#{1,6} (.+)$", text, flags=re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        unique = slug
        suffix = 0
        while unique in result:
            suffix += 1
            unique = f"{slug}-{suffix}"
        result.add(unique)
    return result


def check(root: Path, sources: list[Path]) -> list[str]:
    pages = {
        path.resolve(): path.read_text(encoding="utf-8")
        for path in (root / "docs").rglob("*.md")
    }
    entry = root / "docs/README.md"
    index = root / "docs/source-map.md"
    errors = []
    if entry not in pages or index not in pages:
        return ["缺少 docs/README.md 或 docs/source-map.md"]

    graph = {path: set() for path in pages}
    indexed = set()
    for page, content in pages.items():
        for link in links(content):
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (page.parent / unquote(url.path)).resolve() if url.path else page
            if not target.exists():
                errors.append(f"{page.relative_to(root)}: 无效链接 {link}")
                continue
            if target in pages:
                graph[page].add(target)
                if url.fragment and unquote(url.fragment) not in anchors(pages[target]):
                    errors.append(f"{page.relative_to(root)}: 无效锚点 {link}")
            if page == index:
                indexed.add(target)

    visited = set()
    pending = [entry]
    while pending:
        page = pending.pop()
        if page not in visited:
            visited.add(page)
            pending.extend(graph[page] - visited)
    for page in sorted(pages.keys() - visited):
        errors.append(f"总路由不可达: {page.relative_to(root)}")

    directories = {path for path in indexed if path.is_dir()}
    for source in sources:
        path = root / source
        if path not in indexed and not directories.intersection(path.parents):
            errors.append(f"源码未归属: {source}")
    return errors


def self_check() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory).resolve()
        (root / "docs").mkdir()
        (root / "src").mkdir()
        (root / "src/device.cpp").write_text("// fixture\n", encoding="utf-8")
        entry = root / "docs/README.md"
        entry.write_text("# 路由\n[索引](source-map.md)\n", encoding="utf-8")
        index = root / "docs/source-map.md"
        index.write_text("# 源码\n[设备](../src/device.cpp)\n", encoding="utf-8")
        sources = [Path("src/device.cpp")]
        assert check(root, sources) == []
        entry.write_text("[索引](source-map.md#不存在)\n[坏链](missing.md)\n", encoding="utf-8")
        errors = check(root, sources)
        assert any("无效锚点" in error for error in errors)
        assert any("无效链接" in error for error in errors)
        entry.write_text("# 无出口\n", encoding="utf-8")
        index.write_text("# 空索引\n", encoding="utf-8")
        errors = check(root, sources)
        assert any("总路由不可达" in error for error in errors)
        assert any("源码未归属" in error for error in errors)


if __name__ == "__main__":
    self_check()
    root = Path(__file__).resolve().parents[1]
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         "src", "freebios", "melonDLDI", "tools", "cmake", ".github", "res"],
        cwd=root,
    ).decode("utf-8")
    sources = sorted({Path(path) for path in output.split("\0") if path})
    errors = check(root, sources)
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"通过：{len(list((root / 'docs').rglob('*.md')))} 篇文档；"
        f"{len(sources)} 个源码/资源文件均有路由；链接、锚点和可达性正常。"
    )
