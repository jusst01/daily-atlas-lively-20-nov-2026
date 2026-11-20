from PIL import ImageFont, ImageDraw, Image
F = "/usr/share/fonts/truetype/dejavu/"
img = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(img)
def font(n, s): return ImageFont.truetype(F + n, s)
def wrap(text, f, mw):
    words = text.split(); lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= mw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

BRIEFS = [
"Brussels: Coordinated European youth action day - living costs, housing and education; more planned for the weekend",
"Genoa: The airport suspends flights after unidentified drones are detected",
"France: One dead and 15 injured in a fire at an 18-storey apartment building",
"New Caledonia: A 5.6-magnitude earthquake strikes near the islands",
"Washington: The US sanctions the Comancheros biker network and an 'Ndrangheta web, its Toronto faction included",
"Washington: Trump announces a posthumous pardon for baseball legend Pete Rose",
"San Salvador: Bukele formally registers to seek a third presidential term",
"Warsaw: Poland prepares a $50bn nuclear-power deal with US firms",
"Menlo Park: Meta revises its 2030 climate targets amid its AI infrastructure expansion",
"New Delhi: India-Japan 2+2 - Japanese forces will train at Indian ranges; missile and maritime tech agreed",
"Amsterdam: 'The Year of the Ghost' wins Best Film at the IDFA documentary festival",
"Cincinnati: Fiona the hippo dies at the zoo, days after swallowing a visitor's hat",
"Washington: The White House taps Kirsten Davies as national cyber director after widespread outages",
"Washington: The Senate nears a vote on a permitting bill to speed power-plant and transmission reviews",
"South Pacific: Cyclone Xavier - RSMC Nadi issues bulletin 39; island warning levels unchanged",
"Paris: Macron backs Philippe Diallo's bid for the FIFA presidency",
"Formula 1: Verstappen backs F1's plan to press ahead with its Middle East races despite the war",
"Washington: The US war with Iran has cost over $48bn so far, officials say",
]

for size in (9.5, 9.25, 9.0, 8.75, 8.5, 8.25, 8.0):
    f = font("DejaVuSans.ttf", size)
    lh = size + 2
    counts = [len(wrap(b, f, 145)) for b in BRIEFS]
    hts = [c * lh + 2 for c in counts]  # +2 gap
    print(size, "lines", counts, "total", sum(hts))
    # greedy contiguous split 3..7 per col balancing
    best = None
    n = len(BRIEFS)
    import itertools
    for a in range(3, 8):
        for b in range(3, 8):
            for c in range(3, 8):
                dd = n - a - b - c
                if not (3 <= dd <= 7): continue
                cols = [sum(hts[0:a]), sum(hts[a:a+b]), sum(hts[a+b:a+b+c]), sum(hts[a+b+c:])]
                m = max(cols)
                if best is None or m < best[0]: best = (m, (a,b,c,dd), cols)
    print("   best", best)
