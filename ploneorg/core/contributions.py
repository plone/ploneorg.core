# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
from datetime import datetime
from github import Github
from github import UnknownObjectException

import argparse
import json
import logging
import os
import requests

logging.basicConfig()
logger = logging.getLogger('contributions')

debug_limit = None


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
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, User):
            return str(obj.contributions)

        return super(JSONEncoder, self).default(obj)


def find_base():
    path = os.getcwd()
    while path:
        if os.path.exists(os.path.join(path, 'contributions.cfg')):
            break
        old_path = path
        path = os.path.dirname(path)
        if old_path == path:
            path = None
            break
    if path is None:
        raise IOError('contributions.cfg not found')
    return path


def check_debug_limit(iterable, type_):
    if debug_limit:
        logger.info('Debug limit for %s: %s' % (type_, debug_limit))
        return iterable[:debug_limit]
    return iterable


def find_data_dir(config):
    '''Calculate the data dir and make sure it exists'''
    base = find_base()
    data_dir = os.path.abspath(
        os.path.join(base, config.get('general', 'datadir')))
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def get_auth(config):
    admin_user = config.get('general', 'admin_user')
    admin_password = config.get('general', 'admin_password')
    return requests.auth.HTTPBasicAuth(admin_user, admin_password)


def write_data(config, json_string):
    '''Write the data do a json file.'''
    data_dir = find_data_dir(config)
    isodate = datetime.now().isoformat()
    filename = 'contributions.%s.json' % isodate
    path = os.path.join(data_dir, filename)
    with open(path, 'w') as f:
        f.write(json_string)
    logger.info('Wrote data to %s' % filename)


def fetch(config):
    data = {'github': {},
            'stackoverflow': None}

    try:
        data['github']['plone'] = fetch_github(config, 'plone')
        data['github']['collective'] = fetch_github(config, 'collective')
        data['stackoverflow'] = fetch_stackoverflow(config)
    except IOError:
        logger.exception('An IOError happend, probably a read timeout')
        exit(1)
    json_string = json.dumps(data, cls=JSONEncoder, sort_keys=True, indent=4)
    write_data(config, json_string)
    return json_string


def fetch_github(config, organization):

    logger.info('Fetch data from github for "%s"...' % organization)
    token = config.get('github', 'token')
    g = Github(token)

    logger.debug('... get organization data')
    organization = g.get_organization(organization)

    start_limit = current_limit = g.rate_limiting[0]

    contributions = {}
    data = {
        'rate_limits': {
            'doc': 'Track github api request rate limits. Just in case',
            'start': start_limit,
            'expense': {},
            'end': None},
        'contributions': contributions,
        'unknown': []}

    repos = check_debug_limit(organization.get_repos(), 'repos')

    for repo in repos:
        try:
            logger.debug('... get contributors for %s' % repo.name)
            contributors = repo.get_contributors()
            for contributor in contributors:
                login = contributor.login
                user = contributions.setdefault(login, User(login))
                user.add_contributions(repo.name, contributor.contributions)
        except UnknownObjectException:
            # empty repository
            logger.debug('... repository "%s" seems to be empty' % repo.name)
            data['unknown'].append(repo.name)

        # Track # of requests used for the repo
        new_limit = g.rate_limiting[0]
        data['rate_limits']['expense'][repo.name] = current_limit - new_limit
        current_limit = new_limit

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
    for member_id in plone_member_ids:
        stackoverflow_id = stackoverflow_users[member_id]
        activity = _so_activity_for_user(stackoverflow_id, member_id)
        stackoverflow_users[member_id] = activity

    logger.info('Done.')
    return stackoverflow_users


def _so_activity_for_user(userid, member_id):
    # FIXME: something better is needed here.
    # FIXME: ask for top answerers last month also?
    logger.debug('...plone member: %s, so userid: %s' % (member_id, userid))
    from random import choice
    return choice([0, 0, 0, 0, 0, 5, 8, 11, 14, 18, 21])


def upload(config, json_string):
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
    # Parse the config and the command line arguments
    base_dir = find_base()
    config = SafeConfigParser()
    config.read(os.path.join(base_dir, 'contributions.cfg'))

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--upload', metavar='path/to/contributions.xxx.json',
        help=('Only upload the data from the specified file. (Even if '
              'you give further command line arguments!)'),
        type=lambda path: is_valid_data_file(argparser, path))
    argparser.add_argument(
        '--fetch-only',
        help='Only collect the data. Do not upload it to plone',
        action='store_true')
    argparser.add_argument(
        '--debug', action='store_true', help='Print debug output')
    argparser.add_argument(
        '--debug-limit', type=int,
        help='Limit the number of users/obj fetched for debugging')
    args = argparser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.debug_limit:
        global debug_limit
        debug_limit = args.debug_limit
        logger.info('Limit the number of fetched object per task to %s' %
                    debug_limit)

    # upload the data from the given file
    if args.upload:
        upload(config, args.upload)
        logger.info('Uploaded the file and stop now.')
        exit(0)

    # fetch and upload or fetch-only
    json_data = fetch(config)
    if not args.fetch_only:
        upload(config, json_data)


if __name__ == '__main__':
    update_contributions()
