from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    roc_curve,
    auc,
    f1_score,
    accuracy_score
)
import json

class TaggingReport:

    def __init__(self, y_test, y_pred, y_scores, classes, pos_label_index=None):
        # check number of classes
        # if binary problem calculate roc
        if len(classes) == 2:
            self.average = "binary"
            fpr, tpr, _ = roc_curve(y_test, y_scores, pos_label=pos_label_index)
            self.true_positive_rate = tpr.tolist()
            self.false_positive_rate = fpr.tolist()
            self.area_under_curve = auc(fpr, tpr)
        else:
            self.average = "micro"
            self.area_under_curve = 0.0
            self.true_positive_rate = []
            self.false_positive_rate = []

        self.f1_score = f1_score(y_test, y_pred, average=self.average, pos_label=pos_label_index)
        self.confusion = confusion_matrix(y_test, y_pred, labels=classes)
        self.precision = precision_score(y_test, y_pred, average=self.average, pos_label=pos_label_index)
        self.recall = recall_score(y_test, y_pred, average=self.average, pos_label=pos_label_index)
        self.accuracy = accuracy_score(y_test, y_pred)
        self.training_loss = None
        self.val_loss = None
        self.classes = classes


    def to_dict(self):
        return {
            "f1_score": round(self.f1_score, 5),
            "precision": round(self.precision, 5),
            "recall": round(self.recall, 5),
            "confusion_matrix": self.confusion.tolist(),
            "area_under_curve": round(self.area_under_curve, 5),
            "true_positive_rate": self.true_positive_rate,
            "false_positive_rate": self.false_positive_rate,
            "classes": self.classes,
            "accuracy": round(self.accuracy, 5),
            "training_loss": round(self.training_loss.astype(float), 5),
            "val_loss": round(self.val_loss.astype(float), 5),
        }
