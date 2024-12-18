# ets-ogcapi-tiles10-docker

[![Docker Pulls](https://badgen.net/docker/pulls/pdok/ets-ogcapi-tiles10-docker?icon=docker&label=pulls)](https://hub.docker.com/r/pdok/ets-ogcapi-tiles10-docker/)

PDOK Docker image for [OGC API - Tiles Compliance Test Suite](https://github.com/opengeospatial/ets-ogcapi-tiles10) for command-line use, with additional features:

- pass service url as command-line argument
- when passing `-exitOnFail` flag, return code `0` if test suite passes all tests, otherwise `1` (instead of always returning `0`)

## Usage examples

```bash
docker run -t -v "$(pwd):/mnt" pdok/ets-ogcapi-tiles10-docker:latest https://api.pdok.nl/lv/bag/ogc/v1/ --generateHtmlReport true --outputDir /mnt/output --exitOnFail --prettyPrint
```

```bash
URL=https://api.pdok.nl/lv/bag/ogc/v1/
cat > ./test-run-props.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties version="1.0">
  <comment>Test run arguments</comment>
  <entry key="iut">${URL}</entry>
  <entry key="tilematrixsetdefinitionuri">http://www.opengis.net/def/tilematrixset/OGC/1.0/WebMercatorQuad</entry>
  <entry key="urltemplatefortiles">${URL}/tiles/WebMercatorQuad/{tileMatrix}/{tileRow}/{tileCol}?f=mvt</entry>
  <entry key="tilematrix">17</entry>
  <entry key="mintilerow">67500</entry>
  <entry key="maxtilerow">67510</entry>
  <entry key="mintilecol">43200</entry>
  <entry key="maxtilecol">43210</entry>
</properties>
EOF
docker run -v "$(pwd):/mnt" pdok/ets-ogcapi-tiles10-docker:latest /mnt/test-run-props.xml --generateHtmlReport true --outputDir /mnt/output
```
