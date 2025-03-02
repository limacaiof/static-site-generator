import os
import sys
import shutil
import pathlib

from textnode import markdown_to_html_node, extract_title

BASE_PATH = sys.argv[1] if len(sys.argv) > 1 else "/"
BUILD_PATH = "docs/"
STATIC_PATH = "static/"
CONTENT_PATH = "content/"

def main():
    if os.path.exists(BUILD_PATH):
        shutil.rmtree(BUILD_PATH)

    setup(STATIC_PATH)
    generate_pages_recursive(CONTENT_PATH, "template.html", BUILD_PATH, BASE_PATH)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for item in os.listdir(dir_path_content):
        item_path = pathlib.Path(os.path.join(dir_path_content, item))
        dest_path = pathlib.Path(os.path.join(dest_dir_path, item))

        if item_path.is_dir():
            generate_pages_recursive(item_path, template_path, dest_path, basepath)
        elif item_path.is_file() and item_path.suffix == ".md":
            generate_page(item_path, template_path, dest_path.with_suffix(".html"), basepath)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as m:
        markdown = m.read()

    with open(template_path, "r") as t:
        page = t.read()

    title = extract_title(markdown)
    nodes = markdown_to_html_node(markdown)
    content = nodes.to_html()

    template = page.replace("{{ Title }}", title, 1).replace( "{{ Content }}", content, 1).replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, "w") as d:
        d.write(template)


def setup(path: str):

    store_path = f"{BUILD_PATH}/" + path.split(STATIC_PATH, 1)[1]
    if not os.path.exists(store_path):
        os.mkdir(store_path)

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        if os.path.isfile(item_path):
            shutil.copy(item_path, os.path.join(store_path, item))
        else:
            setup(item_path)

    return


main()
