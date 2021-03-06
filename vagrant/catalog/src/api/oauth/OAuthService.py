from flask import url_for, redirect, request, flash

from rauth import OAuth2Service

app = None
def init(_app):
    global app
    app = _app
    app.logger.debug('starting oauth')

    app.config['OAUTH_CREDENTIALS'] = {
        'facebook': {
            'id': '942561322487830',
            'secret': '6e36e09a076053e79503cf64caef6318'
        },
        'twitter': {
            'id': '',
            'secret': ''
        }
    }

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        print app
        self.provider_name = provider_name
        credentials = app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider

        return self.providers[provider_name]

class FacebookSignIn(OAuthSignIn):
    provider_name = 'facebook'
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',           
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email, public_profile',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        
        return (
            'facebook$' + me['id'],
            me['name']
        )

