def match_jobs_with_connections(jobs, connections):
    matches = []
    for conn in connections:
        for job in jobs:
            if any(word.lower() in conn["occupation"].lower() for word in job["title"].lower().split()):
                matches.append({
                    "connection": conn,
                    "job": job
                })
    return matches