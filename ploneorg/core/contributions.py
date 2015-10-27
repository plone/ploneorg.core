# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from github import Github
from github import UnknownObjectException

import argparse
import datetime
import json
import logging
import os
import requests
import stackexchange
import time
from twitter import Twitter
from twitter import OAuth


logging.basicConfig()
logger = logging.getLogger('contributions')

debug_limit = None

GITHUB_TIMEFORMAT = '%Y-%m-%dT%H:%M:%S%z'

_GITHUB_FETCHES_BASE = ['issues', 'contributions', 'commits']
OTHER_FETCHES = ['stackoverflow', 'pypi', 'twitter', 'community', ]
ALL_FETCHES = _GITHUB_FETCHES_BASE + OTHER_FETCHES
GITHUB_FETCHES = set(_GITHUB_FETCHES_BASE)


class User(object):

    def __init__(self, name):
        self.name = name
        self.repos = {}
        self.contributions = 0

    def add_contributions(self, repo, count):
        self.repos[repo] = count
        self.contributions += count

    def __str__(self):
        return '%s: %s (%s repos)' % (self.name,
                                      self.contributions,
                                      len(self.repos))

    def __repr__(self):
        return '<User: %s<' % str(self)


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, User):
            return str(obj.contributions)

        return super(JSONEncoder, self).default(obj)


def find_base(config_filename):
    path = os.getcwd()
    while path:
        if os.path.exists(os.path.join(path, config_filename)):
            break
        old_path = path
        path = os.path.dirname(path)
        if old_path == path:
            path = None
            break
    if path is None:
        raise IOError('File {0} not found'.format(config_filename))
    return path


def check_debug_limit(iterable, type_):
    if debug_limit:
        logger.info('Debug limit for %s: %s' % (type_, debug_limit))
    # after slicing problems with github.PaginatedList turn into
    # generator
    for idx, item in enumerate(iterable):
        if debug_limit and idx > debug_limit:
            break
        yield item


def find_data_dir(config, base_dir):
    '''Calculate the data dir and make sure it exists'''
    data_dir = config.get('general', 'datadir')
    if not data_dir.startswith(os.path.sep):
        # path not absolute, make relative to dir of config file
        data_dir = os.path.abspath(os.path.join(base_dir, data_dir))
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def get_auth(config):
    admin_user = config.get('general', 'admin_user')
    admin_password = config.get('general', 'admin_password')
    return requests.auth.HTTPBasicAuth(admin_user, admin_password)


def write_data(config, base_dir, json_string):
    """Write the data do a json file.
    """
    data_dir = find_data_dir(config, base_dir)
    isodate = datetime.datetime.now().isoformat()
    filename = 'contributions.{0:s}.json'.format(isodate)
    path = os.path.join(data_dir, filename)
    with open(path, 'w') as f:
        f.write(json_string)
    logger.info('Wrote data to {0}'.format(path))


def fetch(config, args):
    data = {
        'github': {},
        'stackoverflow': None,
        'pypi': None,
        'twitter': None,
        'community': None,
    }
    try:

        if set(args.fetch_specific) & GITHUB_FETCHES:
            data['github']['plone'] = fetch_github(config, 'plone', args)
            data['github']['collective'] = fetch_github(
                config,
                'collective',
                args
            )
        if 'stackoverflow' in args.fetch_specific:
            data['stackoverflow'] = fetch_stackoverflow(config)
        if 'pypi' in args.fetch_specific:
            data['pypi'] = fetch_pypi(config)
        if 'twitter' in args.fetch_specific:
            data['twitter'] = fetch_twitter(config)
        if 'community' in args.fetch_specific:
            data['community'] = fetch_community(config)
    except IOError:
        logger.exception('An IOError happend, probably a read timeout')
        exit(1)
    json_string = json.dumps(data, cls=JSONEncoder, sort_keys=True, indent=4)
    base_dir = find_base(args.config)
    write_data(config, base_dir, json_string)
    return json_string


