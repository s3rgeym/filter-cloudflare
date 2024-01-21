# filter-cloudflare
filter hosts on cloudflare

* no dependency instead python >= 3.9

Usage:

```bash
> python filter-cloudflare.py -H www.goodfirms.co
skip download: resource https://www.cloudflare.com/ips-v4/ is not modified
skip download: resource https://www.cloudflare.com/ips-v6/ is not modified
total hosts: 1; working processes: 1
check www.goodfirms.co (188.114.98.224) in coludflare subnet 173.245.48.0/20: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 103.21.244.0/22: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 103.22.200.0/22: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 103.31.4.0/22: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 141.101.64.0/18: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 108.162.192.0/18: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 190.93.240.0/20: PASS
check www.goodfirms.co (188.114.98.224) in coludflare subnet 188.114.96.0/20: FAIL
detected cloudflare: www.goodfirms.co
skip host: www.goodfirms.co
Finished!
```
