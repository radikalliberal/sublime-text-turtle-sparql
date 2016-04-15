import sublime, sublime_plugin, http.client, urllib.parse, re, time
from html.parser import HTMLParser

class GotoRowColCommand(sublime_plugin.TextCommand):
    def run(self, edit, row, col):
        print("INFO: Input: " + str({"row": row, "col": col}))
        # rows and columns are zero based, so subtract 1
        # convert text to int
        (row, col) = (int(row) - 1, int(col) - 1)
        if row > -1 and col > -1:
            # col may be greater than the row length
            col = min(col, len(self.view.substr(self.view.full_line(self.view.text_point(row, 0))))-1)
            print("INFO: Calculated: " + str({"row": row, "col": col})) # r1.01 (->)
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(self.view.text_point(row, col)))
            self.view.show(self.view.text_point(row, col))
        else:
            print("ERROR: row or col are less than zero")               # r1.01 (->)

class MyHTMLParser(HTMLParser):
            
    def __init__(self):
        self.msg = 'looks good!'
        self.error = False
        HTMLParser.__init__(self)

    def handle_data(self, data):
        if self.lasttag == 'div':
            if data != '\r\n':
                self.msg = data
                self.error = True


class ValidateturtleCommand(sublime_plugin.TextCommand):
    def run(self, view):

        parser = MyHTMLParser()

        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Encoding": "gzip, deflate", "Accept-Language": "de,en-US;q=0.7,en;q=0.3", "Connection": "keep-alive"}
        turtlecode = self.view.substr(sublime.Region(0,self.view.size()))
        body = "data=" + urllib.parse.quote_plus(turtlecode, safe=':') + "%0D%0A%0D%0A%0D%0A&languageSyntax=Turtle"
        conn = http.client.HTTPConnection("sparql.org")
        conn.request("POST", "/validate/data",body, headers)
        response = conn.getresponse()
        data = response.read()
        parser.feed(data.decode("ASCII"))
        if parser.error:
            row = re.search('(?<=line:\s)\d*',parser.msg)
            col = re.search('(?<=col:\s)\d*',parser.msg)
            if self.view:
                self.view.run_command(
                    "goto_row_col",
                    {"row": row.group(0), "col": col.group(0)}
                )
        self.view.show_popup('<html><head></head><body><div style="color:' + 
        	                 ('firebrick4' if parser.error else 'chartreuse4') + 
        	                 ';font-size:18px;"><b>' + parser.msg + '</b></div><body></html>')
        conn.close()