__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


## ContributorCI Config Schema

schema_url = "https://json-schema.org/draft-07/schema/#"

unique_array = {"type": "array", "uniqueItems": True, "items": {"type": "string"}}
unique_array_or_null = {
    "oneOf": [
        {"type": "array", "uniqueItems": True, "items": {"type": "string"}},
        {"type": "null"},
    ]
}

configProperties = {
    "member_orgs": unique_array_or_null,
    "orgs": unique_array,
    "repos": unique_array,
    "exclude_repos": unique_array,
    "outdir": {"type": ["string", "null"]},
    "editor": {"type": ["string", "null"]},
}

config_schema = {
    "$schema": schema_url,
    "title": "Contributor CI Config Schema",
    "type": "object",
    "required": [
        "orgs",
        "member_orgs",
    ],
    "additionalProperties": True,
    "properties": configProperties,
}
