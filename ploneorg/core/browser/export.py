# -*- coding: UTF-8 -*-
from collective.exportimport.export_content import ExportContent
from collective.exportimport.export_other import BaseExport
from collective.exportimport.interfaces import IPathBlobsMarker
from collective.exportimport.serializer import FileFieldSerializerWithBlobs
from plone import api
from plone.app.vulnerabilities.field import IChecksummedFileField
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer

import logging

logger = logging.getLogger(__name__)


TYPES_TO_MIGRATE = [
    "Collection",
    "Document",
    "Event",
    "File",
    "Folder",
    "Image",
    "Link",
    "News Item",
    "FoundationMember",
    "FoundationSponsor",
    "hotfix",
    "plonerelease",
    "vulnerability",
]

# These are made folderish by plone.volto
FOLDERISH_TYPES = [
    "Document",
    "Event",
    "News Item",
    "Folder",
]


class ExportAll(BrowserView):

    template = ViewPageTemplateFile('export_all.pt')

    def __call__(self):
        request = self.request
        if not request.form.get("form.submitted", False):
            return self.template()

        portal = api.portal.get()

        export_name = "export_content"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        exported_types = TYPES_TO_MIGRATE
        request.form["form.submitted"] = True
        view(portal_type=exported_types, include_blobs=2, download_to_server=True)
        logger.info("Finished {}".format(export_name))

        other_exports = [
            "export_relations",
            "export_members",
            # "export_translations",
            "export_localroles",
            "export_ordering",
            "export_defaultpages",
            "export_discussion",
            "export_portlets",
            "export_redirects",
            "export_zope_users",
        ]
        for export_name in other_exports:
            export_view = api.content.get_view(export_name, portal, request)
            request.form["form.submitted"] = True
            # store each result in var/instance/export_xxx.json
            export_view(download_to_server=True)

        logger.info("Finished export_all")
        # Important! Redirect to prevent infinite export loop :)
        return self.request.response.redirect(self.context.absolute_url())

class PloneOrgExportContent(ExportContent):

    QUERY = {
    }

    DROP_PATHS = [
        "ploneorg/Members",
    ]

    DROP_UIDS = [
    ]

    def update_query(self, query):
        query['portal_type'] = self.portal_type or TYPES_TO_MIGRATE
        return query

    def update(self):
        self.portal_type = self.portal_type or TYPES_TO_MIGRATE

    def global_obj_hook(self, obj):
        """Used this to inspect the content item before serialisation data.
        Bad: Changing the content-item is a bad idea.
        Good: Return None if you want to skip this particular object.
        """
        if obj.language not in ["en", ""]:
            obj.language = "en"
        return obj

    def global_dict_hook(self, item, obj):
        """Used this to modify the serialized data.
        Return None if you want to skip this particular object.
        """
        return item

class ExportZopeUsers(BaseExport):

    AUTO_ROLES = ["Authenticated"]

    def __call__(self, download_to_server=False):
        self.title = "Export Zope users"
        self.download_to_server = download_to_server
        portal = api.portal.get()
        app = portal.__parent__
        self.acl = app.acl_users
        self.pms = api.portal.get_tool("portal_membership")
        data = self.all_zope_users()
        self.download(data)

    def all_zope_users(self):
        results = []
        for user in self.acl.searchUsers():
            data = self._getUserData(user["userid"])
            data['title'] = user['title']
            results.append(data)
        return results

    def _getUserData(self, userId):
        member = self.pms.getMemberById(userId)
        roles = [
            role
            for role in member.getRoles()
            if role not in self.AUTO_ROLES
        ]
        # userid, password, roles
        props = {
            "username": userId,
            "password": json_compatible(self._getUserPassword(userId)),
            "roles": json_compatible(roles),
        }
        return props

    def _getUserPassword(self, userId):
        users = self.acl.users
        passwords = users._user_passwords
        password = passwords.get(userId, "")
        return password


@adapter(IChecksummedFileField, IDexterityContent, IPathBlobsMarker)
@implementer(IFieldSerializer)
class ChecksummedFileFieldSerializer(FileFieldSerializerWithBlobs):
    """ChecksummedFileField has no blob duh, so there's no blob_path...
    So we use he default FileFieldSerializerWithBlobs with base64 encoding.
    """
