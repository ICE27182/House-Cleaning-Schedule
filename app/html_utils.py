

from .type_aliases import RowNo, ColNo


def html_a(href:str, text:str, class_:str = None, id:str = None) -> str:
    return (
        f"<a href=\"{href}\"" + 
            f"{'' if class_ is None else f' class="{class_}"'}" +
            f"{'' if id is None else f' id="{id}"'}" +
        ">" + 
            text +
        "</a>"
    )
def html_p(text:str, class_:str = None, id:str = None) -> str:
    return (
        "<p" +
            f"{'' if class_ is None else f' class="{class_}"'}" +
            f"{'' if id is None else f' id="{id}"'}" +
        ">" + 
            text +
        "</p>"
    )

class HtmlTable:
    def __init__(self, rows:int, columns:int, class_:str = None, id:str = None):
        """
        An empty HTML table with given rows and columns.

        Use `str` to get the table in html.

        Note that rows and columns cannot be changed without accessing
        self.table once it is initiated
        """
        self.table:list[list[str]] = [[""] * columns for _ in range(rows)]
        # i used class_ instead of class becuase class is a keyword
        self.class_ = class_
        self.id = id
    
    def __getitem__(self, posi:tuple[RowNo, ColNo]) -> str:
        """
        Indices start with 0s
        """
        row_no, col_no = posi
        return self.table[row_no][col_no]
    
    def __setitem__(self, posi:tuple[RowNo, ColNo], html_elem:str) -> None:
        """Indices start with 0s"""
        row_no, col_no = posi
        self.table[row_no][col_no] = html_elem
    
    def __str__(self):
        """Get html"""
        out = [
            (
                "<table" + 
                ('' if self.class_ is None else f' class="{self.class_}"') +
                ('' if self.id is None else f' id="{self.id}"') +
                '>'
            ),
        ]
        for row in self.table:
            out.append("<tr>")
            for col in row:
                out.append(f"<td>{col}</td>")
            out.append("</tr>")
        out.append("</table>")
        return "".join(out)
    