class Auditor:
    def summarize_debate(self, logs):
        summary = []
        for log in logs:
            summary.append(f"Round {log['round_number']}:\nAlpha: {log['alpha_argument']}\nBeta: {log['beta_argument']}\nModerator Notes: {log['moderator_notes']}\n")
        return "\n".join(summary)