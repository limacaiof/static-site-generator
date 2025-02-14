import os
import shutil
import pathlib

from textnode import markdown_to_html_node, extract_title


def main():
    if os.path.exists("public"):
        shutil.rmtree("public")

    setup("static/")
    generate_pages_recursive("content", "template.html", "public")


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in os.listdir(dir_path_content):
        item_path = pathlib.Path(os.path.join(dir_path_content, item))
        dest_path = pathlib.Path(os.path.join(dest_dir_path, item))

        if item_path.is_dir():
            generate_pages_recursive(item_path, template_path, dest_path)
        elif item_path.is_file() and item_path.suffix == ".md":
            generate_page(item_path, template_path, dest_path.with_suffix(".html"))


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as m:
        markdown = m.read()

    with open(template_path, "r") as t:
        template = t.read()

    title = extract_title(markdown)
    nodes = markdown_to_html_node(markdown)
    content = nodes.to_html()

    template = template.replace("{{ Title }}", title, 1).replace( "{{ Content }}", content, 1)

    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, "w") as d:
        d.write(template)


def setup(path: str):

    public_path = "public/" + path.split("static/", 1)[1]
    if not os.path.exists(public_path):
        os.mkdir(public_path)

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        if os.path.isfile(item_path):
            shutil.copy(item_path, os.path.join(public_path, item))
        else:
            setup(item_path)

    return


main()
