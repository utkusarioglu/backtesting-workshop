import pandas as pd


def produce_df(ROOT, soups):
    forward = []
    backward = []
    COMMON_TAGS = ["browser", "mdn"]
    for section in soups:
        section_title = section["section_title"]
        for item in section["section_items"]:
            soup = item["soup"]
            link_title = item["link_title"]

            article = soup.find("article")

            h1 = article.find("header").find("h1")
            h1_children = "".join(str(c) for c in h1.contents)

            p = article.select_one(".section-content > p")
            p_children = "".join(str(c) for c in p.contents)
            first_sentence = p_children.split(". ")[0].strip() + "."
            sanitized_first_sentence = first_sentence.replace(
                link_title, "___"
            )

            # Remove browser compatibility section
            # It is rendered using js and is not available in the
            # static page
            bc = article.find(id="browser_compatibility")
            if bc is not None:
                bc.decompose()
            for ns in article.find_all("noscript"):
                ns.parent.decompose()

            # Rewrite relative paths as they break in anki
            for a in article.find_all("a"):
                if not a.has_attr("href"):
                    continue
                if a["href"][0] == "/":
                    a["href"] = ROOT + a["href"]

            # Alter table styles to make then 100% width
            for table in article.find_all("table"):
                preexisting = table["style"] if table.has_attr("style") else ""
                table["style"] = ";".join(
                    [*preexisting.split(";"), "width: 100%;"]
                )

            # Insert mnd page link at the end of the page
            if article.find(id="inserted-mdn-link") is None:
                hr = soup.new_tag("hr")
                a = soup.new_tag("a", id="inserted-mdn-link", href=item["url"])
                a.string = f'Mdn entry for "{link_title}"'
                article.append(hr)
                article.append(a)
                for _ in range(3):
                    article.append(soup.new_tag("br"))

            pretty_article = article.prettify()

            common_tags = [
                *COMMON_TAGS,
                section_title,
                link_title,
            ]

            forward.append(
                {
                    "front": h1_children,
                    "back": pretty_article,
                    "tags": " ".join(
                        [
                            item.title().replace(" ", "")
                            for item in [*common_tags, "forward"]
                        ]
                    ),
                }
            )
            backward.append(
                {
                    "front": sanitized_first_sentence,
                    "back": pretty_article,
                    "tags": " ".join(
                        [
                            item.title().replace(" ", "")
                            for item in [*common_tags, "forward"]
                        ]
                    ),
                }
            )
    df = pd.DataFrame([*forward, *backward])
    return df
