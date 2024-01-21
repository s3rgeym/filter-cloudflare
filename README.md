# filter-cloudflare
filter hosts on cloudflare

* no dependency instead python >= 3.9

Usage:

```bash
$ python filter-cloudflare.py -l hosts.txt > non-clodf.txt
```

56% domains does not use cloudflare (realy?):

```bash
> echo "$(wc -l non-cloud.txt | cut -d ' ' -f1)/$(wc -l data/eu-startups.txt | cut -d ' ' -f1)"|bc -l
.56234496944763748563
```