def _fetch_github_contributor_info(
    repo,
    data,
):
    try:
        logger.debug('... get contributors for %s' % repo.name)
        contributors = repo.get_contributors()
        for contributor in contributors:
            login = contributor.login
            user = data['contributions'].setdefault(login, User(login))
            user.add_contributions(repo.name, contributor.contributions)
    except (UnknownObjectException, TypeError):
        # empty repository
        logger.debug('... repository "%s" seems to be empty' % repo.name)
        data['unknown'].append(repo.name)


def _fetch_github_commits_info(
    repo,
    data,
    delta_weeks,
):
    logger.debug('... fetch commits for repo {0} started'.format(repo.name))
    participation = repo.get_stats_participation()
    if participation is None:
        # no stats available, give github some time to calculate and try agains
        logger.debug('... no stats available, retry in 2s!')
        time.sleep(2)
        participation = repo.get_stats_participation()
        if participation is None:
            logger.debug('... give up, no stats available')
            return
    current_delta = delta_weeks
    if len(participation.all) < delta_weeks:
        current_delta = len(participation.all)
    if data['commits'] < 0:
        data['commits'] = 0
    data['commits'] += sum(participation.all[-current_delta:])


def _fetch_github_issue_info(
    gh,
    organization_name,
    data,
    since,
    blocker_labels,
):
    logger.debug('... fetch issues for {0} started'.format(organization_name))

    # todo: error handling if gh does not like us anymore

    # FETCH ALL OPEN PRS
    prs_all_open = gh.search_issues(
        'user:{0:s} is:open is:pr'.format(
            organization_name
        )
    )
    data['pull_requests'] = prs_all_open.totalCount
    logger.debug('... {0} open PRs'.format(data['pull_requests']))

    # FETCH NEEDS REVIEW
    prs_need_review = gh.search_issues(
        'user:{0:s} is:open is:pr comments:0'.format(
            organization_name
        )
    )
    data['needs_review'] = prs_need_review.totalCount
    logger.debug('... {0} need review'.format(data['needs_review']))

    # FETCH NEW ISSUES
    issues_created_since = gh.search_issues(
        'user:{0:s} is:open is:issue created:>{1}'.format(
            organization_name,
            since.strftime(GITHUB_TIMEFORMAT)
        )
    )
    data['new_issues'] = issues_created_since.totalCount
    logger.debug(
        '... {0} new issues since {1}'.format(
            data['new_issues'],
            since.isoformat(),
        )
    )

    # FETCH BLOCKERS
    data['blockers'] = 0
    for blocker_label in blocker_labels:
        # loop needed because afaik theres no OR search at Github
        issues_blockers = gh.search_issues(
            'user:plone is:open label:{0}'.format(
                blocker_label
            )
        )
        data['blockers'] += issues_blockers.totalCount
    logger.debug('... {0} blockers'.format(data['blockers']))

    logger.debug('... issues finished')


def fetch_github(
    config,
    organization_name,
    args,
):
    """fetches data about an organization from github

    - Contributions by user
    - New issues since ``newticket_delta``
    - Commits since ``commits_delta``
    - Release blockers (total, needs a label to check for)
    - Open pull requests (total)
    - Patches needing reviews (total, no comments so far)
    """
    logger.info('Fetch data from github for "%s"...' % organization_name)
    token = config.get('github', 'token')
    gh = Github(token)

    logger.debug('... get organization data')
    organization = gh.get_organization(organization_name)

    start_limit = current_limit = gh.rate_limiting[0]

    data = {
        'rate_limits': {
            'doc': 'Track github api request rate limits. Just in case',
            'start': start_limit,
            'expense': {},
            'end': None},
        'contributions': {},
        'new_issues': -1,
        'commits': -1,
        'blockers': -1,
        'pull_requests': -1,
        'needs_review': -1,
        'unknown': []
    }

    if 'issues' in args.fetch_specific:
        blocker_labels = config.get('github', 'blocker_labels').split()
        blocker_labels = [lbl.strip() for lbl in blocker_labels]
        ni_delta = int(config.get('github', 'newissues_delta'))
        since = datetime.datetime.now() - datetime.timedelta(ni_delta)
        _fetch_github_issue_info(
            gh,
            organization_name,
            data,
            since,
            blocker_labels,
        )

    # REPOSITORY RELATED COLLECTING
    # get 100 repositories per page
    organization._requester.per_page = 100
    repos = check_debug_limit(organization.get_repos(), 'repos')
    ci_delta = int(config.get('github', 'commits_delta'))

    for repo in repos:
        if 'commits' in args.fetch_specific:
            _fetch_github_commits_info(
                repo,
                data,
                ci_delta,
            )

        if 'contributions' in args.fetch_specific:
            _fetch_github_contributor_info(
                repo,
                data
            )
        # Track # of requests used for the repo
        new_limit = gh.rate_limiting[0]
        logger.debug('... rate limit at {0}'.format(new_limit))
        data['rate_limits']['expense'][repo.name] = current_limit - new_limit
        current_limit = new_limit

        # If we are about to hit the limit, sleep until the limit is resetted
        if new_limit < 20:
            reset_time = int(gh.rate_limiting_resettime)
            reset_datetime = datetime.datetime.fromtimestamp(reset_time)
            now = datetime.datetime.now()
            delta = reset_datetime - now
            print('Sleeping until {0}'.format(reset_datetime))
            time.sleep(delta.total_seconds())

    data['rate_limits']['end_limit'] = current_limit
    logger.info('Done.')
    return data


