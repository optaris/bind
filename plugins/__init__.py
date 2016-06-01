"""
    Copyright 2016 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

import os
import datetime
import hashlib

from inmanta.plugins import plugin, Context

@plugin
def nameservers(master_zones: "list", slave_zones: "list" = []) -> "list":
    """
        Returns a list of all the name servers in ns records in the list of zones
    """
    zones = set(list(master_zones) + list(slave_zones))
    record_list = set([record.server for zone in zones for record in zone.records if record.record_type.lower() == "ns"])
    return list()


@plugin
def serial(context: Context, zone: "string", zonefile: "string") -> "string":
    """ This plugin will check if the zonefile has been updated since the last compile. If the zone
        is update it will replace __SERIAL__ with the current UTC timestamp. If the zonefile has
        not been updated, it will use the previous serial.

        :param zone: The name of the zone to check
        :param zonefile: The actual zone file. This is a complete and valid zonefile with __SERIAL__
                         in it as placeholder. This placeholder is replaced with the current
                         serial.
    """
    data_dir = context.get_data_dir()
    serial_file = os.path.join(data_dir, "serials.txt")

    serials = {}
    if os.path.exists(serial_file):
        with open(serial_file, "r") as fd:
            for line in fd.readlines():
                cols = line.strip().split(" ")
                if len(cols) == 3:
                    serials[cols[0]] = (cols[1], cols[2])

    md5sum = hashlib.md5(zonefile.encode("utf-8")).hexdigest()

    serial = 0
    old_sum = ""
    if zone in serials:
        old_sum = serials[zone][0]
        serial = serials[zone][1]

    if old_sum != md5sum: # this happens in case of a new file and updated file
        serial = datetime.datetime.utcnow().strftime("%s")
        serials[zone] = (md5sum, serial)

    # store serials
    with open(serial_file, "w+") as fd:
        for k,v in serials.items():
            fd.write("%s %s %s\n" % (k, v[0], v[1]))

    return zonefile.replace("__SERIAL__", serial)

