# Copyright 2016 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module provides apis to query server inventory
"""

import json
from imcsdk_ecoen66.imcexception import ImcOperationError

inventory_spec = {
    "cpu": {
        "class_id": "ProcessorUnit",
        "props": [
            {"prop": "dn"},
            {"prop": "id"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "arch"}]
    },
    "memory": {
        "class_id": "MemoryUnit",
        "ignore": [
            {"prop": "presence", "value": "missing"}
        ],
        "props": [
            {"prop": "dn"},
            {"prop": "id"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "serial"},
            {"prop": "capacity"},
            {"prop": "clock"},
            {"prop": "presence"}]
    },
    "psu": {
        "class_id": "EquipmentPsu",
        "ignore": [
            {"prop": "presence", "value": "missing"}
        ],
        "props": [
            {"prop": "id"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "serial"},
            {"prop": "fw_version"}]
    },
    "pci": {
        "class_id": "PciEquipSlot",
        "props": [
            {"label": "Server", "prop": "dn"},
            {"prop": "id"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "version"}]
    },
    "vic": {
        "class_id": "AdaptorUnit",
        "props": [
            {"label": "Server", "prop": "dn"},
            {"prop": "id"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "serial"},
            {"label": "PCI-slot", "prop": "pci_slot"}]
    },
    "lom": {
        "class_id": "NetworkAdapterUnit",
        "props": [
            {"prop": "model"},
            {"label": "PCI-Slot", "prop": "slot"},
            {"label": "Num-Interfaces", "prop": "num_intf"}],
    },
    "tpm": {
        "class_id": "EquipmentTpm",
        "props": [
            {"prop": "dn"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "serial"},
            {"label": "Revision", "prop": "tpm_revision"}]
    },
    "storage": {
        "class_id": "StorageController",
        "props": [
            {"label": "Server", "prop": "dn"},
            {"prop": "model"},
            {"prop": "vendor"},
            {"prop": "serial"},
            {"prop": "type"},
            {"label": "PCI-slot", "prop": "pci_slot"},
            {"label": "Firmware", "prop": "firmware_package_build", "class": "StorageControllerProps", "method": "query_children"}]
    },
    "disks": {
        "class_id": "StorageLocalDisk",
        "props": [
            {"prop": "id"},
            {"label": "Model", "prop": "product_id"},
            {"prop": "vendor"},
            {"label": "Serial Number", "prop": "drive_serial_number"},
            {"label": "PD Status", "prop": "pd_status"},
            {"prop": "health"},
            {"label": "Link Speed", "prop": "link_speed"},
            {"label": "Interface Type", "prop": "interface_type"},
            {"label": "Media Type", "prop": "media_type"},
            {"label": "Size", "prop": "coerced_size"},
            {"label": "Firmware", "prop": "drive_firmware"},
            {"label": "Drive State", "prop": "drive_state"},
            {"prop": "online"}
        ]
    },
    "vNICs": {
        "class_id": "AdaptorHostEthIf",
        "props": [
            {"prop": "dn"},
            {"prop": "name"},
            {"prop": "cdn"},
            {"prop": "mac"},
            {"prop": "mtu"},
            {"prop": "pxe_boot"},
            {"prop": "iscsi_boot"},
            {"prop": "usnic_count"},
            {"prop": "uplink_port"},
            {"prop": "class_of_service"},
            {"prop": "channel_number"},
            {"prop": "port_profile"}
        ]
    },
    "vHBAs": {
        "class_id": "AdaptorHostFcIf",
        "props": [
            {"prop": "dn"},
            {"prop": "name"},
            {"prop": "wwnn"},
            {"prop": "wwpn"},
            {"prop": "uplink_port"},
            {"prop": "san_boot"},
            {"prop": "channel_number"},
            {"prop": "port_profile"},
            {"prop": "admin_persistent_bindings"}
        ]
    }
}


def _sanitize_and_store(mo_dict, prop, mo):
    value = getattr(mo, prop, None)
    if value:
        value = value.strip()
    mo_dict[prop] = value


def _should_ignore(comp, obj):
    if "ignore" not in comp:
        return False

    for ig in comp["ignore"]:
        name, value = ig["prop"], ig["value"]
        if getattr(obj, name, None) == value:
            return True
    return False


def _check_and_create_key(ds, key, value={}):
    if key in ds:
        return
    ds[key] = value


def _get_inventory(handle, comp, spec, inventory):
    component = spec[comp]
    class_id = component["class_id"]
    mos = handle.query_classid(class_id)

    ip = handle.ip
    _check_and_create_key(ds=inventory, key=ip, value={})
    _check_and_create_key(ds=inventory[ip], key=comp, value=[])
    inv_comp = inventory[ip][comp]
    for mo in mos:
        mo_dict = {}
        for each in component["props"]:
            prop = each["prop"]
            class_id = each["class"] if "class" in each else None
            method = each["method"] if "method" in each else None

            if class_id:
                if method == "query_children":
                    sub_mos = handle.query_children(in_dn=mo.dn,
                                                    class_id=class_id)
                    sub_mo = sub_mos[0]

                if sub_mo:
                    if _should_ignore(component, sub_mo):
                        continue
                    _sanitize_and_store(mo_dict, prop, sub_mo)
            else:
                if _should_ignore(component, mo):
                    continue
                _sanitize_and_store(mo_dict, prop, mo)
        if len(mo_dict) > 0:
            inv_comp.append(mo_dict)


def _get_inventory_csv(inventory, file_name, spec=inventory_spec):
    import csv
    if file_name is None:
        raise ImcOperationError("Inventory collection",
                                "file_name is a required parameter")
    f = csv.writer(open(file_name, "w"))

    x = inventory
    for comp in spec:
        f.writerow([comp.upper()])
        props = spec[comp]["props"]
        keys = [y['prop'] for y in props]
        keys.insert(0, "Host")
        f.writerow(keys)

        for ip in x:
            if comp not in x[ip]:
                continue
            host_component = x[ip][comp]
            if len(host_component) == 0:
                continue
            for entry in host_component:
                row_val = []
                for key in keys:
                    if key not in entry:
                        continue
                    row_val.append(entry[key])
                row_val.insert(0, ip)
                f.writerow(row_val)

        f.writerow([])
        f.writerow([])


def _get_search_script():
    script = """
