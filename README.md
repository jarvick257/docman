# docman ![Build Status](https://github.com/jarvick257/docman/actions/workflows/client.yml/badge.svg?branch=develop)
Docman - a scriptable, git inspired document management system featuring document tags, full text search and a web-based front end for searching the database.

# TODO
## Client Side
- [ ] docman diff: show difference between working state and server
- [X] docman pull: download specific files directly
- [ ] docman stash: save/load working state locally
- [X] docman rm: delete documents on server
- [X] docman mode: edit meta elements only without down-/uploading files
- [ ] unit tests

## Server Side
- [ ] housekeeping: clean up orphaned documents (and all thumbs?) periodically (eg once a day) or at service start
- [ ] periodic backups: sync documents with remote server periodically
- [ ] unit tests
- [ ] https and client authentification

