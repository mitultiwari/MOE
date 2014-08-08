# -*- coding: utf-8 -*-
"""Classes (Python) to compute the Bandit UCB1 arm allocation and choosing the arm to pull next.

See :class:`moe.bandit.ucb.UCB` for further details on this bandit.

"""
import math

import numpy

from moe.bandit.constant import UCB_SUBTYPE_1
from moe.bandit.ucb import UCB
from moe.bandit.utils import get_equal_arm_allocations

class UCB1(UCB):

    r"""Implementation of UCB1.

    A class to encapsulate the computation of bandit UCB1.
    See :func:`moe.bandit.ucb1.allocate_arms` for more details on how UCB1 allocates arms.

    See superclass :class:`moe.bandit.ucb.UCB` for further details.

    """

    def __init__(
            self,
            historical_info,
    ):
        """Construct an UCB1 object. See superclass :class:`moe.bandit.ucb.UCB` for details."""
        super(UCB1, self).__init__(
            historical_info=historical_info,
            subtype=UCB_SUBTYPE_1,
            )

    @staticmethod
    def get_unsampled_arm_names(arms_sampled):
        r"""Compute the set of unsampled arm names based on the given ``arms_sampled``..

        Throws an exception when arms_sampled is empty.

        :param arms_sampled: a dictionary of arm name to :class:`moe.bandit.data_containers.SampleArm`
        :type arms_sampled: dictionary of (str, SampleArm()) pairs
        :return: set of names of the unsampled arms
        :rtype: frozenset(str)
        :raise: ValueError when ``arms_sampled`` are empty.

        """
        if not arms_sampled:
            raise ValueError('arms_sampled is empty!')

        unsampled_arm_name_list = [name for name, sampled_arm in arms_sampled.iteritems() if sampled_arm.total == 0]
        return frozenset(unsampled_arm_name_list)

    @staticmethod
    def get_winning_arm_names(arms_sampled):
        r"""Compute the set of winning arm names based on the given ``arms_sampled``..

        Throws an exception when arms_sampled is empty.

        :param arms_sampled: a dictionary of arm name to :class:`moe.bandit.data_containers.SampleArm`
        :type arms_sampled: dictionary of (str, SampleArm()) pairs
        :return: set of names of the winning arms
        :rtype: frozenset(str)
        :raise: ValueError when ``arms_sampled`` are empty.

        """
        if not arms_sampled:
            raise ValueError('arms_sampled is empty!')

        # If there exists an unsampled arm, return the names of the unsampled arms
        unsampled_arm_names = UCB1.get_unsampled_arm_names(arms_sampled)
        if unsampled_arm_names:
            return unsampled_arm_names

        number_sampled = sum([sampled_arm.total for sampled_arm in arms_sampled.itervalues()])

        ucb_payoff_arm_name_list = []
        for arm_name, sampled_arm in arms_sampled.iteritems():
            avg_payoff = numpy.float64(sampled_arm.win - sampled_arm.loss) / sampled_arm.total if sampled_arm.total > 0 else 0
            # See :func:`moe.bandit.ucb1.allocate_arms` for the formula to compute UCB1 payoff
            ucb_payoff = avg_payoff + math.sqrt(2.0 * math.log(sampled_arm.total) / number_sampled)
            ucb_payoff_arm_name_list.append((ucb_payoff, arm_name))

        best_payoff, _ = max(ucb_payoff_arm_name_list)
        # Filter out arms that have average payoff less than the best payoff
        winning_arm_payoff_name_list = filter(lambda ucb_payoff_arm_name: ucb_payoff_arm_name[0] == best_payoff, ucb_payoff_arm_name_list)
        # Extract a list of winning arm names from a list of (UCB payoff, arm name) tuples.
        _, winning_arm_name_list = map(list, zip(*winning_arm_payoff_name_list))
        winning_arm_names = frozenset(winning_arm_name_list)
        return winning_arm_names

    def allocate_arms(self):
        r"""Compute the allocation to each arm given ``historical_info``, running bandit ``subtype`` endpoint.

        Computes the allocation to each arm based on the given subtype, and, historical info.

        Works with k-armed bandits (k >= 1).

        The Algorithm: http://moodle.technion.ac.il/pluginfile.php/192340/mod_resource/content/0/UCB.pdf

        If there is at least one unsampled arm, this method will choose to pull the unsampled arm
        (randomly choose an unsampled arm if there are multiple unsampled arms).
        If all arms are pulled at least once, this method will pull the optimal arm
        (best expected upper confidence bound payoff). The expected upper confidence bound payoff (expected UCB payoff) is computed as follows:

        .. math:: r_j = \mu + \sqrt{\frac{2 \ln n}{n_j}}

        where :math:`\mu` is the average payoff obtained from arm *j*, :math:`n_j` is the number of times arm *j* has been pulled,
        and *n* is overall the number of pulls so far (number sampled). Number sampled is calculated by summing up total from each arm sampled.

        In case of a tie, the method will split the allocation among the optimal arms.
        For example, if we have three arms (arm1, arm2, and arm3) with expected UCB payoff 0.5, 0.5, and 0.1 respectively.
        We split the allocation between the optimal arms arm1 and arm2.

        ``{arm1: 0.5, arm2: 0.5, arm3: 0.0}``

        :return: the dictionary of (arm, allocation) key-value pairs
        :rtype: a dictionary of (str, float64) pairs
        :raise: ValueError when ``sample_arms`` are empty.

        """
        arms_sampled = self._historical_info.arms_sampled
        if not arms_sampled:
            raise ValueError('sample_arms are empty!')

        return get_equal_arm_allocations(arms_sampled, self.get_winning_arm_names(arms_sampled))
