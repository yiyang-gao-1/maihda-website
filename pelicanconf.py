AUTHOR = 'Dr Yiyang Gao'
SITENAME = 'MAIHDA Resource Hub'
SITEURL = ""

PATH = "content"

MARKUP = ('md', 'markdown')

TIMEZONE = 'Europe/London'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('University of Sheffield', 'https://sheffield.ac.uk/education/smi'),
    ('MAIHDA Project', 'https://intersectionalhealth.org/projects/esrc-maihda-project/'),
    ('Google Scholar', 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=MAIHDA&btnG='),
)

# Social widget
SOCIAL = (
    ('GitHub', 'https://github.com/yiyang-gao-1'),
    ('Email', 'mailto:y.gao@sheffield.ac.uk'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# Theme settings
THEME = 'themes/maihda-theme'
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']
PAGINATED_TEMPLATES = {
    'index': None,
    'tag': None,
    'category': None,
    'author': None,
}

# Static paths
STATIC_PATHS = ['data', 'images', 'extra']

# Menu items
MENUITEMS = (
    ('Home', '/'),
    ('Papers', '/category/papers.html'),
    ('Resources', '/pages/resources.html'),
    ('About', '/pages/about.html'),
)

# GitHub Pages settings
GITHUB_URL = 'https://github.com/yiyang-gao-1/maihda-website'