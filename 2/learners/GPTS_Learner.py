import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C


class GPTS_Learner:
    def __init__(self, arms):
        self.n_arms = len(arms)
        self.arms = arms
        self.means = np.zeros(self.n_arms)
        self.sigmas = np.ones(self.n_arms) * 10
        self.pulled_arms = []
        self.collected_rewards = np.array([])
        alpha = 10.0
        kernel = C(1.0, (1e-3, 1e3)) * RBF(1.0, (1e-3, 1e3))
        self.gp = GaussianProcessRegressor(kernel=kernel, alpha=alpha**2,
                                           normalize_y=True, n_restarts_optimizer=9)

    def update_observations(self, arm_idx, reward):
        """
        Updates what the Gaussian Process has observed so far in two lists,
        collected_rewards and pulled arms
        """
        self.collected_rewards = np.append(self.collected_rewards,reward)
        self.pulled_arms.append(self.arms[arm_idx])

    def update_model(self):
        """
        Updates the Gaussian Process using the pulled arms and their rewards.
        """
        x = np.atleast_2d(self.pulled_arms).T
        y = self.collected_rewards
        self.gp.fit(x, y)
        self.means, self.sigmas = self.gp.predict(
            np.atleast_2d(self.arms).T, return_std=True)
        self.sigmas = np.maximum(self.sigmas, 1e-2)
        

    def update(self, pulled_arm, reward):
        """
        Call the two functions above
        """
        self.update_observations(pulled_arm, reward)
        self.update_model()

    def pull_arms(self):
        """
        Returns the predictions of the arms computing a 
        normal distribution for each of them using the currently means and sigmas.
        Note that it return one or more values as sample_values, depending on the
        length of means and sigmas
        """
        sampled_values = np.random.normal(self.means, self.sigmas)
        sampled_values = np.maximum(0 , sampled_values) # to avoid negative values
        return sampled_values