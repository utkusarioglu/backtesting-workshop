from bs4 import BeautifulSoup


def fetch_root_page_from_file(FILE_ROOT):
    f = open("/".join([FILE_ROOT, "page.html"]), "r")
    html = f.read()
    f.close()
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_urls(ROOT, section):
    section_list = section.find("ol").find_all("li")

    urls = []

    for prop in section_list:
        a = prop.find("a")
        href = a["href"]
        link_title = a.code.string

        url = "".join([ROOT, href])
        urls.append(
            {
                "link_title": link_title,
                "url": url,
            }
        )
    return urls


def get_sections_urls(ROOT, sections):
    urls = []
    for section in sections:
        section_title = section.find("summary").text
        section_urls = get_urls(ROOT, section)
        urls.append(
            {
                "section_title": section_title,
                "items": section_urls,
            }
        )
        # urls[section_title] = section_urls
    return urls
