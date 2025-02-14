class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError

    def props_to_html(self) -> str:
        if self.props is None:
            return ""
        return " ".join([f'{key}="{val}"' for key, val in self.props.items()])

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {str(self.props)})"

    def __eq__(self, other):
        return (
            self.tag == other.tag
            and self.value == other.value
            and self.children == other.children
            and str(self.props) == str(other.props)
        )


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self) -> str:
        if self.value is None:
            raise ValueError()

        if self.tag is None:
            return self.value

        html_props = self.props_to_html()
        if html_props:
            return f"<{self.tag} {html_props}>{self.value}</{self.tag}>"

        return f"<{self.tag}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        if self.tag is None:
            raise ValueError()

        if self.children is None:
            raise ValueError("ParentNode must have at least one child")

        content = "<{0}>{1}</{0}>".format(
            self.tag, "".join(list(map(lambda x: x.to_html(), self.children)))
        )

        return content
