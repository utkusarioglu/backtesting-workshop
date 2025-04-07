from requests import get
from bs4 import BeautifulSoup
import re
import pandas as pd


def get_page():
    response = get(
        "https://terragrunt.gruntwork.io/docs/reference/cli-options"
    )
    if response.status_code != 200:
        raise RuntimeError("PAGE_UNAVAILABLE")
    return response.text


def write_html(artifact_abspath, text):
    file = open(artifact_abspath, "w+")
    file.write(text)
    file.close()


def read_soup(artifact_abspath):
    """Reads cached html file from artifact path and returns it as a
    Soup
    """
    file = open(artifact_abspath, "r")
    content = file.read()
    file.close()
    soup = BeautifulSoup(content, "html.parser")
    return soup


def fix_hrefs(base, article):
    a_list = article.find_all("a")
    for anchor in a_list:
        if anchor["href"].startswith("/"):
            anchor["href"] = base + anchor["href"]

    src_list = article.find_all(lambda e: e.has_attr("src"))
    for src in src_list:
        if src["src"].startswith("/"):
            src["src"] = base + src["src"]
    return article


def parse_entries(article):
    """Parses the soup to create lists of different documentation entries"""
    h2_list = article.find_all("h2")
    parsed = [{"header": h2, "list": []} for h2 in h2_list]

    for section in parsed:
        h3_head = section["header"].find_next("h3")
        is_deprecated = False
        loop = []
        for sibling in h3_head.find_next_siblings():
            if isinstance(sibling, str):
                continue
            if sibling.name == "h2":
                h3_head = None
                is_deprecated = False
                loop = []
                break
            if sibling.name == "h3":
                section["list"].append(
                    {
                        "header": h3_head,
                        "is_deprecated": is_deprecated,
                        "list": loop,
                        "details": BeautifulSoup(
                            "".join([e.prettify() for e in loop]),
                            "html.parser",
                        ),
                    }
                )
                loop = []
                is_deprecated = False
                h3_head = sibling
                continue

            if sibling.find(string=re.compile("DEPRECATED")):
                is_deprecated = True

            loop.append(sibling)
    return parsed


def enrich_entries(entries):
    content = []
    for section in entries:
        h2_string = section["header"].string
        section_content_list = []
        # contents.append({"h2": h2_string, "list": []})

        for entry in section["list"]:
            h3_string = entry["header"].string
            h3_string = re.sub(r" \(.*\)", "", h3_string)
            h2_tag = "".join([w.title() for w in h2_string.split(" ")])
            tags = [h2_tag]
            is_deprecated = entry["is_deprecated"]
            if is_deprecated:
                tags.append("Deprecated")

            if is_deprecated:
                summary = entry["list"][1]
            elif h2_string == "CLI options":
                next_p = entry["list"][0].find_next("p")
                if next_p.text.startswith("Can be supplied"):
                    next_p = next_p.find_next("p")
                summary = next_p
                # summary = entry["list"][0].find_next("p")
            else:
                summary = entry["list"][0]
            summary = summary.text.split(".")[0] + "."
            summary = " ".join(summary.split("\n"))
            summary = summary.replace(h3_string, "___")
            pretty_details = entry["details"].prettify()
            pretty_details_with_h3 = BeautifulSoup(
                "".join(
                    [e.prettify() for e in [entry["header"], entry["details"]]]
                ),
                "html.parser",
            ).prettify()
            section_content_list.append(
                {
                    **entry,
                    "pretty_details": pretty_details,
                    "summary": summary,
                    "h3_string": h3_string,
                    "tags": tags,
                    "tags_string": " ".join(tags),
                    "pretty_details_with_h3": pretty_details_with_h3,
                }
            )
        content.append({"h2_string": h2_string, "list": section_content_list})

    return content


def create_df(content_list):
    commands = pd.DataFrame(content_list)
    forwards = commands[["h3_string", "pretty_details", "tags_string"]]
    forwards = forwards.rename(
        columns={
            "h3_string": "front",
            "pretty_details": "back",
            "tags_string": "tags",
        }
    )
    forwards["tags"] = forwards["tags"].apply(lambda v: f"{v} Forwards")
    backwards = commands[["summary", "pretty_details_with_h3", "tags_string"]]
    backwards = backwards.rename(
        columns={
            "summary": "front",
            "pretty_details_with_h3": "back",
            "tags_string": "tags",
        }
    )
    backwards["tags"] = backwards["tags"].apply(lambda v: f"{v} Backwards")
    merged = pd.concat([forwards, backwards], ignore_index=True)
    return merged
