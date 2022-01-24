import numpy as np
import pandas as pd
from collections import Counter

class DecisionTree:
    def __init__(self, X:pd.DataFrame, Y:pd.DataFrame, max_depth=5, depth = 0, min_samples_split=20, node_type = 'root', rule = None, criterion = 'gini', split = 'midpoint'):
        ''' constructor '''

        self.X = X
        self.Y = Y
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.left = None
        self.right = None
        self.counts = Counter(list(Y))
        self.depth = depth
        self.node_type = node_type
        self.features = list(self.X.columns)
        self.rule = rule
        self.target_length = len(Y)
        self.criterion = criterion
        self.predicted_value = list(sorted(self.counts.items(), key=lambda item: item[1]))[-1][0]
        self.best_feature = None
        self.best_value = None
        self.split = split


    def __get_moving_avg_list(self, X_sorted, feature):
        moving_avg_split_pos_list = list()
        feature_array = X_sorted[feature].unique()
        for index in range(len(feature_array)-1):
            mean = (feature_array[index] + feature_array[index+1]) / 2
            moving_avg_split_pos_list.append(mean)
        return moving_avg_split_pos_list



    def __gini_impurity(self, df_y):
        ''' Calculate Gini Index '''
        # Finding unique value of the features
        unique_values = np.unique(np.array(df_y))
        gini = 0
        # Loop over unique values
        for value in unique_values:
            # calculate probability
            p = len(df_y[df_y == value]) / len(df_y)
            gini += p ** 2
        return 1 - gini



    def __calculate_entropy(self, df_y):
        ''' Calculate Entropy '''
        # Finding unique value of the features
        unique_values = np.unique(df_y)
        entropy = 0
        # Loop over unique values
        for value in unique_values:
            # calculate probability
            p = len(df_y[df_y == value]) / len(df_y)
            entropy += -p * np.log2(p)
        return entropy



    def _find_best_split(self, split_points, X_sorted, feature, base_gain, max_gain, best_feature, best_value,criterion):
        ''' find the best split '''

        Y_arry =  np.array(X_sorted['Y'])
        # loop over all the split points
        for n in range(len(split_points)):
            splitValue = split_points[n]
            # Split the dataset into left and right datasets
            data_left = X_sorted.loc[X_sorted[feature] <= splitValue]['Y']
            data_right = X_sorted.loc[X_sorted[feature] > splitValue]['Y']
            # Check if the leaft and right child are not null
            if len(data_left) > 0 and len(data_right) > 0:
                if('entropy' == criterion):
                    leftGain = self.__calculate_entropy(data_left)
                    rightGain = self.__calculate_entropy(data_right)
                else:
                    leftGain = self.__gini_impurity(data_left)
                    rightGain = self.__gini_impurity(data_right)


                # Calculate the gain based on left and right weights
                gain = (len(data_left) / len(Y_arry)) * leftGain + (len(data_right) / len(Y_arry)) * rightGain


                # Calculating the Info gain
                infoGain = base_gain - gain

                # Checking if this is the best split so far
                if infoGain >= max_gain:
                    best_feature = feature
                    best_value = splitValue

                    # Setting the max gain to the current one
                    max_gain = infoGain
        return (best_feature, best_value, max_gain)



    def _find_best_feature(self, criterion, split):
        ''' find best feature, split value, right branch and left branch '''
        best_feature = None
        best_value = None
        df = self.X.copy()
        df['Y'] = self.Y.copy()
        max_gain = 0


        # Calculate the Parent Entropy/Gini based on criterion
        if ('entropy' == criterion):
            base_value = self.__calculate_entropy(df['Y'])
        else:
            base_value = self.__gini_impurity(df['Y'])

        # loop over features
        for feature in self.features:
            X_sorted = df.dropna().sort_values(feature)
            if("unique" == split):
                # Calculating unique features and finding the split points if the split is 'unique'
                split_points = np.unique(X_sorted[feature])
            else:
                # Calculating midpoints and finding the split points if the split is 'mid' (default)
                split_points = self.__get_moving_avg_list(X_sorted, feature)

            # Find the best split
            best_feature, best_value, max_gain = self._find_best_split(split_points, X_sorted, feature, base_value, max_gain, best_feature, best_value, criterion)
        # Spliting left branch and right branch based on the best feature and best value
        left_branch = df[df[best_feature] <= best_value].copy()
        right_branch = df[df[best_feature] > best_value].copy()
        return (best_feature, best_value, left_branch, right_branch)

    def _build_tree(self):
        ''' Recursive function to build the tree '''
        # Build tree until the stopping conditions are met
        if (self.depth <= self.max_depth) and (self.target_length >= self.min_samples_split):
            best_feature, best_value, left_branch, right_branch = self._find_best_feature(self.criterion, self.split)

            if best_feature is not None:
                self.best_feature = best_feature
                self.best_value = best_value
                # Creating the left and right nodes
                left = DecisionTree(
                    X= left_branch.drop(columns=left_branch.columns[-1]),
                    Y=left_branch['Y'],
                    depth=self.depth + 1,
                    max_depth=self.max_depth,
                    min_samples_split=self.min_samples_split,
                    node_type='left_node',
                    criterion=self.criterion,
                    split=self.split,
                    rule=f"{best_feature} <= {round(best_value, 3)}"
                )

                self.left = left
                self.left._build_tree()

                right = DecisionTree(
                    X=right_branch.drop(columns=right_branch.columns[-1]),
                    Y=right_branch['Y'],
                    depth=self.depth + 1,
                    max_depth=self.max_depth,
                    min_samples_split=self.min_samples_split,
                    node_type='right_node',
                    criterion=self.criterion,
                    split=self.split,
                    rule=f"{best_feature} > {round(best_value, 3)}"
                )

                self.right = right
                self.right._build_tree()



    def print_info(self, width=4):
        """
        Method to print the infromation about the tree
        """
        # Defining the number of spaces
        const = int(self.depth * width ** 1.5)
        spaces = "-" * const

        if self.node_type == 'root':
            print("Root")
        else:
            print(f"|{spaces} Split rule: {self.rule}")

        if ('entropy' == self.criterion):
            print(f"{' ' * const}   | Entropy of the node: {(self.__calculate_entropy(self.Y))}")
        else:
            print(f"{' ' * const}   | GINI impurity of the node: {(self._gini_impurity(self.Y))}")
        print(f"{' ' * const}   | Class distribution in the node: {dict(self.counts)}")
        print(f"{' ' * const}   | Predicted class: {self.predicted_value}")

    def print_tree(self):
        """
        Traverse the whole tree from the current node to the bottom and print the values
        """
        self.print_info()

        if self.left is not None:
            self.left.print_tree()

        if self.right is not None:
            self.right.print_tree()

    def _predict(self, X):
        ''' function to predict new dataset '''
        predicted_list = []
        for index, value in X.iterrows():
            head = self
            while (head.depth <= head.max_depth) and (head.target_length >= head.min_samples_split):
                best_feature = head.best_feature
                best_value = head.best_value

                if X[best_feature][index] < best_value:
                    if self.left is not None:
                        head = head.left
                else:
                    if self.right is not None:
                        head = head.right

            predicted_list.append(head.predicted_value)
        return predicted_list

