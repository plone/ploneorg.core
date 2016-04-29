import re
import functools
import os
from distutils import version
from time import time

from launchpadlib.launchpad import Launchpad
from Products.Five import BrowserView
from plone.memoize import ram


@functools.total_ordering
class NumberedVersion(version.Version):
    """
    Taken from
    http://stackoverflow.com/questions/12255554/sort-versions-in-python

    A more flexible implementation of distutils.version.StrictVersion

    This implementation allows to specify:
    - an arbitrary number of version numbers:
        not only '1.2.3' , but also '1.2.3.4.5'
    - the separator between version numbers:
        '1-2-3' is allowed when '-' is specified as separator
    - an arbitrary ordering of pre-release tags:
        1.1alpha3 < 1.1beta2 < 1.1rc1 < 1.1
        when ["alpha", "beta", "rc"] is specified as pre-release tag list
    """

    def __init__(self, vstring=None, sep='.', prerel_tags=('a', 'b', 'rc')):
        version.Version.__init__(self)
            # super() is better here, but Version is an old-style class

        self.sep = sep
        self.prerel_tags = dict(zip(prerel_tags, xrange(len(prerel_tags))))
        self.version_re = self._compile_pattern(sep, self.prerel_tags.keys())
        self.sep_re = re.compile(re.escape(sep))

        if vstring:
            self.parse(vstring)


    _re_prerel_tag = 'rel_tag'
    _re_prerel_num = 'tag_num'

    def _compile_pattern(self, sep, prerel_tags):
        sep = re.escape(sep)
        tags = '|'.join(re.escape(tag) for tag in prerel_tags)

        if tags:
            release_re = '(?:(?P<{tn}>{tags})(?P<{nn}>\d+))?'\
                .format(tags=tags, tn=self._re_prerel_tag, nn=self._re_prerel_num)
        else:
            release_re = ''

        return re.compile(r'^(\d+)(?:{sep}(\d+))*{rel}$'\
            .format(sep=sep, rel=release_re))

    def parse(self, vstring):
        m = self.version_re.match(vstring)
        if not m:
            raise ValueError("invalid version number '{}'".format(vstring))

        tag = m.group(self._re_prerel_tag)
        tag_num = m.group(self._re_prerel_num)

        if tag is not None and tag_num is not None:
            self.prerelease = (tag, int(tag_num))
            vnum_string = vstring[:-(len(tag) + len(tag_num))]
        else:
            self.prerelease = None
            vnum_string = vstring

        self.version = tuple(map(int, self.sep_re.split(vnum_string)))


    def __repr__(self):
        return "{cls} ('{vstring}', '{sep}', {prerel_tags})"\
            .format(cls=self.__class__.__name__, vstring=str(self),
                sep=self.sep, prerel_tags = list(self.prerel_tags.keys()))

    def __str__(self):
        s = self.sep.join(map(str,self.version))
        if self.prerelease:
            return s + "{}{}".format(*self.prerelease)
        else:
            return s

    def __lt__(self, other):
        """
        Fails when  the separator is not the same or when the pre-release tags
        are not the same or do not respect the same order.
        """
        # TODO deal with trailing zeroes: e.g. "1.2.0" == "1.2"
        if self.prerel_tags != other.prerel_tags or self.sep != other.sep:
            raise ValueError("Unable to compare: instances have different"
                " structures")

        if self.version == other.version and self.prerelease is not None and\
                other.prerelease is not None:

            tag_index = self.prerel_tags[self.prerelease[0]]
            other_index = self.prerel_tags[other.prerelease[0]]
            if tag_index == other_index:
                return self.prerelease[1] < other.prerelease[1]

            return tag_index < other_index

        elif self.version == other.version:
            return self.prerelease is not None and other.prerelease is None

        return self.version < other.version

    def __eq__(self, other):
        tag_index = self.prerel_tags[self.prerelease[0]]
        other_index = other.prerel_tags[other.prerelease[0]]
        return self.prerel_tags == other.prerel_tags and self.sep == other.sep\
            and self.version == other.version and tag_index == other_index and\
                self.prerelease[1] == other.prerelease[1]


class LaunchpadReleases(BrowserView):

    @ram.cache(lambda *args: time() // (24 * 60 * 60))
    def releases(self):
        cache_dir = os.path.join(os.getcwd(), '.launchpadlib', 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        launchpad = Launchpad.login_anonymously('plone.org', 'production', cache_dir, version='devel')
        plone = launchpad.projects('plone')

        releases = [{'version': r.version,
                     'date': r.date_released,
                     'url': r.web_link,
                     'name': r.display_name} for r in plone.releases]
        releases = sorted(releases, key=lambda r: NumberedVersion(r['version']))
        releases.reverse()
        return releases

