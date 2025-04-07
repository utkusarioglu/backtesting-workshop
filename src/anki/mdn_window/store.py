import json
from requests import get
from bs4 import BeautifulSoup


def write_specs(FILE_ROOT, name, specs):
    f = open(
        "".join(
            [
                FILE_ROOT,
                "/",
                name,
                ".b64",
            ],
        ),
        "w+",
    )
    # ascii_encoded = json.dumps(specs).encode("ascii")
    # b64_encoded = base64.b64encode(ascii_encoded)
    # f.write(str(b64_encoded))
    f.write(json.dumps(specs))
    f.close()


def get_section_content(section_name, items):
    print(f"Fetching section: {section_name}")
    content = []
    for item in items:
        link_title = item["link_title"]
        url = item["url"]
        print(f"  {link_title}")
        r = get(url)
        if r.status_code != 200:
            print(f"Something went wrong in {url}")
            continue
        content.append(
            {
                "section_name": section_name,
                "url": url,
                "link_title": link_title,
                "html": r.text,
            }
        )
    return content


def get_sections_content(sections_urls):
    content = []
    for section in sections_urls:
        section_title = section["section_title"]
        section_items = section["items"]
        section_content = get_section_content(section_title, section_items)
        content.append(
            {
                "section_title": section_title.title(),
                "section_items": section_content,
            }
        )
    return content


def load_soups(FILE_ROOT: str, file_relpath: str):
    file_abspath = "/".join([FILE_ROOT, file_relpath])
    f = open(file_abspath, "r")
    r = f.read()
    specs = json.loads(r)
    # print(r)
    # f.close()
    # specs_b64 = base64.b64decode(r)
    # print(specs_b64)
    # specs = json.loads(specs_b64.decode("utf-8"))
    # print(specs)
    for section in specs:
        for item in section["section_items"]:
            item["soup"] = BeautifulSoup(item["html"], "html.parser")
    return specs
