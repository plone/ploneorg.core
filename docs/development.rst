===========
Development
===========

What to do to get a development setup up and running.

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

So basically you have to configure the [catalogsource] section accordingly by
informing the location of the source instance and the sections to be migrated,
for example:

.. code-block:: ini
   
    [catalogsource]
    blueprint = ploneorg.migration.catalogsource
    remote-url = http://localhost:8081
    remote-username = admin
    remote-password = admin
    remote-root = /plone.org
    catalog-path = /plone.org/portal_catalog
    catalog-query = {'path': {'query': '/plone.org/foundation'}}
    remote-skip-paths = /foundation/members

The migration should go smoothly, for the content in:

.. code-block:: shell

    /foundation
    /news
    /events

that are already tested.
 
