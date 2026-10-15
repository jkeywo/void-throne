"""Fixed browser-worker entry points around the shared multiplayer authority."""
from copy import deepcopy
from .multiplayer import Multiplayer
from .current_session import from_actions, Session, new_game
from .session import Session as LegacySession


class BrowserHost:
    def __init__(self, backup=None):
        self.session = Multiplayer()
        if backup is not None:
            if backup.get('version') != 1 or not isinstance(backup.get('actions'), list):
                raise ValueError('This browser save is not a supported game. Keep it for recovery.')
            self.session.game=from_actions(backup['actions'])
            if not backup['actions'] and backup.get('ruleset') != Session().public()['ruleset']:
                self.session.game=new_game(backup.get('ruleset','vt:rules:revised-visions-v0.3'))
            for key in ('room', 'seats', 'sheets', 'chats', 'audit', 'revision', 'seen'):
                setattr(self.session, key, deepcopy(backup[key]))

    def request(self, action, payload):
        m = self.session
        if action == 'host':
            result = m.begin_host()
        elif action in ('report', 'export'):
            m.check_host(payload.get('host_key'))
            return {'download': m.report().decode('utf8') if action == 'report' else m.export()}
        else:
            result = m.dispatch(action, payload)
        return {'envelope': result, 'backup': m.backup()}
