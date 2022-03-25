# -*- coding: UTF-8 -*-
from Acquisition import aq_base
from App.config import getConfiguration
from collective.exportimport.export_content import ExportContent
from collective.exportimport.export_content import fix_portal_type
from collective.exportimport.export_other import safe_bytes
from collective.exportimport.interfaces import IPathBlobsMarker
from collective.exportimport.serializer import FileFieldSerializerWithBlobs
from plone import api
from plone.app.vulnerabilities.field import IChecksummedFileField
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer

import json
import logging
import os
import six

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

        # Also store data from all other exports in var/instance/...
        directory = getConfiguration().clienthome

        export_name = "export_relations"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        view.debug = False
        data = view.get_all_references()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_members"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        view.pms = api.portal.get_tool("portal_membership")
        data = {}
        data["groups"] = view.export_groups()
        data["members"] = [i for i in view.export_members()]
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_localroles"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        data = view.all_localroles()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_ordering"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        data = view.all_orders()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_defaultpages"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        data = view.all_default_pages()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_portlets"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        data = view.all_portlets()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        export_name = "export_zope_users"
        logger.info("Start {}".format(export_name))
        view = api.content.get_view(export_name, portal, request)
        view.acl = api.portal.get().__parent__.acl_users
        view.pms = api.portal.get_tool("portal_membership")
        data = view.all_zope_users()
        filepath = os.path.join(directory, "{}.json".format(export_name))
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        logger.info("Finished {}".format(export_name))

        # Important! Redirect to prevent infinite export loop by overriding the redirect :)
        logger.info("Finished export_all")
        return self.request.response.redirect(self.context.absolute_url())


class PloneOrgExportContent(ExportContent):

    QUERY = {
    }

    DROP_PATHS = [
    ]

    DROP_UIDS = [
    ]

    def update_query(self, query):
        query['portal_type'] = self.portal_type or TYPES_TO_MIGRATE
        return query

    def update(self):
        self.transformed_default_pages = []
        self.portal_type = self.portal_type or TYPES_TO_MIGRATE

    def global_obj_hook(self, obj):
        """Used this to inspect the content item before serialisation data.
        Bad: Changing the content-item is a bad idea.
        Good: Return None if you want to skip this particular object.
        """
        return obj

    def global_dict_hook(self, item, obj):
        """Used this to modify the serialized data.
        Return None if you want to skip this particular object.
        """
        # this item is already exported to replace its container in dict_hook_folder
        if item["UID"] in self.transformed_default_pages:
            return
        return item

    def dict_hook_folder(self, item, obj):
        # handle default pages
        default_page = obj.getDefaultPage()
        if not default_page:
            # has no default-page, we keep it as a folder
            return item

        dp_obj = obj.get(default_page)
        dp_obj = self.global_obj_hook(dp_obj)
        if not dp_obj:
            return

        if dp_obj.portal_type not in FOLDERISH_TYPES:
            # keep the old Folder for non-folderish content (Link)
            return item

        self.safe_portal_type = fix_portal_type(dp_obj.portal_type)
        serializer = getMultiAdapter((dp_obj, self.request), ISerializeToJson)
        dp_item = serializer(include_items=False)
        dp_item = self.fix_url(dp_item, dp_obj)
        dp_item = self.export_constraints(dp_item, dp_obj)
        dp_item = self.export_workflow_history(dp_item, dp_obj)
        if self.migration:
            dp_item = self.update_data_for_migration(dp_item, dp_obj)
        dp_item = self.global_dict_hook(dp_item, dp_obj)
        if not dp_item:
            logger.info(u"Skipping {}".format(dp_obj.absolute_url()))
            return obj
        dp_item = self.custom_dict_hook(dp_item, dp_obj)
        if dp_item["@type"] != "Document":
            logger.info(u"Default page is type {} for {}: {}".format(dp_item["@type"], item["@id"], dp_obj.absolute_url()))

        dp_item["parent"] = item["parent"]
        dp_item["@id"] = item["@id"]
        dp_item["id"] = item["id"]
        dp_item["is_folderish"] = True
        # prevent importing the default page obj again
        self.transformed_default_pages.append(dp_item["UID"])
        return dp_item

    def dict_hook_collection(self, item, obj):
        item.pop("items", None)
        return item


class ExportZopeUsers(BrowserView):

    AUTO_ROLES = ["Authenticated"]

    def __call__(self):
        portal = api.portal.get()
        app = portal.__parent__
        self.acl = app.acl_users
        self.pms = api.portal.get_tool("portal_membership")
        results = self.all_zope_users()
        data = json.dumps(results, indent=4)
        filename = "zope_users.json"
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader("content-length", len(data))
        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="{0}"'.format(filename)
        )
        return self.request.response.write(safe_bytes(data))

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
            "password": self._getUserPassword(userId),
            "roles": json_compatible(roles),
        }
        return props

    def _getUserPassword(self, userId):
        users = self.acl.users
        passwords = users._user_passwords
        password = passwords.get(userId, "")
        if six.PY3 and isinstance(password, bytes):
            # bytes are not json serializable.
            # Happens at least in the tests.
            password = password.decode("utf-8")
        return password


@adapter(IChecksummedFileField, IDexterityContent, IPathBlobsMarker)
@implementer(IFieldSerializer)
class ChecksummedFileFieldSerializer(FileFieldSerializerWithBlobs):
    """ChecksummedFileField has no blob duh, so there's no blob_path...
    So we use he default FileFieldSerializerWithBlobs with base64 encoding.
    """
