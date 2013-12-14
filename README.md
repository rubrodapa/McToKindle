README
======

McToKindle is a small program that search for the latest chapters of comics from McAnime.net, downloads them and
sends them by email using Gmail smtp to the kindle cloud.

It parses the web html to search the chapters that are specified in the configuration file.

Requirements
============
- Python 2.7
- [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) module.
- [Kindle Comic Converter](https://github.com/ciromattia/kcc) in a folder called kcc.
- [Kindlegen](http://www.amazon.com/gp/feature.html?docId=1000765211) executable in your path.
