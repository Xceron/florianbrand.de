import pathlib
from fasthtml.common import *
from fh_bootstrap import bst_hdrs, Container, Image, Icon, ContainerT
import frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.anchors import anchors_plugin

headers = (
    Link(
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
        rel="stylesheet",
        type="text/css",
    ),
    StyleX("assets/styles.css"),
    *Socials(title="Florian Brand", description="Florian Brands Personal Site", site_name="florianbrand.de",
             twitter_site="@xceron_", image="", url=""),
    Meta(name="viewport", content="width=device-width, initial-scale=1, viewport-fit=cover"),
    Meta(charset="utf-8"),
)


async def not_found(request, exc):
    return get_base((H2("404 - Not Found"),
                     P("Return to ", A("home", href="/"))))


exception_handlers = {
    404: not_found
}

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
                        Icon("fab fa-x-twitter fa-sm", href="https://www.twitter.com/xceron_", button=False),
                        Icon("fab fa-github fa-sm", href="https://www.github.com/xceron", button=False),
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


def Markdown(s):
    md = (
        MarkdownIt("commonmark")
        .use(anchors_plugin, min_level=2, permalink=True, permalinkSymbol="#", permalinkBefore=True)
        .use(footnote_plugin)
        .use(front_matter_plugin)
    )
    return Div(NotStr(md.render(s)))


@app.get("/")
def home():
    with open('main.md', 'r') as file:
        content = file.read()
    return get_base((H2("About"), Markdown(content)))


@app.get("/posts/")
def posts():
    blog_dir = pathlib.Path("posts")
    blog_files = [file.stem for file in blog_dir.glob("*.md")]
    links = []
    for file in blog_files:
        with open(f"posts/{file}.md", "r") as post_file:
            content = frontmatter.load(post_file)
            if not content["draft"]:
                links.append(Li(content["date"], A(content["title"], href=f"/posts/{file}")))
    return get_base(Div(H2("Posts"), Ul(*links)))


@app.get("/papers/")
def papers():
    return get_base(
        (H2("Papers"),
         Div(
             H3("2024"),
             Ul(
                 Li("Large Language Models as Knowledge Engineers",
                    Br(),
                    Span("[",
                         A("PDF",
                           href="https://www.wi2.uni-trier.de/shared/publications/2024_ICCBR-WS_LLMInCBR_BrandEtAl.pdf")),
                    "]",
                    Span("[", A("DBLP", href="https://dblp.org/rec/conf/iccbr/BrandMB24.html")), "]"),
             ),
             H3("2023"),
             Ul(
                 Li("Using Deep Reinforcement Learning for the Adaptation of Semantic Workflows",
                    Br(),
                    Span("[",
                         A("PDF",
                           href="http://www.wi2.uni-trier.de/shared/publications/2023_Brand_RLForAdaptiveWorkflows.pdf")),
                    "]",
                    Span("[",
                         A("DBLP", href="https://dblp.org/rec/conf/iccbr/BrandLM0B23.html")), "]"),
                 Li("Adaptive Management of Cyber-Physical Workflows by Means of Case-Based Reasoning and Automated Planning",
                    Br(),
                    Span("[",
                         A("PDF",
                           href="http://www.wi2.uni-trier.de/shared/publications/2023_EDOC_MalburgEtAl_AdaptiveWorkflows_by_CBR_and_Planning.pdf")),
                    "]",
                    Span("[",
                         A("DBLP", href="https://dblp.org/rec/conf/edoc/MalburgBB22")),
                    "]"
                    )
             )
         ))
    )


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
