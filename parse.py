import sys
from html.parser import HTMLParser

class LessWrongParser(HTMLParser):

    def __init__(self) :
       self.mode = None
       self.result = []
       self.attrs = {}
       self.divStack = []
       HTMLParser.__init__(self)

    def addToComment(self, data) :
       self.attrs["comment"] += data

    def handle_starttag(self, tag, attrs):
        classValue = dict(attrs).get("class")

        if tag=="div" :
            self.divStack.append(classValue)

        if self.mode=="md" :
            self.addToComment(self.get_starttag_text())
            return

        if tag=="div" and classValue=="md" :
            self.mode = "md"
            self.attrs["comment"] = ""

        if tag=="span" and classValue=="votes " :
            self.mode = "votes"

        if tag=="span" and classValue=="author" :
            self.mode = "author"

        if tag=="span" and classValue=="comment-date" :
            self.mode = "date"

        if tag=="a" and self.mode==None :
            aydee = dict(attrs).get("id")
            if aydee and len(aydee)>=13 and aydee[:13]=="permalink_t1_" :
                self.attrs["permalink"] = dict(attrs)["href"]
        self.mode = "done"

    def handle_data(self,data) :
       if self.mode==None or self.mode=="done" :
           return

       # This was patched in in 2012, as the newlines were mistaken with real data:
       if data=="\n" :
           return

       if self.mode=="md" :
           self.addToComment(data)
           return

       if self.mode=="votes" :
           data = int(data.split(" ")[0])

       self.attrs[self.mode] = data
       self.mode = None

    def handle_endtag(self, tag) :
       if tag=="div" :
           poppedDivClass = self.divStack[-1]
           self.divStack = self.divStack[:-1]

       if self.mode=="md" and tag!="div" :
           self.addToComment("</"+tag+">")
           return
       elif self.mode=="done" :
           self.attrs["ischild"] = ( "child" in self.divStack )
           self.result.append(self.attrs.copy())
           self.attrs = {}

#            (self.votes,self.author,self.permalink,self.date,self.comment) )
       self.mode = None

    def getResult(self) :
       return self.result

def collectResults() :
    allResults = []

    for url in sys.stdin.readlines() :
       filename = url.strip().split("/")[-1]
       sys.stderr.write(filename+"\n")
       filetext = open(filename).read()

       p = LessWrongParser()
       p.feed(filetext)
       p.close()
       allResults += p.getResult()
    return allResults

def printPost(votes,permalink,date,comment,ischild,author=None) :
    if author!=None :
       authorURL = "<a href=\"http://lesswrong.com/user/"+author+"\">"+author+"</a>"
    else :
       authorURL = "[deleted]"

    print(("""
<div class="comment">
    <div class="entry">
       <div class="comment-meta clear">
           <span class="votes ">""" + str(votes) + """ points</span>
           <span class="comment-author"><strong>""" +authorURL+ """</strong></span>
           <span class="comment-author">""" +date+ """</span>
           <span class="comment-author"><a href=\" """ + permalink +
           """\">Permalink</a></span>
       </div>
    </div>
    <div class="comment-content">
       <div class="md">
"""+ comment + """
       </div>
    </div>
</div>"""))

def printHeader() :
    print(file("lesswrong.template").read())

def printFooter() :
    print("""
</div></div></div></div></div></div>
</body>""")

def textTable(allResults,includeChildren,forMaxent) :
    for result in allResults :
        if includeChildren or not result["ischild"] :
           votes = result["votes"]
           q = result["comment"]
           if forMaxent :
                s = sorted(list(set(q.split())))
                print(str(votes)+"\t"+ " ".join(s))
           else :
                print(str(votes)+"\t"+q.replace("\n"," "))

def scoreTable(allResults,includeChildren) :
    for result in allResults :
        if includeChildren or not result["ischild"] :
           votes = result["votes"]
           author = result.get("author","[deleted]")
           print(author +"\t"+ str(votes))

def main() :
    argNum = len(sys.argv)
    assert argNum in (2,3,4)
    command = sys.argv[1]
    assert command in ("pretty","score","text","rawtext")

    minimalScoreToInclude = 1e-9
    if argNum>=3 :
       assert command=="pretty"
       minimalScoreToInclude = int(sys.argv[2])

    includeChildren = False
    if argNum==4 :
       assert sys.argv[3]=="includechildren"
       includeChildren = True

    allResults = collectResults()

    if command=="pretty" :
       allResults.sort( key = lambda attrs : -attrs["votes"] )
       printHeader()
       for result in allResults :
           votes = result["votes"]
           isChild = result["ischild"]
           if votes>=minimalScoreToInclude :
                if includeChildren or not isChild :
                    # sys.stderr.write( result.get("author","[deleted]") +"\t"+ str(result["votes"]) +"\n" )
                    printPost(**result)

       printFooter()
    elif command=="score" :
       scoreTable(allResults,includeChildren)
    elif command=="text" :
       textTable(allResults,includeChildren,forMaxent=True)
    elif command=="rawtext" :
       textTable(allResults,includeChildren,forMaxent=False)
    else :
       assert False

main()
