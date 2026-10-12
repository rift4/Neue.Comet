// A content hash of docs/lab/ and its scripts, used to bust their caches.
// The value is filled in by misc/tools/build-site.py, which hashes the file
// itself; it is a literal here because with Jekyll gone the lab is served as
// plain static files and nothing else would ever update it.
const interBuildVersion = "f4c1fb76"