def fetch_stackoverflow(config):
    # get all stackoverflow ids form member profiles
    logger.info('Fetch data from stackoverflow...')
    logger.info('...Get stackoverflow ids from Plone.')
    url = (config.get('general', 'plone_url') +
           '/@@contributor-stackoverflow-ids')
    r = requests.get(
        url, auth=get_auth(config),
        allow_redirects=False)  # don't redirect to the login form for unauth

    if r.status_code != 200:
        msg = ("Can't fetch stackoverflow user ids from plone."
               'status: %s.') % r.status_code
        if r.status_code == 302:
            msg += 'This might be and authentication error.'
        logger.error(msg)
        logger.error('Cannot fetch stackoverflow data. Exit.')
        exit(1)

    stackoverflow_users = r.json()['data']

    logger.info('...Start getting data from stackoverflow.')
    plone_member_ids = check_debug_limit(stackoverflow_users.keys(),
                                         'stackoverflow users')
    stackoverflow = stackexchange.Site(stackexchange.StackOverflow)
    for member_id in plone_member_ids:
        stackoverflow_id = stackoverflow_users[member_id]
        activity = _so_activity_for_user(stackoverflow, stackoverflow_id,
                                         member_id)
        stackoverflow_users[member_id] = activity

    logger.info('Done.')
    return stackoverflow_users


def fetch_pypi(config):
    logger.info('Fetch data from pypi...')
    package = config.get('general', 'plone_package')
    url = 'http://pypi.python.org/pypi/{0}/json'.format(package)
    rq = requests.get(url)
    if rq.status_code != 200:
        logger.warn('Can not fetch url {0}'.format(url))
        return
    result = rq.json()
    return result['info']['downloads']


def fetch_twitter(config):
    # get all twitter ids form member profiles
    logger.info('Fetch data from twitter...')
    logger.info('...Get twitter ids from Plone.')
    url = (config.get('general', 'plone_url') +
           '/@@contributor-twitter-ids')
    r = requests.get(
        url, auth=get_auth(config),
        allow_redirects=False)  # don't redirect to the login form for unauth

    if r.status_code != 200:
        msg = ("Can't fetch stackoverflow user ids from plone."
               'status: %s.') % r.status_code
        if r.status_code == 302:
            msg += 'This might be and authentication error.'
        logger.error(msg)
        logger.error('Cannot fetch stackoverflow data. Exit.')
        exit(1)

    twitter_users = r.json()['data']

    logger.info('...Start getting data from twitter.')
    plone_member_ids = check_debug_limit(twitter_users.keys(),
                                         'stackoverflow users')

    token = config.get('twitter', 'token')
    token_secret = config.get('twitter', 'token_secret')
    consumer_key = config.get('twitter', 'consumer_key')
    consumer_secret = config.get('twitter', 'consumer_secret')

    if token is None or \
            token_secret is None or \
            consumer_key is None or \
            consumer_secret is None:
        return 'Please add "token", "token_secret", "consumer_key" and ' \
               '"consumer_secret" on the configuration file on a [twitter] ' \
               'section.'

    twitter_app = Twitter(
        auth=OAuth(
            token,
            token_secret,
            consumer_key,
            consumer_secret
        )
    )
    for member_id in plone_member_ids:
        twitter_id = twitter_users[member_id]
        data = twitter_app.search.tweets(
            q='#plone from:{0}'.format(twitter_id)
        )
        twitter_users[member_id] = data['search_metadata']['count']

    logger.info('Done.')
    return twitter_users


