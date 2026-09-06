"""
Card generator for the GitHub profile README.

Rebuilds dark_mode.svg and light_mode.svg (the two color-scheme variants the
README embeds) from the layout, palette, and profile photo defined below. The
dynamic stat values live in <tspan>
elements with ids (repo_data, commit_data, age_data, ...) which today.py
overwrites nightly via GitHub's GraphQL API — regenerate the cards with this
script, then let today.py fill in the numbers.

Ralph Angelo Gonzaga (codejeroo), 2026

Usage: python3 gen_card.py
"""

import base64

W, H = 1300, 760
RX0, RXE = 380, 1270

# Left-column profile photo. GitHub renders README SVGs as <img>, which blocks
# external references — so the card embeds the image as a base64 data URI.
# Regenerate the optimized asset after swapping in a new photo (full-res source
# stays out of the repo):
#   sips -Z 680 -s format jpeg -s formatOptions 78 src/profile.png --out src/profile_card.jpg
PHOTO_PATH = 'src/profile_card.jpg'
PHOTO_W, PHOTO_H = 340, 300
PHOTO_X = (RX0 - PHOTO_W) // 2
PHOTO_Y = (H - PHOTO_H) // 2 - 28  # bias up: the bio quote sits under the photo

DARK = {'bg': '#161b22', 'body': '#c9d1d9', 'key': '#ffa657', 'value': '#a5d6ff', 'green': '#3fb950',
        'red': '#f85149', 'cc': '#616e7f', 'accent': '#4cc2ff', 'track': '#21262d', 'node': '#8b949e',
        'bar2': '#ffa657', 'bar3': '#58a6ff'}
LIGHT = {'bg': '#f6f8fa', 'body': '#24292f', 'key': '#953800', 'value': '#0a3069', 'green': '#1a7f37',
         'red': '#cf222e', 'cc': '#57606a', 'accent': '#0969da', 'track': '#d0d7de', 'node': '#57606a',
         'bar2': '#bf8700', 'bar3': '#8250df'}

ICONS = {
 'i-term':  '<rect x="1.5" y="3.5" width="21" height="17" rx="2.5"/><path d="M6 9l3.5 3L6 15M12.5 15H18"/>',
 'i-monitor': '<rect x="2.5" y="4.5" width="19" height="12.5" rx="2"/><path d="M9 21h6M12 17v4"/>',
 'i-code':  '<path d="M8 5L2.5 12 8 19M16 5l5.5 7L16 19M13.5 4.5l-3 15"/>',
 'i-brain': '<path d="M12 4.7C9.9 4.7 8.8 5.9 8.4 6.9 6.3 6.7 4.6 8.2 4.6 10.2c0 .8.3 1.5.7 2-.7.5-1 1.3-1 2.1 0 1.7 1.3 2.9 3 2.9.3 1.4 1.6 2.4 3.3 2.4.6 0 1.1-.1 1.4-.4z"/><path d="M12 4.7c2.1 0 3.2 1.2 3.6 2.2 2.1-.2 3.8 1.3 3.8 3.3 0 .8-.3 1.5-.7 2 .7.5 1 1.3 1 2.1 0 1.7-1.3 2.9-3 2.9-.3 1.4-1.6 2.4-3.3 2.4-.6 0-1.1-.1-1.4-.4z"/><path d="M8.5 9.5h1.3M14.2 9.5h1.3M8.2 14.3h1.1M14.7 14.3h1.1"/>',
 'i-chip':  '<rect x="6.5" y="6.5" width="11" height="11" rx="1.5"/><rect x="10" y="10" width="4" height="4" rx=".5"/><path d="M9.5 6.5V3M14.5 6.5V3M9.5 21v-3.5M14.5 21v-3.5M6.5 9.5H3M6.5 14.5H3M21 9.5h-3.5M21 14.5h-3.5"/>',
 'i-mail':  '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
 'i-chart': '<path d="M3 20h18M6.5 20v-7M11.5 20V5.5M16.5 20v-10.5"/>',
 'i-db':    '<ellipse cx="12" cy="5.5" rx="7" ry="2.8"/><path d="M5 5.5v13c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-13"/><path d="M5 12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8"/>',
 'i-embed': '<circle cx="6" cy="8" r="1.6"/><circle cx="11" cy="5" r="1.6"/><circle cx="17" cy="8.5" r="1.6"/><circle cx="8.5" cy="14" r="1.6"/><circle cx="14.5" cy="16" r="1.6"/><circle cx="19" cy="14" r="1.6"/><path d="M6 8l5-3 6 3.5M6 8l2.5 6 6 2M17 8.5L8.5 14M14.5 16L19 14" opacity=".55"/>',
 'i-search':'<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L20.5 20.5"/>',
 'i-answer':'<path d="M3.5 5a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9.5L5 19v-4H5.5a2 2 0 0 1-2-2z"/><path d="M8 9.5l2.5 2.5 5-5"/>',
 'i-wifi':  '<path d="M3.5 10a12.5 12.5 0 0 1 17 0M6.5 13.2a8 8 0 0 1 11 0M9.4 16.2a3.8 3.8 0 0 1 5.2 0"/><circle cx="12" cy="19" r="1.3"/>',
 'i-share': '<circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="6" r="2.6"/><circle cx="18" cy="18" r="2.6"/><path d="M8.4 10.8l7.2-3.6M8.4 13.2l7.2 3.6"/>',
}

