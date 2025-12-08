"""In-memory storage for QPPI Firewall"""

class InMemoryStore:
    """Simple in-memory storage for profiles and policies"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.profiles = {}
        self.policies = {}
        self.sessions = {}
    
    def get_profile(self, profile_id):
        return self.profiles.get(profile_id)
    
    def set_profile(self, profile_id, data):
        self.profiles[profile_id] = data
    
    def get_policy(self, policy_id):
        return self.policies.get(policy_id)
    
    def set_policy(self, policy_id, data):
        self.policies[policy_id] = data
    
    def get_session(self, profile_id):
        return self.sessions.get(profile_id)
    
    def set_session(self, profile_id, data):
        self.sessions[profile_id] = data
    
    def clear_session(self, profile_id):
        if profile_id in self.sessions:
            del self.sessions[profile_id]
