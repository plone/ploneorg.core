=======================
Stats retriever process
=======================

There is a helper script that lives in the *bin* folder called
**update_contributions**. It has the follow arguments::

    usage: update_contributions [-h] [--config CONFIG]
                                [--upload path/to/contributions.xxx.json]
                                [--fetch-only]
                                [--fetch-specific {issues,contributions,commits,stackoverflow,pypi,twitter} [{issues,contributions,commits,stackoverflow,pypi,twitter} ...]]
                                [--debug] [--debug-limit DEBUG_LIMIT]

    optional arguments:
     -h, --help            show this help message and exit
     --config CONFIG       Configuration file
     --upload path/to/contributions.xxx.json
                            Only upload the data from the specified file. (Even if
                            you give further command line arguments!)
     --fetch-only          Only collect the data. Do not upload it to plone
     --fetch-specific {issues,contributions,commits,stackoverflow,pypi,twitter} [{issues,contributions,commits,stackoverflow,pypi,twitter} ...]
                            Collect only given specific parts. Do not upload it to Plone

There is a modificator in the script that allows you to push the data from a
file and other that limits the numbre of users/repos fetched which are quite
useful for debugging.

You should provide a configuration file that should match the one in the
contributions.cfg.in. Make a copy and modify its values as needed. You will need
a valid personal Github token (or a developer application one). You can get one
here::

    https://github.com/settings/tokens

The configuration look like this::

     [general]
    plone_url = http://localhost:8080/ploneorg/
    datadir = ./var/contributor_data
    admin_user = admin
    admin_password = admin
    plone_package = Products.CMFPlone

    [github]
    token = <here should be the Github token>

    # days
    newissues_delta = 1

    # weeks
    commits_delta = 1

    # space spearated list of labels to be considered as blockers
    blocker_labels = blocker critical

Make sure that all the values matches de ones in your site.

note::

        At the moment only the Github, Pypi, Stackoverflow and Twitter stats are available.

Stats receiver view
-------------------

The site has a view **update-contributor-data** that has the job of update all
the data structures with the recently retrieved data.

