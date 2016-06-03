import httpagentparser


def parse(ua):
    agent_summary = {}
    parsed = httpagentparser.detect(ua)

    for attr in ("browser", "os", "platform"):
        d = parsed.get(attr)
        if d:
            for subattr in ("name", "version"):
                if subattr in d:
                    key = "%s_%s" % (attr, subattr)
                    agent_summary[key] = d[subattr]

    agent_summary["bot"] = parsed.get("bot")
    dist = parsed.get("dist")

    if dist:
        agent_summary["sub-platform"] = dist.get("name")

    return agent_summary
