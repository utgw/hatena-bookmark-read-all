from xml.etree import ElementTree
from typing import Dict, List, Tuple
from urllib.parse import parse_qs
import requests
import constants
TokenPair = Tuple[str, str]

def _get(auth, url, *, params=None) -> requests.Response:
    '''
    GETリクエストを送る
    モジュールの外から直接呼ばず、適宜関数を定義して使うこと
    '''
    if params is None:
        params = {}

    headers = {'User-Agent': constants.USER_AGENT}
    resp = requests.get(
        url,
        headers=headers,
        auth=auth,
        params=params,
    )
    resp.raise_for_status()
    return resp

def _post(auth, url, *, params=None) -> requests.Response:
    '''
    POSTリクエストを送る
    モジュールの外から直接呼ばず、適宜関数を定義して使うこと
    '''
    if params is None:
        params = {}

    headers = {'User-Agent': constants.USER_AGENT}
    resp = requests.post(
        url,
        headers=headers,
        auth=auth,
        params=params,
    )
    resp.raise_for_status()
    return resp

def request_token(oauth) -> TokenPair:
    '''
    OAuth認可のためのトークンを要求する
    '''
    # Fetch access token
    params = {
        'scope': constants.SCOPE,
        'oauth_callback': constants.CALLBACK_URL,
    }
    resp = _post(
        oauth,
        constants.REQUEST_TOKEN_URL,
        params=params,
    )

    resp_body = parse_qs(resp.text)
    oauth_token = resp_body['oauth_token'][0]
    oauth_token_secret = resp_body['oauth_token_secret'][0]
    return oauth_token, oauth_token_secret

def get_access_token(auth) -> TokenPair:
    '''
    アクセストークンを取得する
    '''
    resp = _post(
        auth,
        constants.GET_ACCESS_TOKEN_URL,
    )
    resp_body = parse_qs(resp.text)
    oauth_token = resp_body['oauth_token'][0]
    oauth_token_secret = resp_body['oauth_token_secret'][0]
    return oauth_token, oauth_token_secret

def get_username(auth) -> str:
    '''
    REST APIを叩いてログインユーザのユーザ名を取得する
    '''
    resp = _get(
        auth,
        'https://bookmark.hatenaapis.com/rest/1/my'
    )
    return resp.json()['name']

def get_bookmark(auth, url):
    '''
    REST APIを叩いて指定されたURLのブックマーク情報を取得する
    '''
    resp = _get(
        auth,
        'https://bookmark.hatenaapis.com/rest/1/my/bookmark',
        params={'url': url},
    )
    return resp.json()

def update_bookmark(auth, url, comment, tags):
    '''
    REST APIを叩いて指定されたURLのブックマーク情報を更新する
    '''
    params = {'url': url, 'comment': comment, 'tags': tags}
    _post(
        auth,
        'https://bookmark.hatenaapis.com/rest/1/my/bookmark',
        params=params,
    )

def get_bookmark_feed(auth, username, page=1) -> str:
    '''
    指定されたユーザの「あとで読む」タグが付いたブックマークのRSSを取得する
    ページネーション可能 (page引数で指定)
    '''
    params = {'tag': 'あとで読む', 'page': page}
    resp = _get(
        auth,
        f'https://b.hatena.ne.jp/{username}/bookmark.rss',
        params=params,
    )
    return resp.text

def get_bookmark_feed_as_list(auth, username, page=1) -> List[Dict[str, str]]:
    '''
    指定されたユーザの「あとで読む」タグが付いたブックマークのRSSを取得し、
    辞書型のリストに変換して返す
    ページネーション可能 (page引数で指定)
    '''
    xml = get_bookmark_feed(auth, username, page)

    tree = ElementTree.fromstring(xml)
    namespace = {
        'rdf': 'http://purl.org/rss/1.0/',
        'dc': 'http://purl.org/dc/elements/1.1/',
    }

    data = []
    targets = tree.findall('rdf:item', namespace)
    for elem in targets:
        url = elem.find('rdf:link', namespace).text
        title = elem.find('rdf:title', namespace).text
        date = elem.find('dc:date', namespace).text.replace('T', ' ')
        entry = {'url': url, 'title': title, 'date': date}
        data.append(entry)

    return data
