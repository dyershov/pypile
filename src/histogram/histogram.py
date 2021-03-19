class SparseHistogram:
    class LinearBins:
        def __init__(self, delta):
            self.__delta = delta

        def __call__(self, value):
            from math import floor
            return int(floor(value / self.__delta))

        def inv(self, index):
            return ((index + 0.0) * self.__delta,
                    (index + 0.5) * self.__delta,
                    (index + 1) * self.__delta)

    def __init__(self, bin_fn):
        if not hasattr(bin_fn, '__iter__'):
            bin_fn = [bin_fn]
        self.__dim = len(bin_fn)

        self.__bin_fn = [fn if callable(fn) else SparseHistogram.LinearBins(fn) for fn in bin_fn]
        self.__bin_count = dict()
        self.__bin_bounds = None
        self.__bin_volumes = None
        self.__count = 0

    def add(self, sample, count=1):
        if not hasattr(sample, '__iter__'):
            sample = [sample]
        bin_index = tuple([fn(v) for fn, v in zip(self.__bin_fn, sample)])
        self.__add(bin_index, count)

    def marginal(self, dim):
        bin_fn = self.__bin_fn[:dim] + self.__bin_fn[dim+1:]
        result = SparseHistogram(bin_fn)
        [result.__add(tuple(index[:dim] + index[dim+1:]), count) for index, count in self.__bin_count.items()]
        return result

    def conditional(self, dim, sample):
        bin_fn = self.__bin_fn[:dim] + self.__bin_fn[dim+1:]
        conditional_index = self.__bin_fn[dim](sample)
        result = SparseHistogram(bin_fn)
        [result.__add(tuple(index[:dim] + index[dim+1:]), count) for index, count in self.__bin_count.items() if index[dim] == conditional_index]
        return result

    def bin_centers(self):
        if self.__bin_bounds is None:
            self.__bin_bounds = [[fn.inv(i) for i, fn in zip(index, self.__bin_fn)] for index in self.__bin_count.keys()]
        return [(bnd[0][1] if self.__dim == 1 else [b[1] for b in bnd]) for bnd in self.__bin_bounds]

    def bin_bounds(self):
        if self.__bin_bounds is None:
            self.__bin_bounds = [[fn.inv(i) for i, fn in zip(index, self.__bin_fn)] for index in self.__bin_count.keys()]
        return [(bnd[0][0] if self.__dim == 1 else [b[0] for b in bnd], bnd[0][2] if self.__dim == 1 else [b[2] for b in bnd]) for bnd in self.__bin_bounds]

    def bin_volumes(self):
        if self.__bin_volumes is None:
            import numpy as np
            self.__bin_volumes = [(bnd[1] - bnd[0]) if self.__dim == 1 else np.prod([h - l for l,h in zip(*bnd)]) for bnd in self.bin_bounds()]
        return self.__bin_volumes

    def bin_count(self):
        return list(zip(self.bin_bounds(), self.__bin_count.values()))

    def count(self):
        return self.__count

    def mean(self):
        return [count / self.__count / vol for count, vol in zip(self.__bin_count.values(), self.bin_volumes())]

    def bars(self, variance, model=None):
        from math import floor
        from scipy.stats import poisson
        import numpy as np
        if not hasattr(variance, '__iter__'):
            variance = [variance]
        variance.sort()

        bars = list()

        nus = list(self.__bin_count.values()) if model is None else [model(center) * volume * self.__count for center, volume in zip(self.bin_centers(), self.bin_volumes())]
        os = [(int(floor(nu)),int(floor(nu))) for nu in nus]
        ps = [poisson.pmf(o[0], nu) for o, nu in zip(os, nus)]

        for var in variance:
            for index in range(len(nus)):
                nu = nus[index]
                o_l, o_r = os[index]
                p = ps[index]
                p_l = None
                p_r = None
                while p < var:
                    if p_l is None:
                        p_l = poisson.pmf(o_l - 1, nu) if o_l >= 1 else 0
                    if p_r is None:
                        p_r = poisson.pmf(o_r + 1, nu)
                    if p_l < p_r:
                        o_r += 1
                        p += p_r
                        p_r = None
                    else:
                        o_l -= 1
                        p += p_l
                        p_l = None
                os[index] = (o_l, o_r)
                ps[index] = p
            bars.append([(o[0] / self.__count / volume, o[1] / self.__count / volume) for o, volume in zip(os, self.bin_volumes())])

        return tuple(bars)

    def __add(self, bin_index, count):
        if bin_index in self.__bin_count.keys():
            self.__bin_count[bin_index] += count
        else:
            self.__bin_count[bin_index] = count
            self.__bin_bounds = None
            self.__bin_volumes = None
        self.__count += count
