from collections import Counter
from itertools import chain
from typing import Hashable, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from matplotlib import colors, pyplot, ticker
from scipy.stats import entropy


class DiversityMetrics:
    """Metrics to evalutate the diversity level of recommended results.

    gini-coefficient/ECS/shannon-index/histogram are supported.
    """

    clist: List[Tuple] = [(0, "red"), (0.5, "orange"), (1, "yellow")]

    @staticmethod
    def _get_histogram(
        items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]],
    ) -> np.ndarray:
        first_element = next(iter(items))
        if isinstance(first_element, Sequence) and not isinstance(first_element, str):
            items = chain.from_iterable(items)
        flatten_items = list(items)
        return np.asarray(pd.Series(flatten_items).value_counts())

    @staticmethod
    def _gini_coefficient(
        categories_histogram: np.ndarray, histogram_sum: float, sort: bool = True
    ) -> float:
        if sort:
            categories_histogram = np.sort(categories_histogram)[::-1]
        count: int = categories_histogram.shape[0]
        area: float = categories_histogram @ np.arange(1, count + 1)
        area /= histogram_sum * count
        return 1 - 2 * area + 1 / count

    @staticmethod
    def _effective_catalog_size(
        categories_histogram: np.ndarray, histogram_sum: float, sort: bool = True
    ) -> float:
        pmf = categories_histogram / histogram_sum
        if sort:
            pmf.sort()
            pmf = pmf[::-1]
        ecs: float = pmf @ np.arange(1, categories_histogram.shape[0] + 1) * 2 - 1
        return ecs

    @classmethod
    def gini_coefficient(
        cls,
        items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]],
    ) -> float:
        histogram = cls._get_histogram(items)
        return cls._gini_coefficient(histogram, histogram.sum())

    @classmethod
    def effective_catalog_size(
        cls, items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]]
    ) -> float:
        histogram = cls._get_histogram(items)
        return cls._effective_catalog_size(histogram, histogram.sum())

    @classmethod
    def shannon_index(
        cls,
        items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]],
        base: Optional[float] = None,
    ) -> float:
        ent: float = entropy(cls._get_histogram(items), base=base)
        return ent

    @classmethod
    def shannon_index(
        cls,
        items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]],
        base: Optional[float] = None,
    ) -> float:
        ent: float = entropy(cls._get_histogram(items), base=base)
        return ent

    @classmethod
    def get_lorenz_curve(
        cls, items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]]
    ) -> None:
        categories_histogram = cls._get_histogram(items)[::-1]
        scaled_prefix_sum = categories_histogram.cumsum() / categories_histogram.sum()
        lorenz_curve: np.ndarray = np.insert(scaled_prefix_sum, 0, 0)
        _, ax = pyplot.subplots()
        x_axis: np.ndarray = np.linspace(0.0, 1.0, lorenz_curve.size)
        ax.fill_between(x_axis, 0, lorenz_curve, alpha=0.3)
        ax.fill_between(x_axis, lorenz_curve, x_axis, alpha=0.3)
        pyplot.plot(x_axis, lorenz_curve)
        pyplot.savefig("Lorenz.png")

    @classmethod
    def get_distribution(
        cls, items: Union[Iterable[Hashable], Iterable[Sequence[Hashable]]]
    ) -> pd.DataFrame:
        first_element = next(iter(items))
        if isinstance(first_element, Sequence) and not isinstance(first_element, str):
            items = chain(*items)
        counter: pd.DataFrame = pd.DataFrame(Counter(items).most_common())
        counter.columns = pd.Index(["category", "count"])
        counter["percentage"] = counter["count"] / counter["count"].sum()
        rvb = colors.LinearSegmentedColormap.from_list("", cls.clist)
        counter_len = len(counter)
        x = np.arange(counter_len).astype(float)
        y = counter["percentage"]
        pyplot.style.use("seaborn")
        pyplot.bar(x, y, color=rvb(x / counter_len))
        pyplot.gca().yaxis.set_major_formatter(ticker.PercentFormatter(1, 2))
        pyplot.savefig("distribution.png")
        return counter
