from scipy.optimize import linprog


class TransportationAlgorithm:
    """ Class to run the Transportation Algorithm"""
    def __init__(self, production, sales, ranking, index_prod='Index_Production', index_sales='Index_Sales'):
        """ Initialize the class
        :param production: Production DataFrame
        :param sales: Sales DataFrame
        :param ranking: Ranking Matrix DataFrame
        """
        self.prod = production.sort_values(index_prod)
        self.sales = sales.sort_values(index_sales)
        self.ranking = ranking.sort_values([index_sales] + [index_prod])

    @staticmethod
    def _build_a_matrix(m, n):
        """ Build the A matrix that solves the problem Ax=b
        :param m: Dimensions in the production side
        :param n: Dimensions in the sales side
        :return: A matrix to solve the Ax=b problem
        """
        a_first = []
        for ai in range(m):
            ij = (ai - 1) * n + (n - 1)
            col = [0] * m * n
            for aj in range(ij + 1, (ij + n) + 1):
                col[aj] = 1
            a_first += [col]
        a_second = []
        for ai in range(n):
            col = [0] * m * n
            for aj in range(m):
                h = n * (aj - 1) + (m + 1) + (ai - m - 1)
                col[h] = 1
            a_second += [col]
        a_matrix = a_first + a_second
        return a_matrix

    def solve_lp(self, rank_col='RankValue', col_name='Tonnage', max_iter=20000, tolerance=1e-12, display=True):
        """ Solving the Linear Problem Ax = b using the Simplex and the Interior-Point methods
        :param rank_col: Name of the column gathering the Ranking Values
        :param col_name: Name of the column where the variable to split is contained in sales and production
        :param max_iter: Maximum number of iterations before the algorithm stops
        :param tolerance: Tolerance in which the iteration finishes
        :param display: Indicates whether the solution of the problem should be displayed or not
        :return: Result of the allocation in a DataFrame
        """
        # define problem variables
        m = self.sales.shape[0]
        n = self.prod.shape[0]

        # multiply by -1 to convert the problem to a minimisation problem
        c = (self.ranking[rank_col] * -1).reset_index(drop=True)
        sales = self.sales[col_name].reset_index(drop=True)
        prod = self.prod[col_name].reset_index(drop=True)

        # Building the A matrix
        a_matrix = self._build_a_matrix(m, n)

        # right-hand side of equation
        b = sales.append(prod).reset_index(drop=True)
        # Solve the linear Problem as equality
        options = {"disp": display, "maxiter": max_iter, 'tol': tolerance}

        # Run the Simplex method
        method = 'Interior-Point without constraints'
        res = linprog(c, A_eq=a_matrix, b_eq=b, options=options, method='interior-point')
        res_success = res.success

        # Run the Interior-Point method
        if res_success is False:
            method = 'Interior-Point without constraints'
            res = linprog(c, A_eq=a_matrix, b_eq=b, options=options, method='revised simplex')
            res_success = res.success

        # Run the interior-point method with constraints
        if res_success is False:
            method = 'interior-point with constraints'
            a_eq = a_matrix[1:m] + a_matrix[m + 1:(m + n)]
            a_ub = [a_matrix[0]] + [a_matrix[m]]
            b_eq = sales[1:m].append(prod[1:n])
            max_value = max(prod[0], sales[0])
            b_ub = [max_value] + [max_value]
            res = linprog(c, A_eq=a_eq, b_eq=b_eq, A_ub=a_ub, b_ub=b_ub,
                          options=options, method='interior-point')
            res_success = res.success

        # Run the Revised Simplex method with constraints
        if res_success is False:
            method = 'Revised simplex with constraints'
            a_eq = a_matrix[1:m] + a_matrix[m + 1:(m + n)]
            a_ub = [a_matrix[0]] + [a_matrix[m]]
            b_eq = sales[1:m].append(prod[1:n])
            max_value = max(prod[0], sales[0])
            b_ub = [max_value] + [max_value]
            res = linprog(c, A_eq=a_eq, b_eq=b_eq, A_ub=a_ub, b_ub=b_ub,
                          options=options, method='revised simplex')
            res_success = res.success

        result = self.ranking
        result[col_name] = res.x
        if res_success is False:
            print('Success: ', res_success, ' Message: ', "The algorithm couldn't find a feasible solution")
        else:
            print('Success: ', res_success, ' Message: ', res.message + " Method employed: " + method)
        result = result[result[col_name] > 0]

        return result, res_success, method
