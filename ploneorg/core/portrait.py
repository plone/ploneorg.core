# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from OFS.Image import Image
from PIL import ImageOps
from Products.CMFCore.permissions import ManageUsers
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO

import PIL


def changeMemberPortrait(self, portrait, id=None):
    """update the portait of a member.

    We URL-quote the member id if needed.

    Note that this method might be called by an anonymous user who
    is getting registered.  This method will then be called from
    plone.app.users and this is fine.  When called from restricted
    python code or with a curl command by a hacker, the
    declareProtected line will kick in and prevent use of this
    method.
    """
    authenticated_id = self.getAuthenticatedMember().getId()
    if not id:
        id = authenticated_id
    safe_id = self._getSafeMemberId(id)

    # dexterity.membrane hand the current user id in unicode, but BTree can't
    # handle unicode keys in inner objects... *sigh*
    if isinstance(safe_id, unicode):
        safe_id = str(safe_id)

    valid_id = id == authenticated_id or id == authenticated_id + '_large'

    if authenticated_id and not valid_id:
        # Only Managers can change portraits of others.
        if not _checkPermission(ManageUsers, self):
            raise Unauthorized
    if portrait and portrait.filename:
        if not id.endswith('_large'):
            # Override default resizing
            scaled, mimetype = convertSquareImage(portrait)
        else:
            scaled, mimetype = adjust_large_image(portrait)

        portrait = Image(id=safe_id, file=scaled, title='')
        membertool = getToolByName(self, 'portal_memberdata')
        membertool._setPortrait(portrait, safe_id)


def convertSquareImage(image_file):
    CONVERT_SIZE = (250, 250)
    image = PIL.Image.open(image_file)
    format = image.format
    mimetype = 'image/%s' % format.lower()

    result = ImageOps.fit(
        image,
        CONVERT_SIZE,
        method=PIL.Image.ANTIALIAS,
        centering=(0, 0)
    )
    new_file = StringIO()
    result.save(new_file, format, quality=88)
    new_file.seek(0)

    return new_file, mimetype


def adjust_large_image(large_image):
    CONVERT_SIZE = (1200, 400)
    image = PIL.Image.open(large_image)
    format = image.format
    mimetype = 'image/%s' % format.lower()

    result = ImageOps.fit(
        image,
        CONVERT_SIZE,
        method=PIL.Image.ANTIALIAS,
        centering=(0, 0)
    )
    new_file = StringIO()
    result.save(new_file, format, quality=88)
    new_file.seek(0)

    return new_file, mimetype
