# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageColor
from random import choice
import cStringIO
import logging
import pytz

from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from ploneorg.core import HOMEPAGE_ID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

PROFILE_ID = 'profile-ploneorg.core:default'
logger = logging.getLogger("ploneorg.core")


def richify(string):
    """
    :param string: HTML string
    :return: RichTextValue
    """
    return RichTextValue(
        raw=string,
        mimeType='text/html',
        outputMimeType='text/html',
    )


def create_lead_image(size=(800, 450), color="blue"):
    """
    Creates an memory object containing an image.
    Expects a size tuple and PIL color.

    :param size: tuple of ints (width, height) default (800, 450)
    :param color: String or PIL color (r,g,b) tuple.
    :return: NamedBlobImage
    """
    # Create an image.
    im = Image.new("RGB", size, color=color)

    # Draw some lines
    draw = ImageDraw.Draw(im)
    color = ImageColor.getrgb(color)
    for i in range(9):
        factor = choice(range(8, 18, 1)) / 10.0
        stroke_color = (
            int(min(color[0] * factor, 255)),
            int(min(color[1] * factor, 255)),
            int(min(color[2] * factor, 255)),
        )
        draw.line(
            [
                (choice(range(0, size[0])), choice(range(0, size[1]))),
                (choice(range(0, size[0])), choice(range(0, size[1])))
            ],
            fill=stroke_color,
            width=int(size[1] / 5)
        )

    # 'Save' the file.
    sio = cStringIO.StringIO()
    im.save(sio, format="PNG")
    sio.seek(0)

    # Create named blob image
    nbi = NamedBlobImage()
    nbi.data = sio.read()
    nbi.filename = u"example.png"

    return nbi


def create_folder(portal, uid, title):
    folder = api.content.create(
        container=portal,
        type='Folder',
        id=uid,
        title=title,
    )
    portal.portal_workflow.doActionFor(folder, 'publish')
    logger.info('Created folder: %s', title)
    return folder


def create_folders(portal):
    items = [
        ('getting-started', 'Getting started'),
        ('community', 'Community'),
        ('foundation', 'Foundation'),
        ('related-websites', 'Related websites'),
    ]
    for (uid, title) in items:
        obj = getattr(portal, uid, False)
        if not obj:  # Only create folder if it doesn't exist.
            create_folder(portal, uid, title)


def create_links(portal):
    """
    :param portal: The current portal
    :return: None
    """
    # Do not create links if there are links in the portal.
    catalog = getToolByName(portal, 'portal_catalog')
    if len(catalog.searchResults({'portal_type': 'site_link'})):
        logger.info("There are existing links. Skipping link creation.")
        return

    items = [
        (
            "plone.com",
            "http://plone.com",
            """Overview of Plone and it's features.
               It is the online Plone brochure.""",
            True,
        ),
        (
            "docs.plone.org",
            "http://docs.plone.org",
            """Community-maintained manual for the Plone content
               management system.""",
            True,
        ),
        (
            "community.plone.org",
            "http://community.plone.org",
            """Nec dubitamus multa iter quae et nos invenerat. Etiam
               illo tempore, ab est sed immemorabili. Tu quoque, Brute.""",
            True,
        ),
        (
            "training.plone.org",
            "http://trainig.plone.org",
            """Quam diu etiam furor iste tuus nos eludet? Morbi odio eros,
               volutpat ut pharetra vitae, lobortis sed nibh.""",
            False,
        ),
    ]

    for title, url, description, display_in_top_bar in items:
        obj = api.content.create(
            container=portal['related-websites'],
            type='site_link',
            title=title,
            remoteUrl=url,
            description=description,
            display_in_top_bar=display_in_top_bar
        )
        portal.portal_workflow.doActionFor(obj, 'publish')
        logger.info('Created link: %s', title)


def create_events(portal):
    """
    Creates events only if there are no events in the portal.

    :param portal: the Plone portal
    :return: None
    """

    # Do not create events if there are events in the portal.
    catalog = getToolByName(portal, 'portal_catalog')
    if len(catalog.searchResults({'portal_type': 'Event'})):
        logger.info("There are existing events. Skipping event creation.")
        return

    now = datetime.now().replace(tzinfo=pytz.UTC)
    events = [
        (
            "Yesterday all my troubles",
            "yesterday",
            (now - timedelta(days=1)),
            "ForgetItTown",
        ),
        (
            "Today Smashing Pumpkins",
            "today",
            now,
            "TodayCity",
        ),
        (
            "Tomorrow never comes",
            "tomorrow",
            now + timedelta(days=1),
            "TomorrowLand"
        ),
        (
            "Sun is shining and so are you!",
            "next_month",
            now + timedelta(days=30),
            "NextMonthCity",
        ),
    ]

    for title, slug, start, location in events:
        event = createContentInContainer(
            portal.events,
            'Event',
            id=slug,
            title=title,
            start=start,
            end=start + timedelta(hours=1),
            whole_day=True,
            location=location,
        )
        logger.info("Created event: {}".format(title))
        portal.portal_workflow.doActionFor(event, 'publish')


