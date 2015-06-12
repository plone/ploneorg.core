Introduction
============

This is the core policy package of the 2015 reboot of plone.org site project.

Other related packages:

 * ploneorg.theme


The project
===========

Vision
------

We initially planned the first release of the plone.org reboot should target
Plone 4.3.x, and we should ensure that the eventually migration to Plone 5 will
be as easy as possible.

Having this in mind, we will initially not make use of products or technologies
that will eventually need a migration or make use of non-core features. For
example, we decided not to use any of the existing page composition products out
there to ensure that point. Once plone.org will sport a fully stable Plone 5
there would be easy to add those kind of features.

So we will try to match the technologies used in plonetheme.barceloneta (mockup,
p.a.widgets) in ploneorg.theme as far as possible and other approaches as well.

The new plone.org theme are Bootstrap 3.x based, using LESS as a CSS
preprocessor. We are using bower to track any library/dependency in the theme.

Contributors profile
--------------------

This is the main focus of the relaunch of the site. The site should be centered
on the Plone project contributors: developers, collaborators and friends.

The site will sport a collaborator profile pages that will show all the
contributions and merits of each the individuals.

Plone Foundation
----------------

As usual, it will contain the information relevant of the Foundation and its
activity.

Other content
-------------

It will have the information of the Foundation Members. The Plone related news
and events too.

Content not to be migrated
--------------------------

The old documentation will be left in the legacy site, as it lives now in the
amazing docs.plone.org.

The PSC and products and addons information will be deprecated too in favor of a
more lightweight and usable catalog, probably hosted on paragon.plone.org.

Migration process
=================

The process works using a collective.transmogrifier pipeline on the import
side. The code is in:

https://github.com/collective/ploneorg.migration

The export part is performed via collective.jsonify-like views but due to it's
aimed to work on very old versions of Plone we didn't wanted to deal with all
the upstream process we decided to forked it and customize it for plone.org. You
can find it here:

https://github.com/collective/ploneorg.jsonify

Requirements
------------

We need a working buildout of the current Plone.org instance with a copy of
the production site:

https://github.com/plone/Products.PloneOrg

and we should add the ploneorg.jsonify egg to the list of required eggs and
mr.developer auto-checkout list. Then it will be ready for exporting content.

On the import side, we need a new plone.org buildout working and a brand
new instance. There are a view to trigger the migration:

@@ploneorg_migration_main

and the configuration of the pipeline lives in:
/src/ploneorg.migration/src/ploneorg/migration/browser/ploneorg.cfg

So basicaly you have to configure the [catalogsource] section accordingly by
informing the location of the source instance and the sections to be migrated,
for example:

    [catalogsource]
    blueprint = ploneorg.migration.catalogsource
    remote-url = http://localhost:8081
    remote-username = admin
    remote-password = admin
    remote-root = /plone.org
    catalog-path = /plone.org/portal_catalog
    catalog-query =
        {'path': {'query': '/plone.org/foundation'}}
    remote-skip-paths =
        /foundation/members

The migration should go smoothly, for the content in

/foundation
/news
/events

that are already tested.
