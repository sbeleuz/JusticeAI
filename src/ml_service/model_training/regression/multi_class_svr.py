from sklearn.svm import SVR
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import explained_variance_score
from util.file import Load, Save
from util.log import Log


class MultiClassSVR:

    def __init__(self, data_set=None):
        """
        Constructor
        :param data_set: [{
            name: 'AZ-XXXXXXX.txt',
            demands_vector: [...],
            facts_vector: [...],
            outcomes_vector: [...]
        },
        {
            ...
        }]
        """
        self.data_set = data_set
        self.model = None

    def get_weights(self):
        """
        The weight associated with each input fact.
        Useful in seeing which facts the classifier
        values more than others
        :return: None
        """
        if self.model is not None:
            return self.model.coef_[0]
        Log.write('Please train or load the regression model first')
        return None

    def __test(self, x_test, y_test):
        """

        :param x_test:
        :param y_test:
        :return: None
        """
        Log.write("Testing Classifier")
        y_predict = self.model.predict(x_test)
        r_Score = r2_score(y_test, y_predict)
        explained_variance = explained_variance_score(y_test, y_predict)
        Log.write('R2: {}'.format(r_Score))
        Log.write('Explained Variance: {}'.format(explained_variance))

    def train(self):
        """
        Train a classifier using Linear SVC
        1) reshape date in a format that sklearn understands
        2) split training data
        3) train (fit)
        4) test model
        :return: None
        """
        x_total, y_total = self.reshape_dataset() # 1

        x_train, x_test, y_train, y_test = train_test_split(
            x_total, y_total, test_size=0.20, random_state=42) # 2

        Log.write("Sample size: {}".format(len(x_total)))
        Log.write("Train size: {}".format(len(x_train)))
        Log.write("Test size: {}".format(len(x_test)))
        Log.write("Training Regression Using Multi Class SVR")

        clf = MultiOutputRegressor(SVR(kernel='linear')) # 3
        clf.fit(x_train, y_train)
        self.model = clf
        self.__test(x_test, y_test) # 4

    def save(self):
        """
        :return: None
        """
        save = Save()
        save.save_binary("multi_class_svr_model.bin", self.model)

    def predict(self, data):
        """
        Predicts an outcome given facts
        :param data: numpy([1, 0, 0, ...])
        :return: np.array([...])
        """
        return self.model.predict([data])

    def load(self):
        """
        Returns a model of the classifier
        :return: OneVsRestClassifier(SVC())
        """
        self.model = Load.load_binary("multi_class_svr_model.bin")

    def reshape_dataset(self):
        """
        Restructure the data to accomodate the sklearn library
        1) Reshape the x data
            1.1) 2D numpy array: [
                    [precedent #1 facts],
                    [precedent #2 facts],
                    ...
                ]

        2) Reshape the y data
            2.1) The data looks as such: [1, 1, 1, 0, 1, 0, 0, 1...]

            2.2) We must create a new list with only the integer values greater
                 than 1. We assume that 1/0 represent booleans

            2.3) Example:        (transformation)
                [1, 1, 554, 0, 1] ------------------> [554]

            2.4) Create a 2D numpy array from the new list:[
                [precedent #1 outcomes],
                [precedent #2 outcomes],
                ...
            ]
        :return: x_total <#1.1>, y_total <#2.4>
        """

        # --------------------1--------------------------
        x_total = np.array(
            [np.reshape(precedent['facts_vector'], (len(precedent['facts_vector'],))) for precedent in self.data_set])

        # --------------------2--------------------------
        y_list = []
        for precedent in self.data_set:
            classified_precedent = []
            for i in range(len(precedent['outcomes_vector'])):
                if precedent['outcomes_vector'][i] > 1:
                    classified_precedent.append(precedent['outcomes_vector'][i])
                else:
                    classified_precedent.append(0)
            y_list.append(classified_precedent)
        y_total = np.array(y_list)
        return x_total, y_total