def create_news(portal):
    """
    Creates news only if there are no news items in the portal.

    :param portal: the Plone portal
    :return: None
    """
    # Do not create news if there are news items in the portal.
    catalog = getToolByName(portal, 'portal_catalog')
    if len(catalog.searchResults({'portal_type': 'News Item'})):
        logger.info("There are existing news items. Skipping news creation.")
        return

    news_items = [
        (
            u"Plone Conference Boston 2016",
            u"plone-conference-boston-2016",
            (datetime.now() - timedelta(days=1)).replace(tzinfo=pytz.UTC),
            u"""
                We are pleased to announce that the 2016 Plone conference
                will be in Boston, October 17-23, 2016!
            """,
            richify(
                u"""
                <p>We are pleased to announce that the 2016 Plone conference
                will be in Boston, October 17-23, 2016!</p>
                """
            ),
            create_lead_image(color="#184d72"),
        ),
        (
            u"2015 Plone Conference Summary",
            u"2015-plone-conference-summary",
            (datetime.now() - timedelta(days=2)).replace(tzinfo=pytz.UTC),
            u"""
                The 13th annual Plone Conference, hosted by Eau de Web in
                Bucharest, Romania, was a smashing success! The theme was
                "Plone 5: Built with Passion" to highlight the September
                release of Plone 5. There were close to 200 attendees, 40+
                presentations, 3 hours of lightning talks, a sprint for the
                upcoming new Plone.org, and a lot of sprints around Plone 5
                and popular add-ons.
            """,
            richify(
                u"""
                    <p>The 13th annual Plone Conference, hosted by Eau de
                    Web in Bucharest, Romania, was a smashing success! The
                    theme was "Plone 5: Built with Passion" to highlight the
                    September release of Plone 5.</p> <p>There were close to
                    200 attendees, 40+ presentations, 3 hours of lightning
                    talks, a sprint for the upcoming new Plone.org, and a
                    lot of sprints around Plone 5 and popular add-ons.</p>
                    <p>The official Plone Conference photos are available on
                    Google+. Videos are still being processed and will be
                    posted next week. Sign up for the Plone Newsletter to
                    get all of the videos, photos, and slides delivered
                    right to you.</p>
                """
            ),
            create_lead_image(color="#184d72"),
        ),
        (
            u"Plone Foundation Board Elects Officers for 2015-2016",
            u"plone-foundation-board-elects-officers-for-2015-2016",
            (datetime.now() - timedelta(days=3)).replace(tzinfo=pytz.UTC),
            u"""
                Meet your new Plone Foundation officers: Paul Roeland has
                been named President, Carol Ganz Vice-President, Chrissy
                Wainwright Secretary and Jen Myers Treasurer. Hi omnes
                lingua, institutis, legibus inter se differunt.
            """,
            richify(
                u"""
                    <p>The Plone Foundation Board of Directors held their
                    first meeting on Thursday, October 29, 2015, and
                    selected officers for the upcoming year. The officers
                    are elected annually.</p>
                """
            ),
            create_lead_image(color="#184d72"),
        ),
        (
            u"Munich Plone 5 Sprint and Party",
            u"munich-plone-5-sprint-and-party",
            (datetime.now() - timedelta(days=4)).replace(tzinfo=pytz.UTC),
            u"""
                Come to our sprint September 16 through September 20, 2015 in
                Munich, Germany. Celebrate the Plone 5 release with a special
                party on September 16.
            """,
            richify(
                u"""
                    <p>The sprint will focus on documenting and improving the
                    different approaches used to implement designs for Plone 5.
                    </p>
                """
            ),
            create_lead_image(color="#184d72"),
        ),
        (
            u"Plone 5 Revealed: Modern, Powerful, and User-driven",
            u"plone-5-revealed-modern-powerful-and-user-driven",
            (datetime.now() - timedelta(days=5)).replace(tzinfo=pytz.UTC),
            u"""
                The Plone community has again raised the bar in the Content
                Management System market with today’s release of Plone 5.
                Plone 5 is fifteen years of stability wrapped in a modern,
                powerful user-centric package. It continues to set the pace
                for content management systems by offering the most
                functionality and customization out of the box.
            """,
            richify(
                u"""
                    <p>Plone 5’s new default theme, Barceloneta, is
                    responsive out the box to work with the full range of
                    mobile devices and is written using HTML5 and CSS3.</p>
                """
            ),
            create_lead_image(color="#184d72"),
        ),
    ]

    for title, slug, date, description, text, image in news_items:
        obj = createContentInContainer(
            portal.news,
            'News Item',
            id=slug,
            title=title,
            description=description,
            date=date,
            text=text,
            image=image
        )
        logger.info("Created news item: %s", title)
        portal.portal_workflow.doActionFor(obj, 'publish')


def create_sponsors_page(portal):
    folder_id = "sponsors"
    page_id = "sponsor"

    folder = getattr(portal, folder_id, False)
    if folder:
        return folder

    create_folder(portal, folder_id, folder_id.capitalize())
    page = createContentInContainer(
        portal.sponsors,
        "Document",
        id=page_id,
        title=unicode(page_id.capitalize())
    )
    portal.portal_workflow.doActionFor(page, 'publish')
    logger.info("Created page: %s", page_id)
    portal.sponsors.setDefaultPage(page_id)
    return page


