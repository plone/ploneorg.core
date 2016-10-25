=================
Content migration
=================

Plone Foundation
================

As usual, it will contain the information relevant of the Foundation and its
activity.

Other content
=============

It will have the information of the Foundation Members. The Plone related news
and events.


Content not to be migrated
==========================

The old documentation will be left in the legacy site, as it lives now in the
amazing docs.plone.org.

The Plone Software Center, products and addons information will be deprecated.
Look at paragon.plone.org for add-ons.

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


