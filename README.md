# KikGroupScraper
A simple bot for scraping user data from Kik groups that uses PostgreSQL with Tomer8007's Kik Bot API. Just add the bot to groups and db will update, keep in mind users with PMs off give AJID not JID. (Haven't figured out how to resolve those yet 🤔)

Update .env file with BOT_EMAIL, BOT_PASSWORD, DATABASE_URL, PGDATABASE, PGHOST, PGPORT, PGUSER, and PGPASSWORD, also be sure to install kik-unofficial and psycopg2.
You can add the bot manually, but it's best used with a group joining botnet that adds your bot to counter group join limits. Discord in bio if you need that.