def create_homepage(portal, sponsors_page):

    def get_relation(obj):
        intids = getUtility(IIntIds)
        return RelationValue(intids.getId(obj))

    homepage_content = {
        'text': richify(
            u"""
                <p class="lead">We build and maintain Plone</p>
                <h1>The&nbsp;Ultimate Enterprise&nbsp;CMS</h1>
                <p>
                  <a class="btn btn-secondary btn-sm"
                     href="#"
                     role="button">
                    Getting started
                  </a>
                  <a class="btn btn-secondary btn-sm"
                     href="#"
                     role="button">
                    Meet the community
                  </a>
                  <a class="btn btn-secondary btn-sm"
                     href="#"
                     role="button">
                    Documentation
                  </a>
                </p>
            """
        ),
        'download_title': u'Get the latest Plone',
        'download_text': richify(
            u"""
                <p class="lead">
                    New responsive theming story, dexterity content
                    types by default and lots more exciting features!
                </p>
            """
        ),
        'download_button_text': u'Download Plone 5.3.2',
        'download_url': u'https://plone.org/download',
        'download_below_button_text': richify(
            u"""
            <p>
                <a href="#">New&nbsp;features</a> 
                <a href="#">Roadmap</a> 
                <a href="#">Older&nbsp;releases</a>
            </p>
            """
        ),
        'event_title': u"Upcoming events",
        'event_text': richify(
            u"""
                <p class="lead">
                    Something about sprints, userdays, conferences. Plura mihi
                    bona sunt, inclinet, amari petere vellent. At nos hinc
                    posthac, sitientis piros Afros.
                </p>
                <p>
                  <a href="#" class="btn btn-primary">
                    <i class="fa fa-chevron-circle-right"></i>
                    Add an event
                  </a>
                </p>
                <p>
                  <a href="#" class="btn btn-primary">
                    <i class="fa fa-chevron-circle-right"></i>
                    All events
                  </a>
                </p>
            """
        ),
        'event_page': get_relation(portal['events']),
        'community_title': u"""Community activity""",
        'community_text': richify(
            u"""
                <p class="lead">
                    Text that explains where those numbers are from.
                    Mention the period. E.g: The actvity in the past
                    seven days.
                </p>
            """
        ),
        'community_page': get_relation(portal['Members']),
        'stats_contributors': 1729,
        'stats_addons': 196,
        'stats_providers': 1,
        'stats_countries': 2,
        'stats_languages': 42,
        'stats_downloads': 3,
        'stats_new_issues': 4,
        'stats_commits': 5,
        'stats_blockers': 6,
        'stats_pull_requests': 7,
        'stats_needs_review': 8,
        'sponsor_title': u"Sponsors",
        'sponsor_text': richify(
            u"""
                <p class="lead">
                    Gallia est omnis divisa in partes tres, quarum. Morbi
                    odio eros, volutpat ut pharetra vitae, lobortis sed
                    nibh. Sed haec quis possit intrepidus aestimare tellus.
                </p>
                <p>
                    <a class="btn btn-primary" href="#">
                        <span class="fa fa-chevron-circle-right"></span>
                        Become a sponsor
                    </a>
                </p>
                <p>
                    <a class="btn btn-primary" href="#">
                        <span class="fa fa-chevron-circle-right"></span>
                        All sponsors
                    </a>
                </p>
            """
        ),
        'sponsor_page': get_relation(sponsors_page),
    }

    registry = getUtility(IRegistry)
    settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
    settings.icon_visibility = 'false'

    # Create homepage if not present
    homepage = getattr(portal, HOMEPAGE_ID, False)
    if not homepage:
        homepage = createContentInContainer(
            portal,
            "homepage",
            title=unicode(HOMEPAGE_ID.capitalize()),
            checkConstraints=False,
            **homepage_content
        )
        # TODO: We can't exclude home, can we?
        # homepage.exclude_from_nav = True
        portal.portal_workflow.doActionFor(homepage, 'publish')
        logger.info('Default homepage site setup successfully.')

    portal.setDefaultPage(HOMEPAGE_ID)


def delete_content(portal):
    items = [
        'front-page',
    ]
    for item in items:
        if item in portal:
            api.content.delete(portal[item])
            logger.info('Deleted item: %s', item)


def order_content(portal):
    items = [
        ('getting-started', 'Getting started'),
        ('community', 'Community'),
        ('foundation', 'Foundation'),
    ]
    items.reverse()
    for uid, title in items:
        obj = portal[uid]
        portal.moveObjectsToTop(obj.id)
        logger.info('%s is now on top.', title)


def setupVarious(context):
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('ploneorg.core_various.txt') is None:
        return

    portal = context.getSite()

    logger.info('Create content...')

    create_folders(portal)
    create_events(portal)
    create_news(portal)
    sponsors_page = create_sponsors_page(portal)
    create_homepage(portal, sponsors_page)
    create_links(portal)

    order_content(portal)

    delete_content(portal)
