class Scribe:
    def __init__(self):
        self.logs = []

    def record_round(self, round_number, alpha_argument, beta_argument, moderator_notes):
        log_entry = {
            "round_number": round_number,
            "alpha_argument": alpha_argument,
            "beta_argument": beta_argument,
            "moderator_notes": moderator_notes
        }
        self.logs.append(log_entry)

    def get_logs(self):
        return self.logs