import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_method(self):
        node = HTMLNode(
            "a",
            "Blocked Button",
            None,
            {"href": "https://google.com", "disabled": "disabled"},
        )
        node2 = HTMLNode(
            "p", None, [node], {"class": "colored margin", "id": "paragraph"}
        )
        node3 = HTMLNode("h1", "Page Title", None, None)

        self.assertEqual(
            node.props_to_html(), 'href="https://google.com" disabled="disabled"'
        )
        self.assertEqual(node2.props_to_html(), 'class="colored margin" id="paragraph"')
        self.assertEqual(node3.props_to_html(), "")


class TestLeafNode(unittest.TestCase):
    def test_to_html_method(self):
        node = LeafNode("p", "This is a paragraph of text.")
        node2 = LeafNode("p", None, {"class": "colored margin", "id": "paragraph"})
        node3 = LeafNode("a", "Page Title", None)
        node4 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})

        self.assertEqual(node.to_html(), "<p>This is a paragraph of text.</p>")
        self.assertEqual(node3.to_html(), "<a>Page Title</a>")
        self.assertEqual(
            node4.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

        with self.assertRaises(ValueError):
            node2.to_html()


class TestParentNode(unittest.TestCase):
    def test_to_html_method(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        node2 = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                ParentNode(
                    "span",
                    [LeafNode(None, "Normal text "), LeafNode("b", "and bold text")],
                ),
            ],
        )

        node3 = ParentNode(
            "ul",
            [
                ParentNode(
                    "li",
                    [
                        LeafNode(None, "Normal text"),
                    ],
                ),
                ParentNode(
                    "li",
                    [
                        LeafNode("i", "italic text"),
                    ],
                ),
                ParentNode(
                    "li",
                    [
                        ParentNode(
                            "span",
                            [
                                LeafNode(None, "Normal text "),
                                LeafNode("b", "with bold text"),
                            ],
                        ),
                    ],
                ),
            ],
        )

        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

        self.assertEqual(
            node2.to_html(),
            "<div><b>Bold text</b><span>Normal text <b>and bold text</b></span></div>",
        )

        self.assertEqual(
            node3.to_html(),
            "<ul><li>Normal text</li><li><i>italic text</i></li><li><span>Normal text <b>with bold text</b></span></li></ul>",
        )


if __name__ == "__main__":
    unittest.main()