class Card:
    def __init__(self, pal):
        self.p = pal
        self.out = []

    def text(self, x, y, s, cls=None, anchor=None, size=None, extra='', weight=None):
        a = f' x="{x}" y="{y}"'
        if anchor: a += f' text-anchor="{anchor}"'
        if size: a += f' font-size="{size}"'
        if weight: a += f' font-weight="{weight}"'
        if cls: a += f' class="{cls}"'
        self.out.append(f'<text{a}{" " + extra.strip() if extra.strip() else ""}>{s}</text>')

    def tspan_row(self, x, y, frags):
        # frags: (css_class_or_None, id_or_None, text)
        parts = []
        for cls, id_, s in frags:
            attr = (f' class="{cls}"' if cls else '') + (f' id="{id_}"' if id_ else '')
            parts.append(f'<tspan{attr}>{s.replace("&","&amp;").replace("<","&lt;")}</tspan>')
        self.out.append(f'<text x="{x}" y="{y}">{"".join(parts)}</text>')

    def line(self, x1, y1, x2, y2, stroke, w='1', op='0.35', dash=''):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
                        f'stroke-width="{w}" opacity="{op}"{d}/>')

    def divider(self, y):
        self.line(RX0, y, RXE, y, '#8b949e', op='0.25', dash='1 5')

    def icon(self, name, x, y, scale=1):
        s = f' scale({scale})' if scale != 1 else ''
        self.out.append(f'<g transform="translate({x},{y}){s}"><use href="#{name}"/></g>')

    def circle(self, cx, cy, r, fill, stroke=None, sw='1.3'):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ' stroke="none"'
        self.out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}/>')

    def rect(self, x, y, w_, h_, fill, rx='0'):
        self.out.append(f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="{rx}" fill="{fill}"/>')

    def kv(self, x, y, key, pad, value_cls, value, vid=None):
        self.tspan_row(x, y, [('key', None, key.ljust(pad) + ':'),
                              ('cc', None, ' '),
                              (value_cls, vid, value)])

    def neural_network(self):
        # Animated forward-pass diagram (right of info). SMIL runs even in the README's
        # <img>-embedded context (same mechanism as the status blink), so every element
        # shares one 5s cycle and encodes its active window via keyTimes — that keeps the
        # whole wave in sync and leaves an idle gap before each repeat.
        nnx = [1020, 1065, 1110, 1155, 1200, 1250]
        cnt = [4, 4, 3, 2, 2, 1]
        cy, gap = 158, 20
        cols = [[(nnx[i], cy + (j - (cnt[i] - 1) / 2) * gap) for j in range(cnt[i])] for i in range(6)]
        T = 5  # cycle seconds
        fire = lambda i: 0.2 + i * 0.7  # when column i activates
        kt = lambda ts: ';'.join(f'{t / T:.3f}' for t in ts)  # seconds -> keyTimes fractions
        for i in range(5):
            for x1, y1 in cols[i]:
                for x2, y2 in cols[i + 1]:
                    self.line(x1, y1, x2, y2, self.p['node'], '0.8', '0.45')
                    # signal dot travels the edge just before the next column fires
                    t0, t1 = fire(i) + 0.1, fire(i + 1)
                    self.out.append(
                        f'<circle r="2" fill="{self.p["accent"]}" opacity="0">'
                        f'<animate attributeName="opacity" values="0;0;0.9;0.9;0;0" '
                        f'keyTimes="{kt([0, max(0, t0 - 0.1), t0, t1, t1 + 0.2, T])}" '
                        f'dur="{T}s" repeatCount="indefinite"/>'
                        f'<animateMotion path="M {x1},{y1} L {x2},{y2}" keyPoints="0;0;1;1" '
                        f'keyTimes="{kt([0, t0, t1, T])}" calcMode="linear" '
                        f'dur="{T}s" repeatCount="indefinite"/></circle>')
        for i, c in enumerate(cols):
            t0 = fire(i)
            # node flash window: ramp to peak at t0+0.18, settle by t0+0.35
            bump = kt([0, t0, t0 + 0.18, t0 + 0.35, T])
            flash = kt([0, t0, t0 + 0.10, t0 + 0.25, T])
            for x, y in c:
                if i == 0:
                    head = f'<circle cx="{x}" cy="{y}" r="4.2" fill="{self.p["accent"]}" stroke="none">'
                else:
                    head = (f'<circle cx="{x}" cy="{y}" r="4.2" fill="{self.p["bg"]}" '
                            f'stroke="{self.p["node"]}" stroke-width="1.3">'
                            f'<animate attributeName="fill" '
                            f'values="{self.p["bg"]};{self.p["bg"]};{self.p["accent"]};'
                            f'{self.p["bg"]};{self.p["bg"]}" keyTimes="{flash}" '
                            f'dur="{T}s" repeatCount="indefinite"/>')
                self.out.append(f'{head}<animate attributeName="r" values="4.2;4.2;5.8;4.2;4.2" '
                                f'keyTimes="{bump}" dur="{T}s" repeatCount="indefinite"/></circle>')
        self.text(1135, 96, 'NEURAL NETWORK', cls='sec', anchor='middle', size=13)
        self.text(1135, 240, '128 → 64 → 32 → 16 → 8 → 1', cls='cc', anchor='middle', size=13)

    def render(self):
        pal = self.p
        # header
        self.icon('i-term', RX0 + 2, 26, 1.05)
        self.text(RX0 + 44, 47, 'codejeroo@caraga', weight='bold', size=20, extra=f' fill="{pal["body"]}"')
        self.text(RXE - 14, 47, 'AI ENGINEERING // EDGE INTELLIGENCE', cls='sec', anchor='end')
        self.circle(RXE - 2, 42, 4, pal['accent'])
        self.divider(64)
        # info
        self.icon('i-monitor', RX0 + 2, 82)
        for key, dy, vid, val in [
            ('OS', 0, None, 'macOS, Windows, Linux'),
            ('GitHub since', 24, 'age_data', '5 years, 0 months, 0 days'),
            ('Host', 48, None, 'Caraga State University, Butuan, PH'),
            ('Kernel', 72, None, 'Software (AI/ML) Engineering'),
            ('IDE', 96, None, 'VS Code')]:
            self.kv(RX0 + 55, 102 + dy, key, 13, 'value', val, vid)
        self.neural_network()
        self.divider(258)
        # languages
        self.icon('i-code', RX0 + 2, 276)
        self.text(RX0 + 55, 292, 'LANGUAGES', cls='sec')
        self.text(RX0 + 55, 320, 'Python, JavaScript, C, C++', cls='value')
        for i, (lbl, col, wfill) in enumerate([
                ('Python', pal['accent'], 239), ('JavaScript', pal['bar2'], 203), ('C / C++', pal['bar3'], 161)]):
            y = 288 + i * 24
            self.text(900, y + 7, lbl, size=13, weight='bold', extra=f' fill="{col}"')
            self.rect(1010, y, 260, 8, pal['track'], rx='4')
            self.rect(1010, y, wfill, 8, col, rx='4')
        self.divider(368)
        # ai/ml focus + rag pipeline beside it
        self.icon('i-brain', RX0 + 2, 386)
        self.text(RX0 + 55, 402, 'AI / ML FOCUS', cls='sec')
        self.text(RX0 + 55, 428, 'Agentic AI, RAG, Computer Vision,', cls='value')
        self.text(RX0 + 55, 450, 'Natural Language Processing, Edge AI', cls='value')
        for i, (ic, lbl) in enumerate([('i-db', 'DATA'), ('i-embed', 'EMBEDDING'), ('i-search', 'RETRIEVAL'),
                                       ('i-brain', 'LLM'), ('i-answer', 'ANSWER')]):
            x = 830 + i * 100
            self.icon(ic, x, 396, 1.15)
            if i < 4:
                self.text(x + 72, 416, '→', extra=f'fill="{pal["node"]}"')
            self.text(x + 15, 452, lbl, cls='sec', anchor='middle', size=11)
        self.divider(472)
        # hardware
        self.icon('i-chip', RX0 + 2, 490)
        self.text(RX0 + 55, 506, 'HARDWARE', cls='sec')
        self.text(RX0 + 55, 532, 'IoT, Arduino, Raspberry Pi, ESP32, Embedded C', cls='value')
        for i, ic in enumerate(['i-chip', 'i-wifi', 'i-share']):
            self.icon(ic, 1060 + i * 75, 492, 1.15)
        self.divider(556)
        # bottom band: contact beside github stats
        self.icon('i-mail', RX0 + 2, 566)
        self.text(RX0 + 55, 582, 'CONTACT', cls='sec')
        for i, (k, v) in enumerate([
                ('Email', 'gonzaga.angelor@gmail.com'), ('GitHub', 'github.com/codejeroo'),
                ('LinkedIn', 'in/ralph-angelo-gonzaga-a32184320')]):
            self.kv(RX0 + 12, 606 + i * 21, k, 15, 'value', v)
        self.icon('i-chart', 950, 566)
        self.text(1003, 582, 'GITHUB STATS', cls='sec')
        def statrow(y, frags, size=14):
            parts = []
            for cls, id_, s in frags:
                attr = (f' class="{cls}"' if cls else '') + (f' id="{id_}"' if id_ else '')
                parts.append(f'<tspan{attr}>{s.replace("&","&amp;").replace("<","&lt;")}</tspan>')
            self.out.append(f'<text x="950" y="{y}" font-size="{size}">{"".join(parts)}</text>')
        statrow(606, [('key', None, 'Repos :      '), ('value', 'repo_data', '33'),
                      ('key', None, '   Contributed : '), ('value', 'contrib_data', '33')])
        statrow(627, [('key', None, 'Stars :      '), ('value', 'star_data', '0'),
                      ('key', None, '   Commits : '), ('value', 'commit_data', '0')])
        statrow(648, [('key', None, 'Followers : '), ('value', 'follower_data', '1')])
        statrow(669, [('key', None, 'Lines of Code : '), ('value', 'loc_data', '0')])
        statrow(690, [('cc', None, '( '), ('addColor', 'loc_add', '0'), ('cc', None, '++ , '),
                      ('delColor', 'loc_del', '0'), ('cc', None, '-- )')])
        # footer
        self.divider(722)
        self.text(RX0 + 2, 745, 'LEARNING. SHIPPING. IMPROVING.', cls='sec', size=15)
        self.text(RXE - 20, 745, 'STATUS: ONLINE', anchor='end', weight='bold', extra=f' fill="{pal["green"]}"')
        # bio slogan under the centered photo (left column), wrapped to fit the 340px photo width
        for i, line in enumerate([
                '“Building what I imagine,', 'learning what I don’t know,',
                'and shipping what matters.”']):
            self.text(PHOTO_X + PHOTO_W / 2, PHOTO_Y + PHOTO_H + 30 + i * 20, line,
                      cls='cc', anchor='middle', size=14)
        self.out.append(f'<rect x="{RXE - 12}" y="734" width="11" height="11" rx="2" fill="{pal["green"]}">'
                        f'<animate attributeName="opacity" values="1;0.15;1" dur="2s" repeatCount="indefinite"/></rect>')
        # assemble
        defs = ''.join(f'<g id="{n}" fill="none" stroke="{pal["accent"]}" stroke-width="1.6" '
                       f'stroke-linecap="round" stroke-linejoin="round">{b}</g>' for n, b in ICONS.items())
        style = f'''<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {pal['key']};}}
.value {{fill: {pal['value']};}}
.addColor {{fill: {pal['green']};}}
.delColor {{fill: {pal['red']};}}
.cc {{fill: {pal['cc']};}}
.sec {{fill: {pal['accent']}; font-weight: bold; letter-spacing: 1px;}}
text, tspan {{white-space: pre;}}
</style>'''
        bg = pal['bg']
        return (f'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" '
                f'width="{W}px" height="{H}px" font-size="16px">\n{style}\n'
                f'<rect width="{W}px" height="{H}px" fill="{bg}" rx="15"/>\n'
                f'<defs>{defs}{photo_clip()}</defs>\n{photo_block(pal)}\n' + '\n'.join(self.out) + '\n</svg>')


def photo_clip():
    """Rounded-corner clip for the left-column photo box."""
    return (f'<clipPath id="pclip"><rect x="{PHOTO_X}" y="{PHOTO_Y}" '
            f'width="{PHOTO_W}" height="{PHOTO_H}" rx="12"/></clipPath>')

def photo_block(pal):
    """Embed the profile photo as a rounded, accent-framed image centered in the
    left band. The bytes are inlined as a data URI so the card stays self-contained."""
    with open(PHOTO_PATH, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    return (f'<image href="data:image/jpeg;base64,{b64}" x="{PHOTO_X}" y="{PHOTO_Y}" '
            f'width="{PHOTO_W}" height="{PHOTO_H}" clip-path="url(#pclip)" '
            f'preserveAspectRatio="xMidYMid slice"/>\n'
            f'<rect x="{PHOTO_X}" y="{PHOTO_Y}" width="{PHOTO_W}" height="{PHOTO_H}" rx="12" '
            f'fill="none" stroke="{pal["accent"]}" stroke-width="1.5" opacity="0.8"/>')


if __name__ == '__main__':
    for fname, pal in [('dark_mode.svg', DARK), ('light_mode.svg', LIGHT)]:
        with open(fname, 'w') as f:
            f.write(Card(pal).render())
        print('wrote', fname)
