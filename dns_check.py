import dns.resolver
def dns_check(domain):
    resolvers=[
        "8.8.8.8",
        "1.1.1.1",
        "208.67.222.222"
    ]
    for resolver_ip in resolvers:
        resolver=dns.resolver.Resolver()
        resolver.nameservers=[resolver_ip]
        resolver.lifetime=3
        try:
            result=resolver.resolve(domain,"A")
            ips=[ip.to_text() for ip in result]
            return{
                "status":True,
                "type":"A",
                "value":ips,
                "resolver":resolver_ip
            }
        except dns.resolver.NoAnswer:
            try:
                result=resolver.resolve(domain,"CNAME")
                cname=result[0].to_text()
                return {
                    "status":True,
                    "type":"CNAME",
                    "value":cname,
                    "resolver":resolver_ip
                }
            except Exception:
                continue
        except dns.resolver.NXDOMAIN:
            return {
                "status":False,
                "reason":"NXDOMAIN"
            }
        except dns.resolver.Timeout:
            continue
    return {
        "status":False,
        "reason":"All resolvers failed"
    }