<script>
    function myFunction() {
    // Declare variables
    var input, filter, table, tr, td, i, j, tds, ths, matched;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    tr = document.getElementsByTagName("tr");

    // Loop through all table rows, and hide
    // those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        tds = tr[i].getElementsByTagName("td");
        ths = tr[i].getElementsByTagName("th");
        matched = false;
        if (ths.length > 0) {
            matched = true;
        }
        else {
            for (j = 0; j < tds.length; j++) {
                td = tds[j];
                if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                    matched = true;
                    break;
                }

            }
        }
        if (matched == true) {
            tr[i].style.display = "";
        }
        else {
            tr[i].style.display = "none";
        }
        }
    }
</script>
"""
    return script


def _get_inventory_html(inventory, file_name, spec=inventory_spec):
    if file_name is None:
        raise ImcOperationError("Inventory collection",
                                "file_name is a required parameter")
    f = open(file_name, "w")

    html = ""
    html += "<html>\n"

    html += "<head>\n"
    html += _get_search_script()
    html += "</head>\n"
    html += "<body>\n"
    html += """
    <br>
    <input type="text" id="searchInput" onkeyup="myFunction()" placeholder="Search..">
    </br>
    """

    x = inventory
    for comp in spec:
        html += '<table border="1">'
        html += "<br><br>" + comp.upper()

        props = spec[comp]["props"]
        keys = [y['prop'] for y in props]
        keys.insert(0, "Host")
        html += '<tr style="background-color: gainsboro;">'
        for key in keys:
            html += "<th>" + key + "</th>"
        html += '</tr>'

        for ip in x:
            if comp not in x[ip]:
                continue
            host_component = x[ip][comp]
            if len(host_component) == 0:
                continue
            for entry in host_component:
                row_val = []
                for key in keys:
                    if key not in entry:
                        continue
                    row_val.append(entry[key])
                row_val.insert(0, ip)
                html += "<tr>"
                for each in row_val:
                    if each is None:
                        each = ""
                    html += "<td>" + each + "</td>"
                html += "</tr>"

    html += "</table>\n"
    html += "</body>"
    html += "</html>"
    f.write(html)
    f.close()


def inventory_get(handle,
                  component="all",
                  file_format="json",
                  file_name=None,
                  spec=inventory_spec):
    """
    This method fetches the inventory of the server for various
    items like cpus, memory, psu or the entire server.

    Args:
        handle (ImcHandle or list of ImcHandle):
            Can consume a single handle or a list of handles
        types (string): comma separated values for the components
            "all" - will get inventory for all components
            For individual components use -
                "cpu, disk,  memory, psu, pci, vic, lom, storage, tpm"
        file_format (string): "json", "csv", "html"
        file_name (string): file name to save the data to.
        spec (dictionary): only for advanced usage

    Returns:
        json formatted inventory data. additionally data is also written to
        a file, if one is specified.
    """

    inventory = {}

    if isinstance(handle, list):
        servers = handle
    else:
        servers = [handle]

    for server in servers:
        components = component
        if not isinstance(component, list):
            components = [component]
        if "all" in components:
            for comp in spec.keys():
                _get_inventory(server, comp, spec, inventory)
        else:
            for comp in components:
                if comp not in spec:
                    raise ImcOperationError("Inventory Collection",
                                            ("Unsupported component type:" +
                                             str(component)))

                _get_inventory(server, comp, spec, inventory)

    if file_format == "csv":
        _get_inventory_csv(inventory=inventory, file_name=file_name, spec=spec)
    elif file_format == "html":
        _get_inventory_html(inventory=inventory, file_name=file_name, spec=spec)
    elif file_format == "json" and file_name:
        f = open(file_name, 'w')
        f.write(json.dumps(inventory))
        f.close()

    return inventory
