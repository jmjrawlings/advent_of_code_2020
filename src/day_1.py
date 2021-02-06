from .prelude import *

log = setup_logger(__file__)

input = """
1801
1324
1924
1848
1735
1721
1948
1667
1832
1773
1972
1777
1866
1850
1786
1617
1806
1923
789
1645
1530
1989
1720
1681
1807
1716
1935
1944
1878
1859
1602
1154
1824
1993
1952
1849
1695
523
1845
1879
1744
1374
1567
1725
1986
2006
1739
1751
1709
1800
2008
1715
1728
1677
1388
1815
1750
1827
1737
1819
1916
1909
1726
1753
1899
1981
1558
1852
1762
551
1881
1891
1957
1976
1383
1847
1968
1736
1828
1851
1975
1794
1785
1837
1979
1798
1789
1534
1877
1724
1843
1812
1743
1951
1900
1887
1766
1991
1839
1700
1858
1864
2004
1870
1985
1919
1466
1754
1964
946
1907
1942
1911
321
1930
1854
1644
1757
1719
1741
1853
1706
1659
1945
1821
1950
1761
1838
1770
1927
1447
1803
2000
2010
1765
1691
1742
1936
1929
1902
1539
1816
1553
1982
1813
1896
1772
267
1829
1912
1787
1782
1763
1461
1883
1894
2005
1758
1717
1749
1733
1775
1767
1705
1959
1903
1880
2003
1544
1732
1833
1926
1980
1946
1978
1710
1831
1906
1922
1861
1694
1875
307
1920
1934
1966
1804
1799
1548
1871
1769
1997
1639
1830
917
1797
1672
1921
1965
1662
"""


@attr.s(repr=False)
class Data:
    nums: List[int] = attr.ib()
    target: int = attr.ib(default=2020)

    @property
    def count(self):
        return len(self.nums)

    def __repr__(self) -> str:
        return f"<{self.count} nums, target {self.target}>"


class Day1(Day[Data]):
    num = 1
    title = "Report Repair"
    input = input

    @property
    def data(self):
        return Data([int(x) for x in self.lines])


class Part1(Part[Data]):

    blurb = r"""
    After saving Christmas five years in a row, you've decided to take a vacation at a nice resort on a tropical island. Surely, Christmas will go on without you.

    The tropical island has its own currency and is entirely cash-only. The gold coins used there have a little picture of a starfish; the locals just call them stars. None of the currency exchanges seem to have heard of them, but somehow, you'll need to find fifty of these coins by the time you arrive so you can pay the deposit on your room.

    To save your vacation, you need to get all fifty stars by December 25th.

    Collect stars by solving puzzles. Two puzzles will be made available on each day in the Advent calendar; the second puzzle is unlocked when you complete the first. Each puzzle grants one star. Good luck!

    Before you leave, the Elves in accounting just need you to fix your expense report (your puzzle input); apparently, something isn't quite adding up.

    Specifically, they need you to find the two entries that sum to 2020 and then multiply those two numbers together.

    For example, suppose your expense report contained the following:

    1721
    979
    366
    299
    675
    1456

    In this list, the two entries that sum to 2020 are 1721 and 299. Multiplying them together produces 1721 * 299 = 514579, so the correct answer is 514579.

    Of course, your expense report is much larger. Find the two entries that sum to 2020; what do you get if you multiply them together?
    """

    model = f"""
    int: N;
    set of int: INDEX = 1 .. N;
            
    array[INDEX] of int: xs;
    int: target;

    var INDEX: i;
    var INDEX: j;
    
    var int: a;
    var int: b;

    constraint a = xs[i];
    constraint b = xs[j];
    constraint a + b = target;
    solve maximize a*b;
        
    """

    def formulate(self, data: Data):
        return self.model, dict(xs=data.nums, N=data.count, target=data.target)


class Part2(Part[Data]):

    blurb = r"""
    The Elves in accounting are thankful for your help; one of them even offers you a starfish coin they had left over from a past vacation. They offer you a second one if you can find three numbers in your expense report that meet the same criteria.

    Using the above example again, the three entries that sum to 2020 are 979, 366, and 675. Multiplying them together produces the answer, 241861950.

    In your expense report, what is the product of the three entries that sum to 2020?
    """

    model = f"""
    int: N;
    set of int: INDEX = 1 .. N;

    array[INDEX] of int: xs;
    int: target;

    var INDEX: i;
    var INDEX: j;
    var INDEX: k;

    var int: a;
    var int: b;
    var int: c;

    constraint a = xs[i];
    constraint b = xs[j];
    constraint c = xs[k];

    constraint a + b + c = target;
    solve maximize a*b*c;
    """

    def formulate(self, data):
        return self.model, dict(xs=data.nums, N=data.count, target=data.target)


register(Day1, Part1, Part2)