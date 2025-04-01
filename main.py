import pathlib
from fasthtml.common import *
from fasthtml.js import HighlightJS
from fh_bootstrap import bst_hdrs, Container, Image, Icon, ContainerT
import frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.anchors import anchors_plugin
import yaml
from collections import defaultdict

fa_cfurl = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0"
headers = (
    Link(href=f"{fa_cfurl}/css/all.min.css", rel="stylesheet"),
    Link(
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
        rel="stylesheet",
        type="text/css",
    ),
    StyleX("assets/styles.css"),
    Script(src="https://unpkg.com/htmx.org@next/dist/htmx.min.js"),
    *HighlightJS(
        langs=["python", "html", "yaml", "bash", "sh", "powershell", "dockerfile"], light="a11y-light", dark="a11y-dark"
    ),
    Favicon("/assets/favicon.ico", "/assets/favicon.ico"),
    Meta(name="viewport", content="width=device-width, initial-scale=1, viewport-fit=cover"),
    Meta(charset="utf-8"),
)


async def not_found(request, exc):
    return get_base((H2("404 - Not Found"), P("Return to ", A("home", href="/"))))


exception_handlers = {404: not_found}

app = FastHTML(hdrs=bst_hdrs + headers, live=False, default_hdrs=False, exception_handlers=exception_handlers)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/posts/img", StaticFiles(directory="posts/img"), name="posts_img")


def get_base(content):
    return (
        Title("Florian Brand"),
        Container(
            Nav(
                Div(
                    A("Home", href="/", cls="nav-link"),
                    A("Posts", href="/posts", cls="nav-link"),
                    A("Papers", href="/papers", cls="nav-link"),
                    cls="nav-links",
                ),
                cls="navbar",
            ),
            Div(
                Image(
                    "/assets/profile_picture.jpeg",
                    alt="Florian Brand",
                    cls="profile-image",
                ),
                Div(
                    H1("Florian Brand"),
                    P("Trier University | DFKI"),
                    Div(
                        Icon("fas fa-rss fa-sm", href="/feeds/atom.xml", button=False),
                        Icon("fab fa-bluesky fa-sm", href="https://bsky.app/profile/florianbrand.de", button=False),
                        Icon("fab fa-github fa-sm", href="https://www.github.com/xceron", button=False),
                        Icon(
                            "fab fa-linkedin fa-sm",
                            href="https://www.linkedin.com/in/florianbrand-de/",
                            button=False,
                        ),
                        Icon("fas fa-at fa-sm", href="mailto:privat@florianbrand.de", button=False),
                        cls="social-icons",
                    ),
                    cls="profile-info",
                ),
                cls="profile",
            ),
            Div(
                content,
                cls="content",
            ),
            typ=ContainerT.Sm,
        ),
    )


def Markdown(s):
    md = (
        MarkdownIt("commonmark")
        .enable("table")
        .use(anchors_plugin, min_level=2, permalink=True, permalinkSymbol="#", permalinkBefore=True)
        .use(footnote_plugin)
        .use(front_matter_plugin)
    )
    return Div(NotStr(md.render(s)))


@app.get("/")
def home():
    with open("main.md", "r") as file:
        content = file.read()
    return get_base(
        (
            *Socials(
                title="Florian Brand",
                description="Florian Brand's personal website",
                site_name="florianbrand.de",
                twitter_site="@xceron_",
                image="",
            ),
            H2("About"),
            Markdown(content),
        )
    )


@app.get("/feeds/atom.xml")
def atom_feed():
    return FileResponse("feeds/atom.xml")


