#!/bin/sh

cat <<EOF
{
    "lb": {
        "children": [],
        "hosts": [
            "f4-test1"
        ],
        "vars": {}
    },
    "lbha": {
        "children": [],
        "hosts": [
            "f4-test2"
        ],
        "vars": {}
    },
    "all": {
        "vars": {
            "klantnaam": "test_klant",
            "user": "admin",
            "password": "vergeten",
            "validate_certs": "no",
            "partition": "foo",
            "nlc": "1234",
            "vlan": "100",
            "tagged_interfaces": "1.1",
            "ipprefix": "10.10.10",
            "ha": "no"
        }
    }
}
EOF