def fetch_community(config):
    logger.info('Fetch data from community.plone.org ...')
    url = 'https://community.plone.org/about.json'
    rq = requests.get(url)
    if rq.status_code != 200:
        logger.warn('Can not fetch url {0}'.format(url))
        return
    result = rq.json()
    return result['about']['stats']['post_count']


def _so_activity_for_user(stackoverflow, userid, member_id):
    # FIXME: something better is needed here.
    # FIXME: ask for top answerers last month also?
    logger.debug('...plone member: %s, so userid: %s' % (member_id, userid))
    user = stackoverflow.user(userid)
    user.tags.fetch()
    for tag in user.tags:
        print tag.name, tag.count
        if tag.name == u'plone':
            return tag.count
    return 0


def upload(config, json_string):
    """Upload data to Plone
    """
    url = config.get('general', 'plone_url') + '/@@update-contributor-data'
    logger.info('Upload data to "%s"...' % url)
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain'}
    r = requests.post(
        url, data=json_string, headers=headers,
        allow_redirects=False,  # don't redirect to the login form for unauth
        auth=get_auth(config))
    if r.status_code != 200:
        content = '*content stripped*' if (r.status_code == 302) else r.content
        message = (
            'Someting went wrong uploading the contribution data to\n' +
            '%s\n\n' % url +
            '---- Response ----\n' +
            'status: %s, reason: %s\n' % (r.status_code, r.reason) +
            content + '\n\n'
            '---- Data to upload ----\n' +
            json_string)
        logger.error(message)
        if r.status_code == 302:
            logger.error('Upload error: The 302 status code probably is a '
                         'redirect after a failed authentication')
    else:
        logger.debug('Response:\n' + r.content)
        logger.info('Done.')


def is_valid_data_file(parser, path):
    '''Validate the file input on the command line'''
    if not os.path.exists(path):
        parser.error('The file "%s" does not exist!' % path)
        return

    with open(path, 'r') as f:
        return f.read()


def update_contributions():
    # Parse the command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--config',
        default='contributions.cfg',
        help='Configuration file',)
    argparser.add_argument(
        '--upload',
        metavar='path/to/contributions.xxx.json',
        help=('Only upload the data from the specified file. (Even if '
              'you give further command line arguments!)'),
        type=lambda path: is_valid_data_file(argparser, path))
    argparser.add_argument(
        '--fetch-only',
        help='Only collect the data. Do not upload it to plone',
        action='store_true')
    argparser.add_argument(
        '--fetch-specific',
        nargs='+',
        choices=ALL_FETCHES,
        default=ALL_FETCHES,
        help='Collect only given specific parts. Do not upload it to plone',)
    argparser.add_argument(
        '--debug',
        action='store_true',
        help='Print debug output')
    argparser.add_argument(
        '--debug-limit',
        type=int,
        help='Limit the number of users/obj fetched for debugging')

    args = argparser.parse_args()

    # Parse the config file
    base_dir = find_base(args.config)
    config = SafeConfigParser()
    config.read(os.path.join(base_dir, args.config))

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.debug_limit:
        global debug_limit
        debug_limit = args.debug_limit
        logger.info(
            'Limit the number of fetched object per task to %s' %
            debug_limit
        )

    # upload the data from the given file
    if args.upload:
        upload(config, args.upload)
        logger.info('Uploaded the file and stop now.')
        exit(0)

    # fetch and upload or fetch-only
    json_data = fetch(config, args)
    if not args.fetch_only:
        upload(config, json_data)


if __name__ == '__main__':
    update_contributions()
