from github import Github
from github.ContentFile import ContentFile
from github import Auth
from datetime import datetime
import re
import sqlite3
import os

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()

auth = Auth.Token(os.environ["GH_TOKEN"])
g = Github(auth=auth)


for repo in g.get_user().get_repos():
    if 'game' in repo.topics and 'portfolio' in repo.topics:
        repo_url = repo.html_url if not repo.private else ''

        cart_image_box = repo.get_contents("cart.png")
        cart_image_url = cart_image_box.download_url if isinstance(cart_image_box, ContentFile) else ''
        
        readme_box = repo.get_contents("README.md")
        readme = readme_box.decoded_content.decode("utf-8") if isinstance(readme_box, ContentFile) else ''
        
        title_match = re.search(r'^[^#]*#\W*(.+)', readme)
        title: str = title_match.group(1) if title_match else ''
        
        pub_match = re.search(r'Published on (January|February|March|April|May|June|July|August|September|October|November|December) (\d\d), (\d\d\d\d)', readme)
        pub_month: str = pub_match.group(1) if pub_match else ''
        pub_day: str = pub_match.group(2) if pub_match else ''
        pub_year: str = pub_match.group(3) if pub_match else ''
        
        # create datetime string based on format string 'YYYY-MM-DD'
        pub_date = f'{pub_year}-{datetime.strptime(pub_month, "%B").month:02d}-{pub_day.zfill(2)}'

        _ = cur.executemany("""--sql
            INSERT INTO games 
            (title, cart_img, repo_url, pub_date) 
            VALUES (?, ?, ?, ?)
        """, [(title, cart_image_url, repo_url, pub_date)])
        con.commit()


g.close()
cur.close()