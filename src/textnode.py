import re

from enum import Enum

from htmlnode import HTMLNode, LeafNode, ParentNode

IMAGE_REGEX_PATTERN = r"\!\[(.*?)\]\((.*?)\)"
LINK_REGEX_PATTERN = r"\[(.*?)\]\((.*?)\)"

REGEX_HEADING_PATTERN = r"^(#{1,6}\ )(.*)"
REGEX_CODE_PATTERN = r"(```)?(\w*)([\S\s]*)(```)"
REGEX_QUOTE_PATTERN = r">\ ?(.*)"
REGEX_UNORDERED_LIST_PATTERN = r"^((\*|\-)\ \w)"
REGEX_ORDERED_LIST_PATTERN = r"^([1-9]([0-9]+)?\.\ \w)"


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    QUOTE = "quote"
    CODE = "code"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            (self.text == other.text)
            and (self.text_type == other.text_type)
            and (self.url == other.url)
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> HTMLNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text, None)
        case TextType.BOLD:
            return LeafNode("b", text_node.text, None)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text, None)
        case TextType.CODE:
            return LeafNode("code", text_node.text, None)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue

        splited = node.text.split(delimiter)
        if len(splited) % 2 == 0:
            raise Exception("Invalid Markdown")

        new_text = []
        for i in range(len(splited)):
            if splited[i] == "":
                continue

            new_text.append(
                TextNode(splited[i], node.text_type if i %
                         2 == 0 else text_type)
            )
        new_nodes.extend(new_text)

    return new_nodes


def extract_markdown_images(text: str) -> list:
    return re.findall(IMAGE_REGEX_PATTERN, text)


def extract_markdown_links(text: str) -> list:
    return re.findall(LINK_REGEX_PATTERN, text)


def split_nodes_image(old_nodes: list[TextNode]):
    new_nodes = []
    for old_node in old_nodes:
        text = old_node.text
        links = extract_markdown_images(text)
        for link in links:
            section = text.split(f"![{link[0]}]({link[1]})", 1)
            if len(section) != 2:
                raise Exception("Invalid Markdown")
            if section[0] != "":
                new_nodes.append(TextNode(section[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.IMAGE, link[1]))
            text = section[1]
        if text != "":
            new_nodes.append(TextNode(text, old_node.text_type, old_node.url))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]):
    new_nodes = []
    for old_node in old_nodes:
        text = old_node.text
        links = extract_markdown_links(text)
        for link in links:
            section = text.split(f"[{link[0]}]({link[1]})", 1)
            if len(section) != 2:
                raise Exception("Invalid Markdown")
            if section[0] != "":
                new_nodes.append(TextNode(section[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            text = section[1]
        if text != "":
            new_nodes.append(TextNode(text, old_node.text_type, old_node.url))
    return new_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []
    current_block = []
    for line in markdown.split("\n"):
        is_code_block = len(current_block) and current_block[0].startswith("```")
        if is_code_block:
            current_block.append(line)
            if line == "```":  # closes code tag
                blocks.append("\n".join(current_block))
                current_block.clear()
        else:
            content = line.strip()
            if content != "":
                current_block.append(content)
                continue

            if len(current_block) != 0:
                blocks.append("\n".join(current_block))
                current_block.clear()

    if len(current_block) > 0:
        blocks.append("\n".join(current_block))
    return blocks


def block_to_block_type(block: str) -> BlockType:
    if re.match(REGEX_HEADING_PATTERN, block):
        return BlockType.HEADING

    if re.match(REGEX_CODE_PATTERN, block):
        return BlockType.CODE

    if re.match(REGEX_QUOTE_PATTERN, block):
        return BlockType.QUOTE

    if re.match(REGEX_UNORDERED_LIST_PATTERN, block):
        return BlockType.UNORDERED_LIST

    if re.match(REGEX_ORDERED_LIST_PATTERN, block):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    nodes = []
    mardown_blocks = markdown_to_blocks(markdown)
    for block in mardown_blocks:
        block_type = block_to_block_type(block)
        nodes.append(block_to_html_node(block, block_type))

    return ParentNode("div", nodes)


def block_to_html_node(block: str, block_type: BlockType) -> HTMLNode:
    match block_type:
        case BlockType.HEADING:
            return heading_block_to_html_node(block)

        case BlockType.CODE:
            return code_block_to_html_node(block)

        case BlockType.QUOTE:
            return quote_block_to_html_node(block)

        case BlockType.ORDERED_LIST:
            return list_block_to_html_node(block)

        case BlockType.UNORDERED_LIST:
            return list_block_to_html_node(block)

        case BlockType.PARAGRAPH:
            return paragraph_block_to_html_node(block)


def extract_title(markdown: str) -> str:
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block.split("# ", 1)[1].strip()

    raise Exception("No title found in markdown")


# Helpers
def heading_block_to_html_node(block: str):
    h_size = block.count("#")
    text = block.split("#" * h_size + " ")[1]
    tag = f"h{h_size}"

    children = text_to_children(text)
    if children:
        return ParentNode(tag, children)

    return LeafNode(tag, text)


def code_block_to_html_node(block: str):
    matches = re.findall(REGEX_CODE_PATTERN, block)[0]
    lang = matches[1]
    code = matches[2].lstrip("\n")

    props = {'class': f"language-{lang}"} if lang else None

    return ParentNode("pre", [LeafNode("code", code, props)])


def quote_block_to_html_node(block: str):
    nodes = []

    quotes = re.findall(REGEX_QUOTE_PATTERN, block)
    if len(quotes) == 1:
        children = text_to_children(quotes[0])
        return ParentNode("blockquote", children) if children else LeafNode("blockquote", quotes[0])

    for quote in quotes:
        children = text_to_children(quote)
        nodes.append(ParentNode("p", children) if children else LeafNode("p", quote))

    return ParentNode("blockquote", nodes)


def list_block_to_html_node(block: str):
    nodes = []

    lines = block.split("\n")
    for line in lines:
        content = line.split(" ", 1)[1].strip()
        children = text_to_children(content)
        nodes.append(
            ParentNode("li", children) if children else LeafNode("li", content)
        )
    tag = "ol" if lines[0].strip()[0].isnumeric() else "ul"

    return ParentNode(tag, nodes)


def paragraph_block_to_html_node(block: str):
    tag = "p"

    children = text_to_children(block)
    if children:
        return ParentNode(tag, children)

    return LeafNode(tag, block)


def text_to_children(text: str):
    nodes = text_to_textnodes(text)
    if len(nodes) == 1 and nodes[0].text_type == TextType.TEXT:  # meaning that is leaf
        return None

    return list(map(text_node_to_html_node, nodes))
