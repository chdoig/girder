#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2015 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import constants
from quota import QuotaPolicy, ValidateSizeQuota
from girder import events
from girder.models.model_base import ValidationException


def validateSettings(event):
    key, val = event.info['key'], event.info['value']

    if key in (constants.PluginSettings.QUOTA_DEFAULT_USER_QUOTA,
               constants.PluginSettings.QUOTA_DEFAULT_COLLECTION_QUOTA):
        (val, err) = ValidateSizeQuota(val)
        if err:
            raise ValidationException(err, 'value')
        event.info['value'] = val
        event.preventDefault().stopPropagation()


def load(info):
    quota = QuotaPolicy()
    info['apiRoot'].collection.route('GET', (':id', 'quota'),
                                     quota.getCollectionQuota)
    info['apiRoot'].collection.route('PUT', (':id', 'quota'),
                                     quota.setCollectionQuota)
    info['apiRoot'].user.route('GET', (':id', 'quota'), quota.getUserQuota)
    info['apiRoot'].user.route('PUT', (':id', 'quota'), quota.setUserQuota)
    events.bind('model.setting.validate', 'userQuota', validateSettings)
    events.bind('model.upload.assetstore', 'userQuota',
                quota.getUploadAssetstore)
    events.bind('model.upload.save', 'userQuota', quota.checkUploadStart)
    events.bind('model.upload.finalize', 'userQuota',
                quota.checkUploadFinalize)
