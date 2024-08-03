import pathlib
from fasthtml.common import (
    Link,
    FastHTML,
    Nav,
    A,
    Div,
    serve,
    H2,
    H1,
    P,
    StyleX,
    Ul,
    NotStr,
    Li,
    RedirectResponse,
    StaticFiles,
    Socials,
    Title
)
from fh_bootstrap import bst_hdrs, Container, Image, Icon, ContainerT
from markdown import markdown
import frontmatter

headers = (
    Link(
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
        rel="stylesheet",
        type="text/css",
    ),
    StyleX("assets/styles.css"),
    *Socials(title="Florian Brand", description="Florian Brands Personal Site", site_name="florianbrand.de",
             twitter_site="@xceron_", image="", url=""),
)


async def not_found(request, exc):
    return RedirectResponse(url="/")


exception_handlers = {
    404: not_found
}

app = FastHTML(hdrs=bst_hdrs + headers, live=False, exception_handlers=exception_handlers)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


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
                    P("Uni Trier | DFKI"),
                    Div(
                        Icon("fab fa-x-twitter fa-sm", href="www.twitter.com/xceron_", button=False),
                        Icon("fab fa-github fa-sm", href="www.github.com/xceron", button=False),
                        Icon("fab fa-linkedin fa-sm", href="https://www.linkedin.com/in/florian-brand-b046b622b/",
                             button=False),
                        Icon("fab fa-discord fa-sm", href="https://discord.com/users/1233745701243195433",
                             button=False),
                        Icon("fas fa-at fa-sm", href="mailto:hello@florianbrand.de", button=False),
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
        )
    )


md_exts = ('codehilite', 'smarty', 'extra', 'sane_lists')


def Markdown(s, exts=md_exts, **kw):
    # https://github.com/AnswerDotAI/fh-about/blob/7e5109c26ba2f4fcba897cc83add6ee74621ed20/app.py#L6
    return Div(NotStr(markdown(s, extensions=exts)), **kw)


@app.get("/")
def home():
    with open('main.md', 'r') as file:
        content = file.read()
    return get_base(Markdown(content))


@app.get("/posts/")
def posts():
    blog_dir = pathlib.Path("posts")
    blog_files = [file.stem for file in blog_dir.glob("*.md")]
    links = []
    for file in blog_files:
        with open(f"posts/{file}.md", 'r') as post_file:
            content = frontmatter.load(post_file)
            if not content["draft"]:
                links.append(Li(content["date"], A(content["title"], href=f"/posts/{file}")))
    return get_base(Div(H2("Posts"), Ul(*links)))


@app.get("/papers/")
def papers():
    return get_base(H1("Papers"))


@app.get("/posts/{post}")
def get_post(post: str):
    post_path = pathlib.Path(f"posts/{post}.md")
    if not post_path.exists():
        return RedirectResponse(url="/")
    md_file = frontmatter.load(post_path)
    if md_file["draft"]:
        return RedirectResponse(url="/")
    return get_base(Markdown(md_file.content))


if __name__ == "__main__":
    serve(host="0.0.0.0", port=5001)
