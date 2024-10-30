# Copyright 2024 Daniel Roy Greenfeld
# Copyright 2024 Florian Brand
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modified from original source: https://github.com/pydanny/daniel-blog-fasthtml/blob/main/feeds.py
# Changes made: Personal information, access to posts folder
from feedgen.feed import FeedGenerator
import frontmatter
import markdown
import pytz
from datetime import datetime
from pathlib import Path
from dateutil import parser


def convert_dtstr_to_dt(date_str):
    """
    Convert a naive or non-naive date/datetime string to a datetime object.
    Naive datetime strings are assumed to be in GMT (UTC) timezone.
    """
    try:
        dt = parser.parse(str(date_str))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt
    except (ValueError, TypeError) as e:
        print(f"Error parsing date string: {e}")
        return None


def filter_posts_by_category(posts: list[dict], category: str):
    """
    Generator function that filters posts by a single category.
    """
    for post in posts:
        post_categories = [x.lower() for x in post.get("categories", [])]
        if category.lower() in post_categories:
            yield post


def github_markdown_to_html(markdown_str):
    """Convert GitHub-flavored Markdown string to HTML."""
    html = markdown.markdown(markdown_str, extensions=["extra", "codehilite", "toc", "tables"])
    return html


def get_posts():
    """Get all published blog posts."""
    blog_dir = Path("posts")
    posts = []

    for file in blog_dir.glob("*.md"):
        with open(file, "r") as post_file:
            post = frontmatter.load(post_file)

            # Skip drafts
            if post.get("draft", False):
                continue

            # Add slug (filename without extension)
            post.metadata["slug"] = file.stem

            # Add the content
            post.metadata["content"] = post.content

            posts.append(post.metadata)

    # Sort posts by date, newest first
    return sorted(posts, key=lambda x: x.get("date", ""), reverse=True)


def add_entry(fg, post):
    """Add a single entry to the feed."""
    fe = fg.add_entry()
    url = f'https://florianbrand.de/posts/{post["slug"]}'
    fe.id(url)
    fe.link(href=url)
    fe.title(post.get("title", "Untitled"))
    fe.summary(post.get("summary", ""))
    fe.content(content=github_markdown_to_html(post["content"]), type="CDATA")

    author_info = {
        "name": "Florian Brand",
        "email": "privat@florianbrand.de",
    }
    fe.contributor([author_info])
    fe.author([author_info])

    if "date" in post:
        fe.pubDate(convert_dtstr_to_dt(post["date"]))

    # Add categories to the entry
    for category in post.get("categories", []):
        fe.category(term=category)


def build_feed(category: str | None = None):
    """Build the main feed or category-specific feed."""
    fg = FeedGenerator()

    # Basic feed settings - modify with your details
    fg.id("https://florianbrand.de")
    fg.title("Florian Brand - Blog")
    fg.author(
        {
            "name": "Florian Brand",
            "email": "privat@florianbrand.de",
            "uri": "https://florianbrand.de",
        }
    )
    fg.link(href="https://florianbrand.de", rel="alternate")
    fg.subtitle("Florian Brand")
    fg.language("en")
    fg.rights(f"All rights reserved {datetime.now().year}, Florian Brand")

    # Get all published posts
    posts = get_posts()

    # Filter by category if specified
    if category is not None:
        posts = list(filter_posts_by_category(posts, category))

    # Add the most recent posts (limit to 10)
    for post in posts[:10]:
        add_entry(fg, post)

    # Create the feeds directory if it doesn't exist
    Path("feeds").mkdir(exist_ok=True)

    # Generate the feed file
    if category is not None:
        fg.atom_file(f"feeds/{category}.atom.xml", pretty=True)
    else:
        fg.atom_file("feeds/atom.xml", pretty=True)


if __name__ == "__main__":
    import sys

    category = sys.argv[1] if len(sys.argv) > 1 else None
    build_feed(category)
