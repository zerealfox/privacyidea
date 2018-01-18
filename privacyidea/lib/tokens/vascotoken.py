# -*- coding: utf-8 -*-
#
#  License:  AGPLv3
#  contact:  http://www.privacyidea.org
#
#  2018-01-15   Friedrich Weber <friedrich.weber@netknights.it>
#               Initial version of the VASCO token
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import binascii

__doc__ = """This is the implementation of the VASCO token"""

import logging
from privacyidea.api.lib.utils import getParam
from privacyidea.lib.utils import is_true
from privacyidea.lib.decorators import check_token_locked
from privacyidea.lib.error import ParameterError
from privacyidea.lib.log import log_with
from privacyidea.lib.tokenclass import TokenClass
from privacyidea.lib.tokens.vasco import vasco_otp_check
from privacyidea.lib import _

optional = True
required = False

log = logging.getLogger(__name__)


class VascoTokenClass(TokenClass):
    """
    TODO
    """

    def __init__(self, db_token):
        """
        constructor - create a token class object with its db token binding

        :param aToken: the db bound token
        """
        TokenClass.__init__(self, db_token)
        self.set_type(u"vasco")
        self.hKeyRequired = True

    @staticmethod
    def get_class_type():
        """
        return the class type identifier
        """
        return "vasco"

    @staticmethod
    def get_class_prefix():
        """
        return the token type prefix
        """
        return "VASC"

    @staticmethod
    @log_with(log)
    def get_class_info(key=None, ret='all'):
        """
        :param key: subsection identifier
        :type key: string
        :param ret: default return value, if nothing is found
        :type ret: user defined
        :return: subsection if key exists or user defined
        :rtype: dict or string
        """
        res = {'type': 'vasco',
               'title': 'VASCO Token',
               'description': _('VASCO Token: Authentication using VASCO tokens'),
               'user': ["enroll"],
               'ui_enroll': ["admin", "user"],
               'policy': {},
               }

        if key:
            ret = res.get(key, {})
        else:
            if ret == 'all':
                ret = res
        return ret

    @log_with(log)
    def update(self, param, reset_failcount=True):
        """
        update - process initialization parameters

        :param param: dict of initialization parameters
        :type param: dict

        :return: nothing
        """
        if is_true(getParam(param, 'genkey', optional)):
            raise ParameterError("Generating OTP keys is not supported")

        upd_param = param.copy()

        # If the OTP key is given, it is given as a 496-character hex string which
        # encodes a 248-byte blob. As we want to set a 248-byte OTPKey (= Blob),
        # we unhexlify the OTP key
        if 'otpkey' in param:
            upd_param['otpkey'] = binascii.unhexlify(upd_param['otpkey'])

        TokenClass.update(self, upd_param, reset_failcount)

    @check_token_locked
    def check_otp(self, otpval, counter=None, window=None, options=None):
        secret = self.token.get_otpkey().getKey()
        result, new_secret = vasco_otp_check(secret, otpval)
        self.token.set_otpkey(new_secret)
        self.save()

        if result == 0:
            # Successful authentication
            return 0
        else:
            log.warning("VASCO token failed to authenticate, result: {!r}".format(result))
            return -1
