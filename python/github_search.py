#!/usr/bin/env python                                                                                                                                     
# -*- coding: utf-8 -*-
# Author: Bob Belderbos / written: Dec 2012
# Purpose: have an interactive github cli search app
#
import re, sys, urllib, pprint
# import html2text # -- to use local version

class GithubSearch:
  """ This is a command line wrapper around Github's Advanced Search
      https://github.com/search """

  def __init__(self):
    """ Setup variables """
    self.searchTerm = ""
    self.scripts = []
    self.show_menu()


  def show_menu(self):
    """ Show a menu to interactively use this program """
    prompt = """
      (N)ew search
      (S)how script of code sample
      (Q)uit
      Enter choice: """
    while True:
      chosen = False 
      while not chosen:
        try:
          choice = raw_input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
          choice = 'q'
        except:
          sys.exit("Not a valid option")
        print '\nYou picked: [%s]' % choice 
        if not choice.isdigit() and choice not in 'nsq':
          print "This is an invalid option, try again"
        else:
          chosen = True
      if choice == 'q': sys.exit("Selected -q-, exiting ...")
      if choice == 'n': self.new_search() 
      if choice == 's': self.show_script_context()
      # I usually throw a number in after (N), instead of going to (S) first
      if choice.isdigit(): self.show_script_context(int(choice)) 

  
  def new_search(self):
    """ Take the input field info for the advanced git search """
    # reset script url tracking list and counter
    self.scripts = [] 
    self.counter = 0
    # take user input to define the search
    self.searchTerm = raw_input("Enter search term: ").strip().lower().replace(" ", "+")
    lang = raw_input("Programming language (default = all): ").strip().lower()
    try:
      numSearchPages = int(raw_input("Number of search pages to process (more takes longer // default = 3): ").strip()[0])
    except:
      numSearchPages = 3
    # get the search results
    for page in range(1,numSearchPages+1):
      results = self.get_search_results(page, lang)
      for result in results[1].split("##"): # each search result is divided by ##
        self.parse_search_result(result)


  def get_search_results(self, page, lang):
    """ Query github's advanced search and re.split for the relevant piece of info 
        RFE: have a branch to use html2text local copy if present, vs. remote if not """
    githubSearchUrl = "https://github.com/search?q="
    searchUrl = urllib.quote_plus("%s%s&p=%s&ref=searchbar&type=Code&l=%s" % \
      (githubSearchUrl, self.searchTerm, page, lang))
    html2textUrl = "http://html2text.theinfo.org/?url="
    queryUrl = html2textUrl+searchUrl
    html = urllib.urlopen(queryUrl).read()
    return re.split(r"seconds\)|## Breakdown", html)


  def parse_search_result(self, result):
    """ Process the search results, also store each script URL in a dict for potential reference
        (if (D)ownload option is chosen from menu) """
    lines = result.split("\n")
    source = "".join(lines[0:2])
    pattern = re.compile(r".*\((.*?)\)\s+\((.*?)\).*")
    m = pattern.match(source)
    if m != None:
      self.counter += 1 
      url = "https://raw.github.com%s" % m.group(1).replace("tree/", "")
      lang = m.group(2)
      self.print_banner(lang, url)
      self.scripts.append(url) # keep track of script links 
      for line in lines[2:]:
        if "github.com" in line or "[Next" in line: continue # ignore pagination markup
        print ">> %s" % line


  def print_banner(self, lang, url):
    """ Print the script, lang, etc. in a clearly formatted way """
    width = 140
    delimit = "+" * width
    print "\n"
    print delimit
    print "(%i) %s / src: %s" % (self.counter, lang, url)
    print delimit


  def show_script_context(self, script_num=""):
    """ Another menu option to show more context from the github script 
        surrounding or leading up to the search term """
    if len(self.scripts) == 0:
      print "There are no search results yet, so cannot show any scripts yet."
      return False
    if not script_num:
      script_num = int(raw_input("Enter search result number: ").strip())
    try: 
      script = self.scripts[script_num-1]
      lines = urllib.urlopen(script).readlines() 
      if len(lines) == 0:
        print "Did not get content back from script, maybe it is gone?"
        return False
      num_context_lines = 7
      print "\nExtracting more context for search term <%s> ..." % self.searchTerm
      print "Showing %i lines before and after the match in the original script hosted here:\n%s\n" % \
        (num_context_lines, script)
      for i, line in enumerate(lines):
        if self.searchTerm in line:
          print "\n... %s found at line %i ..." % (self.searchTerm, i)
          j = i - num_context_lines
          for x in lines[i-num_context_lines : i+num_context_lines]:
            if self.searchTerm in x:
              print "%i ---> %s" % (j, x), # makes the match stand out
            else:
              print "%i      %s" % (j, x),        
            j += 1
    except:
      print "Something went wrong, could not get the script"
    pass



### instant
github = GithubSearch()