@app.get("/posts/")
def posts():
    blog_dir = pathlib.Path("posts")
    blog_files = [file.stem for file in blog_dir.glob("*.md")]
    links = []
    for file in blog_files:
        with open(f"posts/{file}.md", "r", encoding="utf-8") as post_file:
            content = frontmatter.load(post_file)
            if "draft" in content and not content["draft"]:
                links.append(
                    Li(
                        Span(content["date"], cls="post-date"),
                        Span(A(content["title"], href=f"/posts/{file}"), cls="post-link"),
                        cls="post-list-item",
                    )
                )
    links = sorted(links, key=lambda x: x[0][0], reverse=True)
    return get_base(
        (
            *Socials(
                title="Florian Brand - Posts",
                description="Florian Brand's posts",
                site_name="florianbrand.de",
                twitter_site="@xceron_",
                image="",
            ),
            Div(H2("Posts"), Ul(*links, cls="post-list")),
        )
    )


PAPER_DATA_FILE = "data/papers.yaml"


def load_papers():
    """Loads paper data from the YAML file."""
    try:
        with open(PAPER_DATA_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"Warning: {PAPER_DATA_FILE} not found. Papers section will be empty.")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing {PAPER_DATA_FILE}: {e}")
        return []


@app.get("/papers/")
def papers():
    all_papers = load_papers()
    if not all_papers:
        return get_base(
            (
                *Socials(
                    title="Florian Brand - Papers",
                    description="Florian Brand's papers",
                    site_name="florianbrand.de",
                    twitter_site="@xceron_",
                    image="",
                ),
                H2("Papers"),
                P("No papers found or data file could not be loaded."),
            )
        )

    # Group papers by year
    papers_by_year = defaultdict(list)
    for paper in all_papers:
        papers_by_year[paper.get("year", "Unknown")].append(paper)

    # Sort years descending
    sorted_years = sorted(papers_by_year.keys(), reverse=True)

    content_items = [H2("Papers")]
    for year in sorted_years:
        content_items.append(H3(str(year)))
        year_papers = papers_by_year[year]
        list_items = []
        for paper in year_papers:
            title = paper.get("title", "No Title")
            pdf_url = paper.get("pdf_url")
            citation_key = paper.get("citation_key")
            has_bibtex = "bibtex" in paper and paper["bibtex"] is not None

            links = []
            if pdf_url:
                links.append(Span("[", A("PDF", href=pdf_url), "]"))

            if citation_key and has_bibtex:
                citation_id = f"citation-{citation_key}"
                bibtex_content = paper.get("bibtex", "")
                links.append(
                    Span(
                        "[",
                        A(
                            "BibTeX",
                            href="#",
                            onclick=f"toggleCitation(this, '{citation_id}'); return false;",
                        ),
                        "]",
                    )
                )
                citation_div = Div(Pre(Code(bibtex_content)), id=citation_id, style="display: none;")
            else:
                citation_div = ""

            list_items.append(Li(title, Br(), *links, citation_div))
        content_items.append(Ul(*list_items))

    # Add the script specifically for this page
    toggle_script = Script("""
function toggleCitation(linkElement, citationDivId) {
    const citationDiv = document.getElementById(citationDivId);
    if (!citationDiv) return;

    if (citationDiv.style.display === 'none' || citationDiv.style.display === '') {
        citationDiv.style.display = 'block'; // Or 'inline-block' or remove style
        linkElement.textContent = 'Hide BibTeX';
    } else {
        citationDiv.style.display = 'none';
        linkElement.textContent = 'BibTeX';
    }
}
""")

    return get_base(
        (
            *Socials(
                title="Florian Brand - Papers",
                description="Florian Brand's papers",
                site_name="florianbrand.de",
                image="",
            ),
            Div(*content_items),
            toggle_script, # Add script to the page content
        )
    )


@app.get("/posts/{post}")
def get_post(post: str):
    post_path = pathlib.Path(f"posts/{post}.md")
    if not post_path.exists():
        return RedirectResponse(url="/")
    md_file = frontmatter.load(post_path)
    return get_base(
        (
            *Socials(
                title=md_file["title"],
                description=md_file["summary"],
                site_name="florianbrand.de",
                twitter_site="@xceron_",
                image=md_file["image"] if "image" in md_file else "",
            ),
            Markdown(md_file.content),
        )
    )


if __name__ == "__main__":
    serve(host="0.0.0.0", port=5001)
