<i>This app is built in Anvil and you can [read more about that here](https://github.com/agsheves/daily-news-summary/blob/a437b772428e4b7efbdf6eef95239643171f7bf7/anvilInfo.md)</i>

<h2>Purpose</h2>

To set up a way to automatically get risk, crisis, and disaster news stories and automatically format and share these online and by email.

<h2>Elements</h2>

- API calls to several different news APIs to get the raw data
- ChatGTP to summarize the stories.
- An Anvil app to display the stories
- Anvil's email service
- Integration with a webpage

<H2>Notes</H2>

The biggest challenge has been the consistency of the data from the news APIs and having sufficient credits to test the app before deciding on a service. Some services also performed well for short periods before deteriorating.

<H2>Next steps</H2>

- [ ] Settle on a 'good enough' API and clean up the code to use this.
- [ ] Finish the web app to display the stories
- [ ] Publish the webapp HTML and embed on a webpage as a test
- [ ] Link to the raw stories to another service to integrate with a newsletter. This could be auto-posting to WordPress to send news out via the ConvertKit RSS feed.

<h2>Other uses</h2>

The same set up could be used to publish a newsletter on any topic and share it in different formats.

