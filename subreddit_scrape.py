import praw
from praw import Reddit


def scrape(subreddit, mode="submissions_hot"):
    """
    Scrapes comments from the provided subreddit and yields the textual content.
    """
    r = praw.Reddit(user_agent='sonnit').get_subreddit(subreddit)

    if mode.startswith('submissions_'):
        # Scrape comments from submissions (~1mb, very slow due to api rate limiting)
        itr = None
        if mode == 'submissions_hot':
            itr = r.get_hot(limit=None)
        elif mode == 'submissions_top':
            itr = r.get_top(limit=None)
        if itr is not None:
            for submission in itr:
                submission.replace_more_comments()
                for comment in submission.comments:
                    yield comment.body
        else:
            raise ValueError('Unknown mode {}'.format(mode))

    elif mode == 'recent_comments':
        # Scrape the most recent comments from the subreddit (limit 1000, ~150kb, fast)
        for comment in r.get_comments(limit=None):
            yield comment.body
    else:
        raise ValueError('Unknown mode {}'.format(mode))


if __name__ == '__main__':
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
