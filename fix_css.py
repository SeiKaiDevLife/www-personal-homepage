import codecs
import re

with codecs.open('index.css', 'r', 'utf-8') as f:
    content = f.read()

# Replace .hero-logo
content = re.sub(
    r'\.hero-logo\s*\{.*?\z-index:\s*1;\s*\}',
    '.hero-logo {\n    height: 180px;\n    object-fit: contain;\n    margin-bottom: 20px;\n    filter: drop-shadow(0 10px 30px rgba(0,0,0,0.9));\n    animation: fadeInDown 0.8s ease-out;\n    z-index: 1;\n}',
    content,
    flags=re.DOTALL
)

# Replace .hero-subtitle
content = re.sub(
    r'\.hero-subtitle\s*\{.*?text-shadow:\s*0\s*4px\s*10px\s*rgba\(0,0,0,0\.8\);\s*\}',
    '.hero-subtitle {\n    font-size: 11px;\n    letter-spacing: 8px;\n    color: #eee;\n    text-transform: uppercase;\n    font-weight: 300;\n    text-shadow: 0 4px 10px rgba(0,0,0,0.8);\n}',
    content,
    flags=re.DOTALL
)

# Replace .top-header and .top-header.scrolled
content = re.sub(
    r'/\*\s*=================\s*全局顶部导航栏\s*=================\s*\*/.*?\.top-nav-menu\s*\{',
    '/* ================= 全局顶部导航栏 ================= */\n.top-header {\n    background: transparent;\n    border: none;\n    height: 60px;\n    display: flex;\n    align-items: center;\n    position: fixed;\n    top: 0;\n    left: 0;\n    width: 100%;\n    z-index: 200;\n    transition: background 0.4s ease, backdrop-filter 0.4s ease;\n    box-sizing: border-box;\n}\n.top-header.scrolled {\n    background: rgba(5, 5, 5, 0.9);\n    backdrop-filter: blur(12px);\n    border-bottom: 1px solid rgba(255, 255, 255, 0.05);\n}\n.top-nav-menu {',
    content,
    flags=re.DOTALL
)

# Replace .top-nav-menu content
content = re.sub(
    r'\.top-nav-menu\s*\{\s*display:\s*flex;\s*justify-content:\s*center;\s*gap:\s*40px;\s*\}',
    '.top-nav-menu {\n    display: flex;\n    justify-content: center;\n    gap: 40px;\n    width: 100%;\n}',
    content,
    flags=re.DOTALL
)

# Replace .sticky-nav
content = re.sub(
    r'\.sticky-nav\s*\{\s*display:\s*flex;\s*justify-content:\s*center;\s*align-items:\s*center;\s*padding:\s*15px\s*5%;\s*position:\s*sticky;\s*top:\s*50px;',
    '.sticky-nav {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    padding: 15px 5%;\n    position: sticky;\n    top: 60px;',
    content,
    flags=re.DOTALL
)

# Clean up garbled text
content = re.sub(
    r'font-size:\s*13px;\n\s*a\s*n\s*i\s*m\s*a\s*t\s*i\s*o\s*n\s*:.*?/\*\s*=================\s*移动端响应式\s*=================\s*\*/',
    'font-size: 13px;\n}\n\n/* ================= 移动端响应式 ================= */',
    content,
    flags=re.DOTALL
)

# Update mobile .hero-logo
content = re.sub(
    r'\.hero-logo\s*\{\s*height:\s*40px;\s*margin-bottom:\s*10px;\s*\}',
    '.hero-logo { height: 120px; margin-bottom: 15px; }',
    content,
    flags=re.DOTALL
)

with codecs.open('index.css', 'w', 'utf-8') as f:
    f.write(content)
