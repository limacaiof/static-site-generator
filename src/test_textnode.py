import unittest

from htmlnode import ParentNode, HTMLNode, LeafNode

from textnode import (
    TextNode,
    TextType,
    BlockType,
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node,
    extract_title,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        node3 = TextNode("This is a text node", TextType.BOLD, "https://google.com")
        node4 = TextNode("This is a text node", TextType.ITALIC)

        self.assertEqual(node, node2)
        self.assertNotEqual(node, node3)
        self.assertNotEqual(node, node3)
        self.assertNotEqual(node2, node4)

    def test_text_node_to_html_node(self):
        node = TextNode("Normal text", TextType.TEXT, None)
        node2 = TextNode("Bold text", TextType.BOLD, None)
        node3 = TextNode("Italic text", TextType.ITALIC, None)
        node4 = TextNode("<h1>Page title</h1>", TextType.CODE, None)
        node5 = TextNode(None, TextType.LINK, "https://google.com")
        node6 = TextNode(
            "a image here",
            TextType.IMAGE,
            "https://images.pexels.com/photos/276267/pexels-photo-276267.jpeg",
        )

        self.assertEqual(
            str(text_node_to_html_node(node)), "HTMLNode(None, Normal text, None, None)"
        )
        self.assertEqual(
            str(text_node_to_html_node(node2)), "HTMLNode(b, Bold text, None, None)"
        )
        self.assertEqual(
            str(text_node_to_html_node(node3)), "HTMLNode(i, Italic text, None, None)"
        )
        self.assertEqual(
            str(text_node_to_html_node(node4)),
            "HTMLNode(code, <h1>Page title</h1>, None, None)",
        )
        self.assertEqual(
            str(text_node_to_html_node(node5)),
            "HTMLNode(a, None, None, {'href': 'https://google.com'})",
        )
        self.assertEqual(
            str(text_node_to_html_node(node6)),
            "HTMLNode(img, , None, {'src': 'https://images.pexels.com/photos/276267/pexels-photo-276267.jpeg', 'alt': 'a image here'})",
        )

    def test_split_nodes_delimiter(self):
        # node list / delimiter / type
        nodes = [
            (
                [TextNode("This is text with a `code block` word", TextType.TEXT)],
                "`",
                TextType.CODE,
            ),
            (
                [
                    TextNode(
                        "This is text with a **bolded phrase** in the middle",
                        TextType.TEXT,
                    )
                ],
                "**",
                TextType.BOLD,
            ),
            (
                [
                    TextNode(
                        "This is text with a *italic phrase* in the middle",
                        TextType.TEXT,
                    )
                ],
                "*",
                TextType.ITALIC,
            ),
        ]

        expected = [
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("italic phrase", TextType.ITALIC),
                TextNode(" in the middle", TextType.TEXT),
            ],
        ]

        invalid_nodes = [
            (
                [
                    TextNode(
                        "This is text with a **wrong bold phrase in the middle",
                        TextType.TEXT,
                    )
                ],
                "**",
                TextType.BOLD,
            ),
        ]

        for i in range(len(nodes)):
            node_list, delimiter, text_type = nodes[i]
            new_nodes = split_nodes_delimiter(node_list, delimiter, text_type)
            self.assertEqual(new_nodes, expected[i])

        for invalid in invalid_nodes:
            with self.assertRaises(Exception):
                node_list, delimiter, text_type = invalid
                split_nodes_delimiter(node_list, delimiter, text_type)

    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        text2 = "This is text with a link ![to boot dev](https://www.boot.dev/icon.png) and ![to youtube](https://www.youtube.com/icon.png)"

        self.assertEqual(
            extract_markdown_images(text),
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )
        self.assertEqual(
            extract_markdown_images(text2),
            [
                ("to boot dev", "https://www.boot.dev/icon.png"),
                ("to youtube", "https://www.youtube.com/icon.png"),
            ],
        )

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with a link ![to boot dev](https://www.boot.dev/icon.ico) and ![to youtube](https://www.youtube.com/icon.png)",
            TextType.TEXT,
        )

        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode(
                    "to boot dev", TextType.IMAGE, "https://www.boot.dev/icon.ico"
                ),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.IMAGE, "https://www.youtube.com/icon.png"
                ),
            ],
        )

    def test_split_nodes_link(self):

        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )

        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"

        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )

    def test_markdown_to_blocks(self):
        text = """
        # This is a heading

        This is a paragraph of text. It has some **bold** and *italic* words inside of it.

        * This is the first list item in a list block
        * This is a list item
        * This is another list item
        """

        text2 = """
        # This is a heading



        This is a paragraph of text. It has some **bold** and *italic* words inside of it.





        * This is the first list item in a list block
        * This is a list item
        * This is another list item
        """

        self.assertEqual(
            markdown_to_blocks(text),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                "* This is the first list item in a list block\n* This is a list item\n* This is another list item",
            ],
        )

        self.assertEqual(
            markdown_to_blocks(text2),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                "* This is the first list item in a list block\n* This is a list item\n* This is another list item",
            ],
        )

    def test_block_to_block_type(self):
        heading = "# This is a heading block"
        code = "```print('Hello world!')```"
        quote = "> This is a quote"
        unordered = "* first element\n* second element\n* third element"
        ordered = "1. first element\n2. second element\n3. third element"
        paragraph = "This is a paragraph"

        self.assertEqual(block_to_block_type(heading), BlockType.HEADING)
        self.assertEqual(block_to_block_type(code), BlockType.CODE)
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(unordered), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type(ordered), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type(paragraph), BlockType.PARAGRAPH)

    def test_markdown_to_html_node(self):
        markdown = """
        # This is a heading

        This is a paragraph of text. It has some **bold** and *italic* words inside of it.

        * first element
        * second element
        * third element
        """
        result = markdown_to_html_node(markdown)
        self.assertEqual(
            result,
            ParentNode(
                "div",
                [
                    HTMLNode("h1", "This is a heading", None, None),
                    HTMLNode(
                        "p",
                        None,
                        [
                            HTMLNode(
                                None,
                                "This is a paragraph of text. It has some ",
                                None,
                                None,
                            ),
                            HTMLNode("b", "bold", None, None),
                            HTMLNode(None, " and ", None, None),
                            HTMLNode("i", "italic", None, None),
                            HTMLNode(None, " words inside of it.", None, None),
                        ],
                        None,
                    ),
                    HTMLNode(
                        "ul",
                        None,
                        [
                            HTMLNode("li", "first element", None, None),
                            HTMLNode("li", "second element", None, None),
                            HTMLNode("li", "third element", None, None),
                        ],
                        None,
                    ),
                ],
            ),
        )

    def test_extract_title(self):
        markdown = """
        # This is a heading

        This is a paragraph of text. It has some **bold** and *italic* words inside of it.

        * first element
        * second element
        * third element
        """

        markdown2 = """
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.
        
        # This is a heading

        * first element
        * second element
        * third element
        """

        markdown3 = """
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.

        * first element
        * second element
        * third element
        """

        self.assertEqual(extract_title(markdown), "This is a heading")
        self.assertEqual(extract_title(markdown2), "This is a heading")
        
        with self.assertRaises(Exception):
            extract_title(markdown3)


if __name__ == "__main__":
    unittest.main()
