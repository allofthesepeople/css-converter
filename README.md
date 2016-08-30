## Introduction

### Overview

Deliver an importer/exporter which accepts product data in CSV format and
exports it as JSON, with the possible extension to further content types.

Currently provides an example


### Technical

It is built with python, using the flask framework and (as stated above) has a
single http POST endpoint, accepting `Content-Type: text/csv`. Optionally, the
service will attempt to honour the `Accept` header for the return format with
default of JSON.

e.g.
`curl -i -X POST http://localhost:4567/product -H "Content-Type: text/csv; Accept: application/json" --data-binary "./example.csv"`


### Caveats / Assumptions

There is no “uploading” of CSV files, instead using the request body to carry
the content. This assumes any uploading is handled by a separate service.

This implementation assumes CSV file sizes of reasonable size as the whole file
is sent in the request and loaded in memory. If larger files are required then
the file would need to be uploaded to some form of storage and read line by
line.


## Getting Started

### Running the application

The recommended way to get going with this app is to use docker.

Once docker is installed simple get going command is `make run`. This will
get the correct ruby image & install the required Gems before starting the app
on `localhost:5000` (this may vary on your docker setup; e.g. if running in a
VM then use the ip address of the VM)


## Extending

Individual CSV processors extend `processors.base_rocessor.BaseProcessor` and
an example processor is included.

Validation requires the `Content-Type` is `text/csv`. The body must exist and the first line must be the CSV headers.

To add further processors, simply provide the processor and direct the first url
segment to the lowercase name of the processor.

Three class (list) variables exist to aid extendibility:

- `header_adj`: rename any headers in output format (nested field require dot
    notation)
- `nested_fields`: field prefixes which should be nested (currently only 1
    level deep allowed)
- `required_fields`: any fields which must be present.

Further modifications and validation can happen per-field by writing a method
to perform the required action. Top level fields follow the convention
`fld__<property_name>` while nested properties follow the convention
`fld__<top_level_property_name>__<nested_property_name>`.


## Testing

Run tests with `make test`
