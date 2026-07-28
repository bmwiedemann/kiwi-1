# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import os
import uuid
import random
import logging
from functools import reduce

log = logging.getLogger('kiwi')


def generate_seed_uuid(name: str, random_bits: int = 128) -> str:
    """
    Create UUID. If SOURCE_DATE_EPOCH is present use
    SOURCE_DATE_EPOCH + name as seed

    The name makes the result unique per caller, such that the
    filesystems and partitions of one image do not all end up
    with the same identifier.

    :param str name: seed name, e.g a filesystem label
    :param int random_bits: number of bits to draw

    :return: UUID string

    :rtype: str
    """
    sde = os.environ.get('SOURCE_DATE_EPOCH')
    if sde:
        name_seed = reduce(lambda x, y: x + y, map(ord, name))
        epoch_seed = name_seed + int(sde)
        log.info(
            'Using UUID seed SOURCE_DATE_EPOCH:{0} + NAME:{1}={2}'.format(
                sde, name, name_seed
            )
        )
        rd = random.Random()
        rd.seed(epoch_seed)
        return format(
            uuid.UUID(int=rd.getrandbits(random_bits))
        )
    else:
        return format(uuid.uuid4())
