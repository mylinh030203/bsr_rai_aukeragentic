"""Re-apply the news filter after any re-render (F3 follow-up).

`doFeedback`/`important` call `render()`, which rebuilds the feed unfiltered
even though the select still shows the chosen topic. Re-apply the stored
filters right after the page is rebuilt.
"""
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

APP = 'docs/design/prototype/assets/app.js'
app = open(APP, encoding='utf-8', newline='').read()

old = """    bindCharts();
    if (route !== lastRoute) window.scrollTo(0, 0);"""
new = """    bindCharts();
    if (route === 'news') filterNews();
    if (route !== lastRoute) window.scrollTo(0, 0);"""

print('occurrences:', app.count(old))
if app.count(old) != 1:
    sys.exit(1)

open(APP, 'w', encoding='utf-8', newline='').write(app.replace(old, new, 1))
print('render() now re-applies the news filter')
