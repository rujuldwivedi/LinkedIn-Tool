def send_messages(matched):
    for match in matched:
        conn = match["connection"]
        job = match["job"]

        print(f"\nTo: {conn['name']} | {conn['occupation']}")
        print(f"📎 Matched Job: {job['title']} at {job['company']}")
        print(f"🔗 Job Link: {job['job_link']}")
        message = f"""
Hi {conn['name']},

I came across a position at {job['company']} that I'm really interested in:
{job['job_link']}

Since you’re connected with the company, I was wondering if you’d be open to referring me?

Thank you so much!
"""
        print(f"\n📨 Message:\n{message}")
        input("Send message? (Press Enter to continue, or type 'exit' to quit): ")