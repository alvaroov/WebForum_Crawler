# Written by Alvaro Ortiz-Vazquez
# October 4, 2016
import pycurl
import bs4
import csv

# Using pycurl to pull source from first thread page. 
a = file("source.html", "wb+")
c = pycurl.Curl()
c.setopt(c.URL, 'http://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/viewtopic.php?t=12591')
c.setopt(c.WRITEDATA, a)
c.perform()

# First time = true
firsttime = 1

# Opening CSV file to store thread information
forum = file("forum.csv", "wb+")
writer = csv.writer(forum)

# Loop until no "Next" page.
while(firsttime or bool(link_body.find('a',text='Next'))):
    
# Using lxml as the parser we seek the html table with the class "forumline" which contains the posts.
    a.seek(0)
    body = a.read()
    soup = bs4.BeautifulSoup(body, "lxml")
    body_tag = soup.body
    table_tag = body_tag.find('table','forumline')

#   Two iterators to go through the data for the dates and the postbodies. 
    date_data = iter(table_tag.find_all("span", "postdetails"))
    postbody_data = iter(table_tag.find_all("span", "postbody"))
    
# Iterate through each post  
    for name_data in table_tag.find_all("span","name"):
        postid = name_data.a['name'].encode('ascii') + ';'
        name = '"' + name_data.b.contents[0].encode('ascii') + '"' + ';'
        
# We must skip over the block of code referencing "Date joined" to pull instead "Date posted"         
        date = date_data.next()
        date = date_data.next()
        date1 = date.contents[0][8:].encode('ascii') + ';'
        
# The postbody may be split up into pieces by </br> tags which we do not want to pull.
# We skip over quoted text since not part of main post body.
        fullcomment = str()
        count = 0
        while(len(fullcomment) == 0 or count == 0 ):
            postbody = postbody_data.next()
            while(not postbody.contents or postbody.parent.attrs == {'class': ['quote']}):
                postbody=postbody_data.next()         
            for i in range(0, len(postbody.contents), 1):
                commentpart = repr(postbody.contents[i].encode('utf-8'))
                if(commentpart == "'_________________'"):
                    break
                elif(commentpart != "'<br/>'"):
                    fullcomment += commentpart[1:-1]
            count += 1
        writer.writerow([postid, name, date1, fullcomment])

#  Take the next page link from 'Next' button in navigation on the page.

    link_body = body_tag.find("span","gensmall")
    try:
        link = 'http://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/' + link_body.find('a',text='Next')['href']
        a.seek(0)
        c.setopt(c.URL, link)
        c.setopt(c.WRITEDATA, a)
        c.perform()
    except:
        break
        
    firsttime = 0

#  Close opened files and Curl()
c.close()
forum.close()
a.close()

print 'Done'