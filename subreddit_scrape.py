from praw import Reddit

def scrape(subreddit):
  """
  Scrapes comments from the provided subreddit and yields the textual content.

  TODO: configurable limit to allow more data
  """
  r = Reddit(user_agent='sonnit')
  for comment in r.get_subreddit(subreddit).get_comments(limit=1000):
    yield comment.body

if __name__=='__main__':
  """
  Writes comments from provided subreddit to stdout

  $ python subreddit_scrape.py starwars > starwars-comments.txt
  """
  import sys
  if len(sys.argv) < 2:
    print('args: subreddit')
    exit()

  for comment in scrape(sys.argv[1]):
    print(comment)
