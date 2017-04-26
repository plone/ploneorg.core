from pyquery import PyQuery as pq

LAUNCHPAD_URLS = [
    'https://launchpad.net/plone/+download',
    'https://launchpad.net/plone/+download?memo=10&start=10',
    'https://launchpad.net/plone/+download?memo=20&start=20',
    'https://launchpad.net/plone/+download?memo=30&start=30',
    'https://launchpad.net/plone/+download?memo=40&start=40',
    'https://launchpad.net/plone/+download?memo=50&start=50',
    'https://launchpad.net/plone/+download?memo=60&start=60'
]


def get_downloads():
    result = 0
    for url in LAUNCHPAD_URLS:
        query = pq(url=url)
        for value in query('td:nth-child(3)'):
            result += int(value.text.strip().replace(',', ''))
    print(result)
