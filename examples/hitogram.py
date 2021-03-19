def main():
    from math import ceil
    import numpy as np
    from scipy.stats import norm
    import interactive_plotter as ip
    from histogram import SparseHistogram as Histogram

    iFig = ip.InteractiveFigure()
    iAx = iFig.get_interactive_axes()
    iAx.axes.set_xlim([0.5,2.5])
    iAx.axes.set_ylim([0,2])
    iAx.axes.set_aspect('equal')
    bar998 = ip.BarCollection(color='r')
    bar950 = ip.BarCollection(color='y')
    bar650 = ip.BarCollection(color='g')
    iAx.add_foreground_artist(bar998)
    iAx.add_foreground_artist(bar950)
    iAx.add_foreground_artist(bar650)
    mean_scatter = iAx.scatter(s=15, color='k')


    mean = 1.5
    sigma = 0.225
    batch_size = 1/25
    hist = Histogram(0.025)

    model = norm(loc=mean, scale=sigma)

    iFig.render(pause=2.01)
    i = 1
    while True:
        [hist.add(model.rvs()) for _ in range(int(ceil(batch_size * i ** 2)))]

        bars = hist.bars([0.68, 0.95, 0.99], model.pdf)
        bar650.plot(hist.bin_bounds(), bars[0])
        bar950.plot(hist.bin_bounds(), bars[1])
        bar998.plot(hist.bin_bounds(), bars[2])
        mean_scatter.plot(hist.bin_centers(), hist.mean())

        iFig.render(pause=0.01)
        iFig.savefig('histogram.png', index=i)
        i += 1
        if i > 600:
            break

if __name__ == '__main__':
    main()
