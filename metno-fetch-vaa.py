#!/usr/bin/env python

import HTMLParser, os, sys, urllib2, urlparse

default_url = "http://www.meteo.fr/vaac/evaa.html"

class Parser(HTMLParser.HTMLParser):

    def __init__(self):
    
        HTMLParser.HTMLParser.__init__(self)
        self.href = ""
        self.text = ""
    
    def feed(self, data):

        self.anchors = []
        HTMLParser.HTMLParser.feed(self, data)
    
    def handle_starttag(self, tag, attrs):
    
        if tag == "a":
            d = dict(attrs)
            try:
                self.href = d["href"]
            except KeyError:
                pass
            self.text = ""

    def handle_data(self, data):
    
        if self.href:
            self.text += data
    
    def handle_endtag(self, tag):

        if tag == "a":
            self.anchors.append((self.href, self.text))
            self.href = ""


if __name__ == "__main__":

    if not 2 <= len(sys.argv) <= 3:

        sys.stderr.write("Usage: %s [URL of page containing links to VAA messages] <download directory>\n" % sys.argv[0])
        sys.exit(1)
    
    download_dir = sys.argv[-1]

    if not os.path.isdir(download_dir):
        try:
            os.mkdir(download_dir)
        except OSError:
            sys.stderr.write("Failed to create the download directory: %s\n" % download_dir)
            sys.exit(1)
    
    if len(sys.argv) == 2:
        url = raw_input("URL [%s]: " % default_url)
        if not url.strip():
            url = default_url
    else:
        url = sys.argv[1]
    
    html = urllib2.urlopen(url).read()
    p = Parser()
    p.feed(html)
    p.close()
    
    count = 0
    for href, text in p.anchors:
        if text.endswith("UTC"):
            vaa_url = urlparse.urljoin(url, href)
            print "Fetching", vaa_url
            vaa_html = urllib2.urlopen(vaa_url).read()
            vaa_file = os.path.join(download_dir, href.split("/")[-1])
            open(vaa_file, "w").write(vaa_html)

            os.system("./parseash.pl " + vaa_file)
            count += 1
            if count == 10:
                break
    
    sys.exit()
