__author__ = 'Multitude -- http://www.experienceproject.com'
""" Experience Project API
    To do:
     * Functions for making data requests, including parsing for data on
       questions, stories, profiles, or main pages for Q&A/stories. "reading"
     * Set up a few test cases for all features.
     * Maybe refactor some function names and shit to make the API simple.
"""


from BeautifulSoup import BeautifulSoup as BS
from multiprocessing import Pool
from threading import Thread
import requests
import time
import sys
import random


DEFAULT_USERNAME = 'KeepEPClean'
DEFAULT_PASSWORD = "Don't waste your time."

BASE_URL = 'http://www.experienceproject.com/'


def main(argv):
    """
    Run some test cases for the API
    """
    pass // TODO: implement


def create_account(username=None, password=None, email=None,
                   birthmonth=1, birthyear=1900, gender='', verbose=False):
    url = BASE_URL + 'register.php'
    session = make_new_session()
    if username is None:
        # default to 9 random alphabetical characters
        username = 'something-here'
    if password is None:
        # default to six random digits
        password = ''.join(map(str, [random.randrange(10) for dummy in range(6)]))
    if email is None:
        # default to the username plus a three digit number @mailinator.com
        email = username + str(random.randrange(100,1000)) + '@mailinator.com'

    # send request to create account
    payload = {
        'username': username,
        'password': password,
        'email': email,
        'birthmonth': birthmonth,
        'birthyear': birthyear,
        'gender': gender,
        'register-button': 'Sign Up'
    }
    response = send_request(session, url, payload, verbose=verbose)

    return (username, password)


def post_story(session, group, content, mood='', verbose=False):
    url = BASE_URL + 'ajax/create-story'
    payload = {
        'group-name': group,
        'content': content,
        'mood': mood,
        'publish': 'Post'
    }

    send_request(session, url, payload, verbose=verbose)


def post_question(session, question, details,
                  category='community', verbose=False):
    url = BASE_URL + 'ajax/member/post-question'
    payload = {
        'question': question,
        'question-details': details,
        'category': category,
        'publish': 'Ask'
    }
    send_request(session, url, payload, verbose=verbose)


def mass_like(username, password, model_id, model_type,
              action='like', delay=2, num_loops=10, pool_size=21):
    not_action = 'unlike' if action == 'like' else 'like'
    url = BASE_URL + 'ajax/like'
    session = login(username, password)
    threads = [] # init this variable in the function scope
    
    try:
        for dummy in range(num_loops):
            threads = []
            current_time = time.time()
            execute_time = current_time + delay

            payload = {
                'modelType': model_type,
                'modelId': model_id,
                'action': action
            }
            flip_payload = {
                'modelType': model_type,
                'modelId': model_id,
                'action': not_action
            }

            # Do the inverse request here to make sure the others won't fail
            send_request(session, url, flip_payload, execute_time)
            
            # Args for concurrent requests
            args = [(session, url, payload, execute_time + delay)]
            
            # Here is where we send concurrent requests to fuck up some numbers
            for dummy in range(pool_size):
                t = Thread(target=send_request, args=args)
                threads.append(t)
                t.start()

    except Exception as e:
        print 'Will debug for food.'
        print e.message

    finally:
        for t in threads:
            t.join()


def login(username, password):
    session = make_new_session()

    payload = {
        'login_username': username,
        'login_password': password,
        'stay_logged_in': 't',
        'ref': 'member_groups.php',
        'login': 'Welcome+Home',
    }

    login_url = BASE_URL + 'dologinhandler.php'
    session.post(login_url, data=payload)

    return (session, user_agent, cookies)


def send_request(session, url, payload, execute_time=None, verbose=False):
    # load a page so that we get a CSRF code
    response = session.get(BASE_URL)

    soup = BS(response.text)
    csrf = soup.findAll('input', {'name':'_csrf'})[0]['value']
    
    payload['_ajax'] = 1  # basically everything needs this
    payload['_csrf'] = csrf

    # wait until the right time
    if execute_time:
        while time.time() < execute_time:
            pass

    session.post(url, data=payload)
    
    if verbose:  # mostly for debugging
        # concurrency and the regular `print` don't play nicely together
        sys.stdout.write(str(response.content) + '\n')


def make_new_session():
    session = requests.session()

    # must spoof user agent or EP will wet the bed
    session.headers = {
        'User-agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Ge' + \
        'cko) + Chrome/43.0.2357.81 Safari/537.36'
    }

    return session


if __name__ == '__main__':
    main(sys.argv)
