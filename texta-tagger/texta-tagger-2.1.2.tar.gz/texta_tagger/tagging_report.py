from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    roc_curve,
    auc,
    f1_score,
    classification_report
)
from itertools import product
import matplotlib
import math
import numpy as np
import json
from sklearn.preprocessing import LabelBinarizer
from itertools import chain


class TaggingReport:

    def __init__(self, y_test, y_pred, y_scores, num_features, num_examples, classes, pos_label= None):
        # check number of classes
        # if binary problem calculate roc
        if len(classes) == 2:
            self.average = "binary"
            fpr, tpr, _ = roc_curve(y_test, y_scores, pos_label=pos_label)
            self.true_positive_rate = tpr.tolist()
            self.false_positive_rate = fpr.tolist()
            self.area_under_curve = auc(fpr, tpr)
        else:
            self.average = "micro"
            self.area_under_curve = 0.0
            self.true_positive_rate = []
            self.false_positive_rate = []

        self.report = classification_report(
            y_test,
            y_pred,
            labels = classes,
            output_dict = True
        )

        self.report_str = str(
            classification_report(
                y_test,
                y_pred,
                labels = classes
            )
        )

        self.precision = precision_score(y_test, y_pred, pos_label=pos_label, average=self.average)
        self.f1_score = f1_score(y_test, y_pred, pos_label=pos_label, average=self.average)
        self.confusion = confusion_matrix(y_test, y_pred, labels=classes)

        self.recall = recall_score(y_test, y_pred, pos_label=pos_label, average=self.average)
        self.num_features = num_features
        self.num_examples = num_examples
        self.classes = classes
        self.pos_label = pos_label

    def to_dict(self):
        return {
            "f1_score": round(self.f1_score, 5),
            "precision": round(self.precision, 5),
            "recall": round(self.recall, 5),
            "num_features": self.num_features,
            "num_examples": self.num_examples,
            "confusion_matrix": self.confusion.tolist(),
            "area_under_curve": round(self.area_under_curve, 5),
            "true_positive_rate": self.true_positive_rate,
            "false_positive_rate": self.false_positive_rate,
            "classes": self.classes,
            "pos_label": self.pos_label,
            "report": self.report
        }


    def confusion_plot(self, render_plot: bool = False):
        """
        Generates confusion matrix plot.
        """
        classes: self.classes

        # For non-GUI rendering
        if render_plot == False:
            matplotlib.use('agg')
        import matplotlib.pyplot as plt
        
        cm = np.asarray(self.confusion.tolist(), dtype='int64')
        # Scale the size of the figure depending on the number of labels
        cm_size_multiplier = 1 + math.ceil(len(self.classes)/5)
        plt.figure(figsize=(2*cm_size_multiplier, 2*cm_size_multiplier))

        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix', size=12)
        tick_marks = np.arange(len(self.classes))

        # Scale xticks rotation based on label lengths
        longest_label_len = len(max(self.classes, key=len))
        rot = 45 if (longest_label_len <= 10  or len(self.classes) == 2) else 90

        plt.xticks(tick_marks, self.classes, rotation=rot, size=10)
        plt.yticks(tick_marks, self.classes, size=10)
        fmt = 'd'
        thresh = cm.max() / 1.5 if cm.any() else 0
        for i, j in product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fmt),
                        horizontalalignment='center',
                        color='white' if cm[i, j] > thresh else 'black')
        
        plt.ylabel('True classes', size=11)
        plt.xlabel('Predicted classes', size=11)
        plt.tight_layout()
        return plt