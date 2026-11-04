#!/usr/bin/env python3
"""Today's news topics for the Mochi robots: a few kid-safe headlines, written to stdout as JSON.

Runs every day on the update hub (NOXUSTIC/mochi-updates, .github/workflows/topics.yml) and writes
topics/topics.json, which the robots read (firmware v30+, social.h) and talk about with each other.
Only the Python standard library, so the GitHub runner needs nothing installed.

Safety first: the robots are toys on children's desks. A headline is kept only if it passes a word list
(no war, crime, death, disaster, politics fights, drugs, ...), is short, and is plain ASCII after cleaning.
Science, space, technology, nature and sport come first; world news only when it passes the same filter.
"""
import json, re, sys, html, unicodedata, datetime, urllib.request
import xml.etree.ElementTree as ET

FEEDS = [  # (category, url): feeds without a paywall, read once a day; mostly discoveries, so mostly cheerful
    ('science', 'https://www.sciencedaily.com/rss/top/science.xml'),
    ('space', 'https://www.sciencedaily.com/rss/space_time.xml'),
    ('animals', 'https://www.sciencedaily.com/rss/plants_animals.xml'),
    ('tech', 'https://www.sciencedaily.com/rss/computers_math.xml'),
    ('science', 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml'),
    ('sport', 'https://feeds.bbci.co.uk/sport/rss.xml'),
]
PER = {'science': 3, 'space': 3, 'animals': 2, 'tech': 2, 'sport': 2}
MAX = 12

# anything a child should not hear from a toy, or that would sound wrong in a cheerful robot chat
BLOCK = r'''
kill|killed|killing|dead|death|deaths|die|dies|died|dying|murder|shoot|shooting|shot|gun|guns|knife|stab|stabbing|
war|wars|warfare|army|military|troops|missile|missiles|bomb|bombing|bombs|attack|attacks|attacked|strike|strikes|airstrike|
terror|terrorist|terrorism|hostage|hostages|massacre|genocide|invasion|invade|soldier|soldiers|weapon|weapons|nuclear|drone strike|
crash|crashes|crashed|collision|disaster|earthquake|flood|floods|wildfire|hurricane|tornado|tsunami|famine|drought|victim|victims|
injured|injury|injuries|wounded|hospital|cancer|disease|virus|outbreak|pandemic|epidemic|sick|illness|overdose|suicide|self-harm|
abuse|abused|assault|rape|sexual|sex|porn|nude|naked|drug|drugs|cocaine|heroin|cannabis|alcohol|drunk|gambling|casino|
crime|criminal|police|arrest|arrested|jail|prison|prisoner|court|trial|guilty|sentenced|charged|lawsuit|sue|sued|fraud|scam|theft|stolen|robbery|
election|elections|vote|voting|president|prime minister|minister|government|parliament|congress|senate|trump|putin|party leader|
protest|protests|riot|riots|refugee|refugees|migrant|migrants|border|sanctions|tariff|tariffs|scandal|resign|resigns|fired|sacked|
hate|racist|racism|extremist|ban|banned|threat|threats|threaten|danger|dangerous|deadly|fatal|tragedy|tragic|grief|mourn|funeral|
layoff|layoffs|recession|bankrupt|inflation|debt|crisis|emergency|collapse|toxic|poison|explosion|exploded|fire|blaze
'''
def words(s):
    return '|'.join(w.strip() for w in s.replace('\n', '').split('|') if w.strip())


BLOCK_RE = re.compile(r'\b(' + words(BLOCK) + r')\b', re.I)
# word families: anything that starts with these
STEMS = r'''wildfire|terrif|horrif|hack|crypto|bitcoin|scam|violen|weapon|bomb|murder|kill|attack|assault|abus|explo[ds]|
casualt|fatalit|tragic|disast|catastroph|starv|poverty|slave|kidnap|traffick|smuggl|prostitut|corrupt|bribe|
korea|iran|israel|gaza|palestin|ukrain|russia|syria|sudan|yemen|afghan|taliban|hamas|isis|nazi|
politic|elect|campaign|lawsuit|sanction|tariff|deport|immigra|warfare|warn|worsen|fear|scare|panic|anxi|depress|lonel|
climate change|global warming|extinct|pollut|air quality|smog|emission|net zero|plastic waste|cull|poach|hunt|
alcohol|smok|vap|tobacco|opioid|steroid|doping|betting|gambl|lottery|celebrit|dating|divorce|affair|bikini|
bulletin|advisory|recall|defect|crack|fail|faulty|error|outage|leak|breach|spy|surveil|privacy|chemical'''
STEM_RE = re.compile(r'\b(' + words(STEMS) + r')', re.I)



def ascii_text(s):
    s = html.unescape(s or '')
    s = s.replace('‘', "'").replace('’', "'").replace('“', '').replace('”', '').replace('"', '')
    s = s.replace('–', '-').replace('—', '-').replace('…', '...')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mochi topics (github.com/NOXUSTIC/mochi-updates)'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def headlines(cat, url):
    out = []
    try:
        root = ET.fromstring(fetch(url))
    except Exception as e:  # one feed down is fine: the others still count
        print('skip %s: %s' % (url, e), file=sys.stderr)
        return out
    for item in root.iter('item'):
        t = ascii_text(item.findtext('title'))
        if not (20 <= len(t) <= 100) or BLOCK_RE.search(t) or STEM_RE.search(t) or t.isupper() or t.count(':') > 0:
            continue
        if not re.search(r'[a-z]', t) or t.endswith('?'):
            continue
        if not t.endswith(('.', '!')):
            t += '.'
        out.append(t)
    return out


def main():
    topics, seen = [], set()
    for cat, url in FEEDS:
        n = 0
        for t in headlines(cat, url):
            key = t.lower()[:40]
            if key in seen:
                continue
            seen.add(key)
            topics.append({'c': cat, 't': t})
            n += 1
            if n >= PER[cat] or len(topics) >= MAX:
                break
        if len(topics) >= MAX:
            break
    if not topics:
        sys.exit('no topics today: keeping yesterday\'s file')
    json.dump({'date': datetime.date.today().isoformat(), 'topics': topics}, sys.stdout, indent=1)
    print()


if __name__ == '__main__':
    main()
