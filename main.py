import sys
import os
import psycopg2
from psycopg2 import OperationalError
from kik_unofficial.client import KikClient
from kik_unofficial.datatypes.xmpp.chat_elements import TextMessage, Group
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, Roster
from kik_unofficial.callbacks import KikClientCallback

BOT_EMAIL = os.environ["BOT_EMAIL"]
BOT_PASSWORD = os.environ["BOT_PASSWORD"]
DATABASE_URL = os.environ["DATABASE_URL"]
PGDATABASE = os.environ["PGDATABASE"]
PGHOST = os.environ["PGHOST"]
PGPORT = os.environ["PGPORT"]
PGUSER = os.environ["PGUSER"]
PGPASSWORD = os.environ["PGPASSWORD"]

class GroupInfoBot(KikClient, KikClientCallback):
    def __init__(self):
        KikClient.__init__(self, callback=self)
        try:
            self.connection = psycopg2.connect(
                dbname=PGDATABASE,
                host=PGHOST,
                port=PGPORT,
                user=PGUSER,
                password=PGPASSWORD
            )
            self.create_user_table()
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

    def create_user_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        jid TEXT PRIMARY KEY,
                        username TEXT,
                        display_name TEXT,
                        alias_jid TEXT,
                        profile_pic_url TEXT
                    )
                """)
                self.connection.commit()
        except Exception as e:
            print(f"Error creating the user table: {e}")
            sys.exit(1)

    def on_authenticated(self):
        print("Bot is authenticated and ready to receive messages.")

    def on_captcha_challenge(self, url: str):
        print(f"CAPTCHA challenge encountered during login. Please solve it manually by visiting the following URL: {url}")
        sys.exit(1)

    def on_group_status_received(self, group_status):
        try:
            self.request_info_of_users(group_status.group.users)
        except Exception as e:
            print(f"Error requesting user info: {e}")

    def on_roster_received(self, response: FetchRosterResponse):
        group_jid = None
        try:
            with self.connection.cursor() as cursor:
                for entry in response.entries:
                    if isinstance(entry, Roster):
                        cursor.execute("""
                            INSERT INTO users (jid, username, display_name, alias_jid, profile_pic_url)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (jid) DO UPDATE
                            SET username = EXCLUDED.username,
                                display_name = EXCLUDED.display_name,
                                alias_jid = EXCLUDED.alias_jid,
                                profile_pic_url = EXCLUDED.profile_pic_url;
                        """, (entry.jid, entry.username, entry.display_name, entry.alias_jid, entry.pic_url))
                        if entry.group:
                            group_jid = entry.group.jid
                self.connection.commit()
        except Exception as e:
            print(f"Error updating the user table: {e}")
        finally:
            if group_jid:
                self.leave_group(group_jid)

if __name__ == "__main__":
    bot = GroupInfoBot()
    try:
        bot.authenticate(BOT_EMAIL, BOT_PASSWORD)
        bot.run_async()
    except Exception as e:
        print(f"Error during bot authentication or execution: {e}")
        sys.exit(1)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        bot.connection.close()
        sys.exit()

