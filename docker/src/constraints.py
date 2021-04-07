from sklearn.metrics import recall_score, f1_score, precision_score, accuracy_score


class Constraints:

    def __init__(self, y_true, y_pred):
        self.y_true = y_true
        self.y_pred = y_pred

    def calc_recall(self):
        return recall_score(y_true=self.y_true, y_pred=self.y_pred)

    def calc_precision(self):
        return precision_score(y_true=self.y_true, y_pred=self.y_pred)

    def calc_accuracy(self):
        return accuracy_score(y_true=self.y_true, y_pred=self.y_pred)

    def calc_f1(self):
        return f1_score(y_true=self.y_true, y_pred=self.y_pred)

    def calc_true_positive_rate(self):
        pass

    def calc_true_negative_rate(self):
        pass

    def calc_false_positive_rate(self):
        pass

    def calc_false_negative_rate(self):
        pass

    def calc_auc(self):
        pass

    def suggest_baseline(self):
        if not self.y_true or not self.y_pred:
            return None

        return {
            "recall": {
                "threshold": self.calc_recall(),
                "comparison_operator": "LessThanThreshold"
            },
            "precision": {
                "threshold": self.calc_precision(),
                "comparison_operator": "LessThanThreshold"
            },
            "accuracy": {
                "threshold": self.calc_accuracy(),
                "comparison_operator": "LessThanThreshold"
            },
            "f1": {
                "threshold": self.calc_f1(),
                "comparison_operator": "LessThanThreshold"
            },
        }
